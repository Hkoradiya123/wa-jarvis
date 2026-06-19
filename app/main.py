import os
import json
import httpx
import re
import uuid
from fastapi import FastAPI, Request, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from app.utils.llm import call_llm
from app.agents.router_agent import get_router_prompt, AgentType, RouterResponse
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
    get_all_conversations, get_conversation_history,
    get_ai_chat_sessions, get_ai_chat_history, add_ai_chat_message, init_db_indexes
)
from pydantic import BaseModel, Field
from app.utils.logger import get_logger, log_manager
from dotenv import load_dotenv

load_dotenv(override=True)

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await init_db_indexes()
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

ALLOWED_ACTIONS = {"SAVE_MEMORY", "CREATE_REMINDER", "CREATE_PLAN"}

def sanitize_input(value: str) -> bool:
    """Returns True if the input is safe, False if it contains sensitive PII."""
    if not value:
        return True
    sensitive_keywords = ["password", "secret", "api_key", "apikey", "token", "cvv", "otp", "credit card"]
    value_lower = value.lower()
    for kw in sensitive_keywords:
        if kw in value_lower:
            return False
    # Regex check for potential credit cards or API keys
    if re.search(r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b', value):
        return False
    return True

async def execute_agent_action(user_id: str, action_json: str):
    """
    Parses the JSON action from an agent and executes the corresponding DB task.
    Returns a friendly confirmation message.
    """
    try:
        data = json.loads(action_json)
        action = data.get("action")
        
        if action not in ALLOWED_ACTIONS:
            logger.warning(f"Rejected unauthorized action: {action} requested by user: {user_id}")
            return "⚠️ Rejected unsafe or invalid action."

        if action == "SAVE_MEMORY":
            val = data.get("value", "")
            if not sanitize_input(val) or not sanitize_input(data.get("category", "")):
                logger.warning(f"Blocked potential PII storage in SAVE_MEMORY for user: {user_id}")
                return "⚠️ Action blocked: Sensitive information (password/API key/card/OTP) cannot be stored."
            from app.database.mongodb import save_memory_task
            await save_memory_task(user_id, data.get("category", "general"), val)
            return f"✅ Memory saved: {val}"
            
        elif action == "CREATE_REMINDER":
            title = data.get("title", "")
            if not sanitize_input(title):
                logger.warning(f"Blocked potential PII storage in CREATE_REMINDER for user: {user_id}")
                return "⚠️ Action blocked: Sensitive information (password/API key/card/OTP) cannot be stored."
            from app.database.mongodb import save_reminder_task
            await save_reminder_task(user_id, title, data.get("datetime", ""), data.get("priority", "medium"))
            return f"✅ Reminder set: {title} for {data.get('datetime')}"
            
        elif action == "CREATE_PLAN":
            items = data.get("items", [])
            for item in items:
                if not sanitize_input(item):
                    return "⚠️ Action blocked: Sensitive information detected in plan items."
            plan_text = f"📅 *YOUR {data.get('type', 'DAILY').upper()} PLAN*\n\n"
            plan_text += "\n".join([f"• {item}" for item in items])
            return plan_text
            
        return "⚠️ Rejected unsafe or invalid action."
    except:
        return "⚠️ Failed to execute action: Invalid action format."


async def process_message(payload: dict):
    if not payload: return
    
    message_id = payload.get("id")
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
    saved = await save_message(sender, "user", clean_query, message_id=message_id)
    if not saved:
        logger.info(f"Duplicate message detected: {message_id}. Skipping processing.")
        return

    
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
            parsed_response = RouterResponse.model_validate_json(router_clean)
            agent_type = parsed_response.agent.value
        except Exception:
            agent_type = AgentType.AI_AGENT.value
            try:
                raw_json = json.loads(router_clean)
                agent_val = str(raw_json.get("agent", "")).strip().upper().replace(" ", "_").replace("-", "_")
                for at in AgentType:
                    if at.value == agent_val:
                        agent_type = at.value
                        break
            except Exception:
                raw_upper = router_raw.upper()
                for at in AgentType:
                    if at.value in raw_upper:
                        agent_type = at.value
                        break

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
            await log_manager.broadcast({"type": "thought", "content": "Formulating search query from context..."})
            
            # Formulate optimized search query from history context
            search_query_prompt = (
                "You are a search query optimizer. Given the conversation history and the user's latest message, "
                "generate a single, concise search query (in English) to find the relevant information. "
                "CRITICAL: Avoid using the word 'current' for prices, rates, or news as it confuses search engines "
                "with 'electric current'. Use 'today', 'latest', or 'live' instead (e.g., use 'gold price today Mumbai' "
                "instead of 'current gold price in Mumbai'). "
                "If the latest message is a confirmation (e.g. 'yes', 'do it', 'go ahead') to a search suggested by the assistant, "
                "formulate the query based on the topic the assistant offered to look up. "
                "Only return the search query itself, nothing else. No quotes, no markdown, no tags."
            )
            # Use all history up to the latest query
            routing_history = context_messages[:-1] if len(context_messages) > 0 else []
            query_gen_messages = [
                {"role": "system", "content": search_query_prompt}
            ] + routing_history + [{"role": "user", "content": clean_query}]
            
            optimized_query = await call_llm(query_gen_messages, max_tokens=50)
            optimized_query = optimized_query.strip().strip('"').strip("'").strip()
            
            if not optimized_query or optimized_query.lower() in ["yes", "no", "do it", "go ahead"]:
                optimized_query = clean_query
                
            await log_manager.broadcast({"type": "thought", "content": f"Performing internet search for: '{optimized_query}'..."})
            search_data = await search_and_summarize(optimized_query)
            search_prompt = await get_search_prompt()
            system_prompt = get_global_rules() + "\n" + search_prompt.format(query=optimized_query, data=search_data)
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


async def get_ai_response(user_id: str, query: str, session_id: str = None):
    """
    Retrieves history and gets a response from the AI logic, running the full agent routing and execution flow.
    """
    if session_id:
        from app.database.mongodb import get_ai_chat_history
        history = await get_ai_chat_history(session_id)
        # Convert DB history format
        # If the latest saved message in DB is the current user query, exclude it from history context
        context_messages = [{"role": h["role"], "content": h["content"]} for h in history]
        if context_messages and context_messages[-1]["role"] == "user" and context_messages[-1]["content"] == query:
            context_messages = context_messages[:-1]
    else:
        history = await get_recent_history(user_id, limit=5)
        context_messages = [{"role": h["role"], "content": h["content"]} for h in history]

    # 1. Routing
    router_prompt = await get_router_prompt() + "\nReturn only valid JSON."
    routing_messages = [{"role": "system", "content": router_prompt}] + context_messages[-3:] + [{"role": "user", "content": query}]
    router_raw = await call_llm(routing_messages, max_tokens=200)
    
    router_clean = router_raw.strip()
    if "```" in router_clean:
        router_clean = router_clean.split("```")[1].replace("json", "").strip()
        
    try:
        parsed_response = RouterResponse.model_validate_json(router_clean)
        agent_type = parsed_response.agent.value
    except Exception:
        agent_type = AgentType.AI_AGENT.value
        try:
            raw_json = json.loads(router_clean)
            agent_val = str(raw_json.get("agent", "")).strip().upper().replace(" ", "_").replace("-", "_")
            for at in AgentType:
                if at.value == agent_val:
                    agent_type = at.value
                    break
        except Exception:
            raw_upper = router_raw.upper()
            for at in AgentType:
                if at.value in raw_upper:
                    agent_type = at.value
                    break

    # 2. Specialized Agent Logic
    system_prompt = get_global_rules() + "\n"
    response_text = ""
    
    if agent_type == "AI_AGENT":
        system_prompt += await get_ai_prompt()
    elif agent_type == "MEMORY_AGENT":
        system_prompt += await get_memory_prompt()
    elif agent_type == "REMINDER_AGENT":
        system_prompt += await get_reminder_prompt()
    elif agent_type == "PLANNER_AGENT":
        system_prompt += await get_planner_prompt()
    elif agent_type == "SEARCH_AGENT":
        # --- SEARCH AGENT SPECIAL FLOW ---
        # Formulate optimized search query from history context
        search_query_prompt = (
            "You are a search query optimizer. Given the conversation history and the user's latest message, "
            "generate a single, concise search query (in English) to find the relevant information. "
            "CRITICAL: Avoid using the word 'current' for prices, rates, or news as it confuses search engines "
            "with 'electric current'. Use 'today', 'latest', or 'live' instead (e.g., use 'gold price today Mumbai' "
            "instead of 'current gold price in Mumbai'). "
            "If the latest message is a confirmation (e.g. 'yes', 'do it', 'go ahead') to a search suggested by the assistant, "
            "formulate the query based on the topic the assistant offered to look up. "
            "Only return the search query itself, nothing else. No quotes, no markdown, no tags."
        )
        query_gen_messages = [
            {"role": "system", "content": search_query_prompt}
        ] + context_messages + [{"role": "user", "content": query}]
        
        optimized_query = await call_llm(query_gen_messages, max_tokens=50)
        optimized_query = optimized_query.strip().strip('"').strip("'").strip()
        
        if not optimized_query or optimized_query.lower() in ["yes", "no", "do it", "go ahead"]:
            optimized_query = query
            
        search_data = await search_and_summarize(optimized_query)
        search_prompt = await get_search_prompt()
        system_prompt = get_global_rules() + "\n" + search_prompt.format(query=optimized_query, data=search_data)
        # Re-call LLM with search data
        final_messages = [{"role": "system", "content": system_prompt}] + context_messages + [{"role": "user", "content": query}]
        response_text = await call_llm(final_messages)
    else:
        system_prompt += await get_ai_prompt()

    if agent_type != "SEARCH_AGENT":
        final_messages = [{"role": "system", "content": system_prompt}] + context_messages + [{"role": "user", "content": query}]
        response_text = await call_llm(final_messages)
        
    # 3. Extract Thought and Answer
    answer_match = re.search(r'<thought>(.*?)</thought>', response_text, re.DOTALL)
    answer_text = re.search(r'<answer>(.*?)</answer>', response_text, re.DOTALL)
    
    if answer_text:
        clean_answer = answer_text.group(1).strip()
        # If it's a specialized agent, execute the action
        if agent_type in ["MEMORY_AGENT", "REMINDER_AGENT", "PLANNER_AGENT"]:
            clean_answer = await execute_agent_action(user_id, clean_answer)
    else:
        clean_answer = re.sub(r'<thought>.*?</thought>', '', response_text, flags=re.DOTALL).strip()
        
    return clean_answer

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
    
    # Get AI response with full routing and session context
    ai_response_content = await get_ai_response(user_id, chat_message.message, session_id=session_id)
    
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
