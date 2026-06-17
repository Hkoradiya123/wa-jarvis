import os
import json
import httpx
import re
from fastapi import FastAPI, Request, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from app.utils.llm import call_llm
from app.agents.router_agent import get_router_prompt
from app.agents.ai_agent import get_ai_prompt
from app.agents.memory_agent import get_memory_prompt
from app.agents.reminder_agent import get_reminder_prompt
from app.agents.planner_agent import get_planner_prompt
from app.agents.summarizer_agent import get_summarizer_prompt
from app.agents.base import get_global_rules
from app.database.mongodb import (
    save_message, get_recent_history, count_messages, delete_oldest_messages,
    get_all_memories, delete_memory, get_all_reminders
)
from app.utils.logger import get_logger, log_manager
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
logger = get_logger("main")

@app.middleware("http")
async def dashboard_security(request: Request, call_next):
    # Skip security for static files and webhook
    path = request.url.path
    if path.startswith("/api/") or path.startswith("/ws/"):
        password = os.getenv("DASHBOARD_PASSWORD")
        if password:
            req_pass = request.headers.get("X-Password") or request.query_params.get("password")
            if req_pass != password:
                return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
    return await call_next(request)

OPENWA_API_URL = os.getenv("OPENWA_API_URL", "http://localhost:2785")
OPENWA_API_KEY = os.getenv("OPENWA_API_KEY")
SESSION_ID = os.getenv("SESSION_ID", "default")
TRIGGER_WORD = os.getenv("TRIGGER_WORD", "//jarvis").lower()

async def send_whatsapp_message(to: str, body: str, thought: str = None):
    current_session = os.getenv("SESSION_ID", SESSION_ID)
    current_api_url = os.getenv("OPENWA_API_URL", OPENWA_API_URL)
    current_api_key = os.getenv("OPENWA_API_KEY", OPENWA_API_KEY)

    url = f"{current_api_url}/api/sessions/{current_session}/messages/send-text"
    headers = {"Authorization": f"Bearer {current_api_key}"}
    payload = {"chatId": to, "text": body}
    
    send_logger = get_logger("whatsapp_send")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code in [200, 201]:
                send_logger.info(f"Message sent to {to}")
                # Save bot response to history
                await save_message(to, "assistant", body, thought=thought)
            else:
                send_logger.error(f"Failed to send: {response.text}")
    except Exception as e:
        send_logger.error(f"Error sending: {e}")

