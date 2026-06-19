import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

MONGO_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URL)
db = client.whatsapp_jarvis

# Collections
conversations = db.conversations
memories = db.memories
reminders = db.reminders
prompts = db.prompts
users = db.users
ai_chats = db.ai_chats

import bcrypt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


async def get_user(username: str):
    return await users.find_one({"username": username})

async def create_user(username: str, password: str, role: str = "user"):
    hashed = get_password_hash(password)
    await users.insert_one({
        "username": username,
        "password": hashed,
        "role": role,
        "created_at": datetime.now(timezone.utc)
    })

async def list_users():
    cursor = users.find({}, {"password": 0})
    return await cursor.to_list(length=100)

async def delete_user(username: str):
    await users.delete_one({"username": username})

# Seed Admin User if not exists
async def seed_admin():
    admin = await get_user("admin")
    if not admin:
        # Default password from user request
        await create_user("admin", "Hkoradiya.jarvis", role="admin")

async def get_db_prompt(name: str):
    doc = await prompts.find_one({"name": name})
    return doc.get("content") if doc else None

async def update_db_prompt(name: str, content: str):
    await prompts.update_one(
        {"name": name},
        {"$set": {"content": content, "updated_at": datetime.now()}},
        upsert=True
    )

from pymongo.errors import DuplicateKeyError

async def init_db_indexes():
    await conversations.create_index("message_id", unique=True, sparse=True)

async def save_message(user_id: str, role: str, content: str, thought: str = None, message_id: str = None):
    doc = {
        "user_id": user_id,
        "role": role,
        "content": content,
        "timestamp": datetime.now(timezone.utc)
    }
    if thought:
        doc["thought"] = thought
    if message_id:
        doc["message_id"] = message_id
    try:
        await conversations.insert_one(doc)
        return True
    except DuplicateKeyError:
        return False


async def get_recent_history(user_id: str, limit: int = 15):
    cursor = conversations.find({"user_id": user_id, "archived": {"$ne": True}}).sort("timestamp", -1).limit(limit)
    history = await cursor.to_list(length=limit)
    return history[::-1]

async def count_messages(user_id: str):
    return await conversations.count_documents({"user_id": user_id, "archived": {"$ne": True}})

async def delete_oldest_messages(user_id: str, count: int):
    # Soft delete: Find IDs of oldest active messages and mark them as archived
    cursor = conversations.find({"user_id": user_id, "archived": {"$ne": True}}).sort("timestamp", 1).limit(count)
    old_msgs = await cursor.to_list(length=count)
    ids = [m["_id"] for m in old_msgs]
    if ids:
        await conversations.update_many({"_id": {"$in": ids}}, {"$set": {"archived": True}})

async def get_all_memories():
    cursor = memories.find({}).sort("timestamp", -1)       
    return await cursor.to_list(length=100)

async def get_relevant_memories(user_id: str, query: str, limit: int = 5):
    import re
    cursor = memories.find({"user_id": user_id})
    all_items = await cursor.to_list(length=None)
    if not all_items:
        # Fallback to generic memories (for users without explicit user_id yet)
        cursor = memories.find({"user_id": {"$exists": False}})
        all_items = await cursor.to_list(length=None)
        if not all_items:
            # Fallback to any memory
            cursor = memories.find({})
            all_items = await cursor.to_list(length=100)
            
    if not all_items:
        return []
    
    query_words = set(re.findall(r'\w+', query.lower()))
    if not query_words:
        return all_items[:limit]
        
    scored_items = []
    for item in all_items:
        val = item.get("value", "")
        cat = item.get("category", "")
        item_words = set(re.findall(r'\w+', (val + " " + cat).lower()))
        score = len(query_words.intersection(item_words))
        scored_items.append((score, item))
        
    scored_items.sort(key=lambda x: x[0], reverse=True)
    
    # If no keyword overlap matches, fallback to returning the 3 most recent memories
    matches = [item for score, item in scored_items if score > 0]
    if not matches:
        return all_items[:3]
    return matches[:limit]

async def delete_memory(memory_id: str):
    from bson import ObjectId
    await memories.delete_one({"_id": ObjectId(memory_id)})

async def get_all_reminders():
    cursor = reminders.find({}).sort("datetime", 1)        
    return await cursor.to_list(length=100)

async def save_memory_task(user_id: str, category: str, value: str):
    await memories.insert_one({
        "user_id": user_id,
        "category": category,
        "value": value,
        "timestamp": datetime.now(timezone.utc)
    })

async def save_reminder_task(user_id: str, title: str, datetime_str: str, priority: str = "medium"):
    await reminders.insert_one({
        "user_id": user_id,
        "title": title,
        "datetime": datetime_str,
        "priority": priority,
        "status": "pending",
        "timestamp": datetime.now(timezone.utc)
    })

async def get_all_conversations():
    """Returns a list of unique user_ids and their last message time."""
    pipeline = [
        {"$sort": {"timestamp": -1}},
        {"$group": {
            "_id": "$user_id",
            "last_message_time": {"$first": "$timestamp"},
            "last_message_content": {"$first": "$content"},
            "message_count": {"$sum": 1}
        }},
        {"$sort": {"last_message_time": -1}}
    ]
    cursor = conversations.aggregate(pipeline)
    return await cursor.to_list(length=None)

async def get_conversation_history(user_id: str):
    """Returns the full message history for a user."""
    cursor = conversations.find({"user_id": user_id}).sort("timestamp", 1)
    return await cursor.to_list(length=None)

async def get_ai_chat_sessions():
    """Returns a summary of all AI chat sessions."""
    pipeline = [
        {"$sort": {"timestamp": 1}},
        {"$group": {
            "_id": "$session_id",
            "first_message": {"$first": "$content"},
            "last_message_time": {"$last": "$timestamp"}
        }},
        {"$sort": {"last_message_time": -1}}
    ]
    cursor = ai_chats.aggregate(pipeline)
    return await cursor.to_list(length=None)

async def get_ai_chat_history(session_id: str):
    """Returns all messages for a specific AI chat session."""
    cursor = ai_chats.find({"session_id": session_id}).sort("timestamp", 1)
    return await cursor.to_list(length=None)

async def add_ai_chat_message(session_id: str, role: str, content: str):
    """Adds a new message to an AI chat session."""
    await ai_chats.insert_one({
        "session_id": session_id,
        "role": role,
        "content": content,
        "timestamp": datetime.now(timezone.utc)
    })
