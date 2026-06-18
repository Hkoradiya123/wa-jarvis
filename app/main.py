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
from app.agents.search_agent import get_search_prompt
from app.utils.mcp_tools import search_and_summarize
from app.agents.base import get_global_rules
from app.database.mongodb import (
    save_message, get_recent_history, count_messages, delete_oldest_messages,
    get_all_memories, delete_memory, get_all_reminders, update_db_prompt,
    db as mongodb_db, get_user, verify_password, seed_admin, list_users, create_user, delete_user,
    get_all_conversations, get_conversation_history
)
from pydantic import BaseModel, Field
from app.utils.logger import get_logger, log_manager
from dotenv import load_dotenv

load_dotenv(override=True)

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await seed_admin()
    # Try to discover active session automatically
    global SESSION_ID
    try:
        base_url = OPENWA_API_URL.strip().rstrip("/")
        if not base_url.startswith("http"):
            base_url = f"https://{base_url}"
            
        url = f"{base_url}/api/sessions"
        headers = {"Authorization": f"Bearer {OPENWA_API_KEY}"}
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url, headers=headers, timeout=10.0)
            if response.status_code == 200:
                sessions = response.json()
                for s in sessions:
                    if s.get("status") in ["CONNECTED", "ready"]:
                        SESSION_ID = s.get("id")
                        os.environ["SESSION_ID"] = SESSION_ID
                        logger.info(f"✅ Auto-discovered active session: {SESSION_ID}")
                        break
    except Exception as e:
        logger.warning(f"⚠️ Could not auto-discover session: {e}")

logger = get_logger("main")

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"

@app.middleware("http")
async def dashboard_security(request: Request, call_next):
    # Skip security for static files and webhook
    path = request.url.path
    if path.startswith("/api/") or path.startswith("/ws/"):
        username = request.headers.get("X-Username") or request.query_params.get("username")
        password = request.headers.get("X-Password") or request.query_params.get("password")
        
        if not username or not password:
            return JSONResponse(status_code=401, content={"detail": "Missing credentials"})
        
        user = await get_user(username)
        if not user or not verify_password(password, user["password"]):
            return JSONResponse(status_code=401, content={"detail": "Invalid credentials"})
            
        # Add user info to request state if needed
        request.state.user = user
            
    return await call_next(request)

# ... API endpoints ...

@app.get("/api/users")
async def get_users(request: Request):
    if request.state.user.get("role") != "admin":
        return JSONResponse(status_code=403, content={"detail": "Admin access required"})
    users = await list_users()
    for user in users:
        user["_id"] = str(user["_id"])
        if "created_at" in user:
            user["created_at"] = user["created_at"].isoformat()
    return users

@app.post("/api/users")
async def add_user(request: Request, user: UserCreate):
    if request.state.user.get("role") != "admin":
        return JSONResponse(status_code=403, content={"detail": "Admin access required"})
    
    existing = await get_user(user.username)
    if existing:
        return JSONResponse(status_code=400, content={"detail": "User already exists"})
        
    await create_user(user.username, user.password, user.role)
    return {"status": "success"}

@app.delete("/api/users/{username}")
async def remove_user(request: Request, username: str):
    if request.state.user.get("role") != "admin":
        return JSONResponse(status_code=403, content={"detail": "Admin access required"})
    
    if username == "admin":
        return JSONResponse(status_code=400, content={"detail": "Cannot delete super admin"})
        
    await delete_user(username)
    return {"status": "success"}

class PromptUpdate(BaseModel):
    content: str

@app.get("/api/prompts")
async def list_prompts():
    all_prompts = {
        "AI_AGENT": await get_ai_prompt(),
        "MEMORY_AGENT": await get_memory_prompt(),
        "REMINDER_AGENT": await get_reminder_prompt(),
        "PLANNER_AGENT": await get_planner_prompt(),
        "SUMMARIZER_AGENT": await get_summarizer_prompt(),
        "ROUTER_AGENT": await get_router_prompt(),
        "SEARCH_AGENT": await get_search_prompt()
    }
    return all_prompts

@app.post("/api/prompts/{name}")
async def set_prompt(name: str, update: PromptUpdate):
    await update_db_prompt(name, update.content)
    return {"status": "success"}