async def process_message(payload: dict):
    if not payload: return
    
    body = payload.get("body", "").strip()
    sender = payload.get("from", "")
    is_self = payload.get("fromMe", False)
    quoted_msg = payload.get("quotedMsg") 

    # 1. Determine if we should respond
    should_respond = False
    clean_query = body

    # Check if message starts with trigger word
    if body.lower().startswith(TRIGGER_WORD):
        should_respond = True
        clean_query = body[len(TRIGGER_WORD):].strip()
    # Check if it's a reply to the bot's message
    elif quoted_msg and quoted_msg.get("fromMe"):
        should_respond = True
        logger.info(f"User replied to bot message in {sender}")

    # If it's a self-message (sent by the user/bot account)
    # we ONLY respond if it has the trigger word OR it's a reply
    # This prevents the bot from responding to its own automated replies.
    if not should_respond:
        return

    # One more safety: if the bot is replying to ITSELF in a loop
    # (e.g. if the bot's own reply somehow triggered 'should_respond')
    # we block it if it's fromMe but doesn't have the trigger and isn't a reply to a NON-bot message.
    # But our current 'should_respond' logic is already safe.

    if not clean_query:
        await send_whatsapp_message(sender, "Yes? How can I help you?")
        return

    # 2. Save user message to history
    await save_message(sender, "user", clean_query)
    
    await log_manager.broadcast({
        "type": "incoming_message",
        "sender": sender,
        "content": clean_query
    })

    # --- Auto Compaction Logic ---
    msg_count = await count_messages(sender)
    if msg_count > 15:
        logger.info(f"Compacting history for {sender} (Count: {msg_count})")
        old_history = await get_recent_history(sender, limit=10)
        history_text = "\n".join([f"{m['role']}: {m['content']}" for m in old_history])
        
        summary_prompt = await get_summarizer_prompt()
        summary = await call_llm([
            {"role": "system", "content": summary_prompt},
            {"role": "user", "content": f"Summarize this:\n{history_text}"}
        ], max_tokens=250)
        
        await delete_oldest_messages(sender, 10)
        await save_message(sender, "system", f"Context Summary: {summary}")
        logger.info("Compaction complete.")
    # -----------------------------

    try:
        # 3. Get history for context
        history = await get_recent_history(sender)
        context_messages = [{"role": h["role"], "content": h["content"]} for h in history]

        # 4. Routing
        router_prompt = await get_router_prompt() + "\nReturn only valid JSON."
        router_raw = await call_llm([{"role": "system", "content": router_prompt}, {"role": "user", "content": clean_query}], max_tokens=200)
        
        # Clean JSON
        router_clean = router_raw.strip()
        if "```" in router_clean:
            router_clean = router_clean.split("```")[1].replace("json", "").strip()
        
        try:
            agent_type = json.loads(router_clean).get("agent", "AI_AGENT")
        except:
            agent_type = "AI_AGENT"

        await log_manager.broadcast({
            "type": "routing",
            "agent": agent_type
        })

        # 5. Specialized Agent Logic
        system_prompt = get_global_rules() + "\n"
        if agent_type == "AI_AGENT": system_prompt += await get_ai_prompt()
        elif agent_type == "MEMORY_AGENT": system_prompt += await get_memory_prompt()
        elif agent_type == "REMINDER_AGENT": system_prompt += await get_reminder_prompt()
        elif agent_type == "PLANNER_AGENT": system_prompt += await get_planner_prompt()
        else: system_prompt += await get_ai_prompt()

        # Combine System Prompt + History
        final_messages = [{"role": "system", "content": system_prompt}] + context_messages
        
        response_text = await call_llm(final_messages)
        
        # 6. Extract Thought and Answer
        thought_match = re.search(r'<thought>(.*?)</thought>', response_text, re.DOTALL)
        answer_match = re.search(r'<answer>(.*?)</answer>', response_text, re.DOTALL)
        
        thought = thought_match.group(1).strip() if thought_match else ""
        
        if answer_match:
            clean_answer = answer_match.group(1).strip()
        else:
            # Fallback: remove thought tags if present to keep WhatsApp clean
            clean_answer = re.sub(r'<thought>.*?</thought>', '', response_text, flags=re.DOTALL).strip()
        
        if thought:
            await log_manager.broadcast({
                "type": "thought",
                "content": thought
            })

        await log_manager.broadcast({
            "type": "outgoing_message",
            "content": clean_answer
        })
        await send_whatsapp_message(sender, clean_answer, thought=thought)

    except Exception as e:
        logger.error(f"Error processing: {e}", exc_info=True)
        await log_manager.broadcast({
            "type": "error",
            "message": str(e)
        })

@app.websocket("/ws/logs")
async def websocket_endpoint(websocket: WebSocket):
    await log_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        log_manager.disconnect(websocket)
    except Exception:
        log_manager.disconnect(websocket)

@app.post("/webhook")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    event = data.get("event")
    payload = data.get("data") or data.get("payload")
    if event in ["message", "message.received", "message.sent"] and payload:
        background_tasks.add_task(process_message, payload)
    return {"status": "success"}

@app.get("/api/memories")
async def list_memories():
    items = await get_all_memories()
    # Convert ObjectId to str for JSON serialization       
    for item in items:
        item["_id"] = str(item["_id"])  
    return items

@app.delete("/api/memories/{memory_id}")
async def remove_memory(memory_id: str):
    await delete_memory(memory_id)
    return {"status": "deleted"}

@app.get("/api/reminders")
async def list_reminders():
    items = await get_all_reminders()
    for item in items:
        item["_id"] = str(item["_id"])
    return items

# Serve frontend static files
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")

# Catch-all for SPA routing
@app.exception_handler(404)
async def spa_fallback(request: Request, exc):
    # Only fallback for non-API requests
    if not request.url.path.startswith("/api"):
        return FileResponse("frontend/dist/index.html")
    return {"detail": "Not Found"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7860))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