@app.get("/api/system/status")
async def get_system_status():
    nvidia_key = os.getenv("NVIDIA_API_KEY")
    if nvidia_key and len(nvidia_key) > 10:
        masked_nvidia = f"{nvidia_key[:6]}****{nvidia_key[-4:]}"
        logger.info("NVIDIA API key is configured.")
    else:
        masked_nvidia = "missing"
        logger.warning("NVIDIA API key is missing from environment variables.")
    
    status = {
        "mongodb": "online",
        "nvidia_api": masked_nvidia,
        "openwa_gateway": "unknown"
    }
    # Check MongoDB
    try:
        await mongodb_db.command("ping")
    except Exception:
        status["mongodb"] = "offline"

    # Check gateway
    try:
        base_url = os.getenv("OPENWA_API_URL", "http://localhost:2785").strip().rstrip("/")
        if not base_url.startswith("http"):
            base_url = f"https://{base_url}"
            
        async with httpx.AsyncClient(follow_redirects=True) as client:
            res = await client.get(base_url, timeout=5.0)
            if res.status_code < 500:
                status["openwa_gateway"] = "online"
            else:
                status["openwa_gateway"] = f"error_{res.status_code}"
    except Exception as e:
        status["openwa_gateway"] = f"offline"
        logger.debug(f"Status check failed for {base_url}: {e}")
    
    return status


OPENWA_API_URL = os.getenv("OPENWA_API_URL", "http://localhost:2785")
OPENWA_API_KEY = os.getenv("OPENWA_API_KEY")
SESSION_ID = os.getenv("SESSION_ID", "default")
TRIGGER_WORD = os.getenv("TRIGGER_WORD", "//jarvis").lower()

async def send_whatsapp_message(to: str, body: str, thought: str = None):
    current_session = os.getenv("SESSION_ID", SESSION_ID)
    current_api_url = os.getenv("OPENWA_API_URL", OPENWA_API_URL)
    current_api_key = os.getenv("OPENWA_API_KEY", OPENWA_API_KEY)

    # Ensure protocol is present and clean up URL
    base_url = current_api_url.strip().rstrip("/")
    if not base_url.startswith("http"):
        base_url = f"https://{base_url}"
        
    url = f"{base_url}/api/sessions/{current_session}/messages/send-text"
    headers = {"Authorization": f"Bearer {current_api_key}"}
    payload = {"chatId": to, "text": body}
    
    send_logger = get_logger("whatsapp_send")
    send_logger.info(f"Sending message to {to} via {url}")
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code in [200, 201]:
                # Save bot response to history
                await save_message(to, "assistant", body, thought=thought)
            else:
                send_logger.error(f"Failed to send message to {to} (Status: {response.status_code})")
                send_logger.error(f"Response: {response.text}")
    except Exception as e:
        send_logger.error(f"Error sending message to {to}: {str(e)}", exc_info=True)

async def execute_agent_action(user_id: str, action_json: str):
    """
    Parses the JSON action from an agent and executes the corresponding DB task.
    Returns a friendly confirmation message.
    """
    try:
        data = json.loads(action_json)
        action = data.get("action")
        
        if action == "SAVE_MEMORY":
            from app.database.mongodb import save_memory_task
            await save_memory_task(user_id, data.get("category", "general"), data.get("value", ""))
            return f"✅ Memory saved: {data.get('value')}"
            
        elif action == "CREATE_REMINDER":
            from app.database.mongodb import save_reminder_task
            await save_reminder_task(user_id, data.get("title", ""), data.get("datetime", ""), data.get("priority", "medium"))
            return f"✅ Reminder set: {data.get('title')} for {data.get('datetime')}"
            
        elif action == "CREATE_PLAN":
            items = data.get("items", [])
            plan_text = f"📅 *YOUR {data.get('type', 'DAILY').upper()} PLAN*\n\n"
            plan_text += "\n".join([f"• {item}" for item in items])
            return plan_text
            
        # Add more actions as needed
        
        return action_json # Fallback to raw if not matched
    except:
        return action_json # Fallback if not JSON

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
        # Give router some context from history for better classification
        routing_messages = [{"role": "system", "content": router_prompt}] + context_messages[-3:] + [{"role": "user", "content": clean_query}]
        router_raw = await call_llm(routing_messages, max_tokens=200)
        
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
        elif agent_type == "SEARCH_AGENT":
            # --- SEARCH AGENT SPECIAL FLOW ---
            await log_manager.broadcast({"type": "thought", "content": "Performing internet search..."})
            search_data = await search_and_summarize(clean_query)
            search_prompt = await get_search_prompt()
            system_prompt = get_global_rules() + "\n" + search_prompt.format(query=clean_query, data=search_data)
            # Re-call LLM with search data
            final_messages = [{"role": "system", "content": system_prompt}] + context_messages
            response_text = await call_llm(final_messages)
            # ---------------------------------
        else: system_prompt += await get_ai_prompt()

        if agent_type != "SEARCH_AGENT":
            # Combine System Prompt + History
            final_messages = [{"role": "system", "content": system_prompt}] + context_messages
            response_text = await call_llm(final_messages)
        
        # 6. Extract Thought and Answer
        thought_match = re.search(r'<thought>(.*?)</thought>', response_text, re.DOTALL)
        answer_match = re.search(r'<answer>(.*?)</answer>', response_text, re.DOTALL)
        
        thought = thought_match.group(1).strip() if thought_match else ""
        
        if answer_match:
            clean_answer = answer_match.group(1).strip()
            # If it's a specialized agent, execute the action
            if agent_type in ["MEMORY_AGENT", "REMINDER_AGENT", "PLANNER_AGENT"]:
                clean_answer = await execute_agent_action(sender, clean_answer)
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
        logger.error("Error processing message", exc_info=True)
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


async def get_ai_response(user_id: str, query: str):
    """
    A stateless function to get a direct response from the AI logic.
    This reuses the core agent routing and execution flow without saving to the database.
    """
    # Use a generic history for stateless chat, or fetch a user-specific one if needed
    history = await get_recent_history(user_id, limit=5)
    context_messages = [{"role": h["role"], "content": h["content"]} for h in history]

    # 1. Routing
    router_prompt = await get_router_prompt() + "\nReturn only valid JSON."
    routing_messages = [{"role": "system", "content": router_prompt}] + context_messages[-3:] + [{"role": "user", "content": query}]
    router_raw = await call_llm(routing_messages, max_tokens=200)
    
    try:
        agent_type = json.loads(router_raw.strip().split("```")[1].replace("json", "").strip()).get("agent", "AI_AGENT")
    except:
        agent_type = "AI_AGENT"

    # 2. Specialized Agent Logic
    system_prompt = get_global_rules() + "\n"
    if agent_type == "AI_AGENT": system_prompt += await get_ai_prompt()
    # ... (add other agents as needed, similar to process_message)
    else: system_prompt += await get_ai_prompt()

    # 3. Get Response
    final_messages = [{"role": "system", "content": system_prompt}] + context_messages + [{"role": "user", "content": query}]
    response_text = await call_llm(final_messages)
    
    # 4. Extract Answer
    answer_match = re.search(r'<answer>(.*?)</answer>', response_text, re.DOTALL)
    if answer_match:
        return answer_match.group(1).strip()
    else:
        return re.sub(r'<thought>.*?</thought>', '', response_text, flags=re.DOTALL).strip()

class NewChatMessage(BaseModel):
    message: str
    session_id: str | None = None

@app.get("/api/ai_chat/sessions")
async def list_ai_chat_sessions():
    sessions = await get_ai_chat_sessions()
    for s in sessions:
        s["session_id"] = s.pop("_id")
    return sessions

@app.get("/api/ai_chat/sessions/{session_id}")
async def get_single_ai_chat_session(session_id: str):
    history = await get_ai_chat_history(session_id)
    for message in history:
        message["_id"] = str(message["_id"])
    return history

@app.post("/api/ai_chat")
async def handle_new_ai_chat(request: Request, chat_message: NewChatMessage):
    user = request.state.user
    user_id = user.get("username", "direct_chat_user") # For context in get_ai_response
    
    session_id = chat_message.session_id or str(uuid.uuid4())
    
    # Save user message
    await add_ai_chat_message(session_id, "user", chat_message.message)
    
    # Get AI response (using the existing stateless function for the logic)
    ai_response_content = await get_ai_response(user_id, chat_message.message)
    
    # Save AI message
    await add_ai_chat_message(session_id, "assistant", ai_response_content)
    
    return {"response": ai_response_content, "session_id": session_id}


@app.post("/webhook")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"detail": "Invalid JSON payload"})
        
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

@app.get("/api/conversations")
async def list_conversations():
    convos = await get_all_conversations()
    # Rename '_id' to 'user_id' for clarity on the frontend
    for convo in convos:
        convo["user_id"] = convo.pop("_id")
    return convos

@app.get("/api/conversations/{user_id}")
async def get_single_conversation(user_id: str):
    history = await get_conversation_history(user_id)
    for message in history:
        message["_id"] = str(message["_id"])
    return history


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
