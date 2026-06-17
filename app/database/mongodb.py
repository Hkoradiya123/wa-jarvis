import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

MONGO_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URL)
db = client.whatsapp_jarvis

# Collections
conversations = db.conversations
memories = db.memories
reminders = db.reminders
prompts = db.prompts

async def get_db_prompt(name: str):
    doc = await prompts.find_one({"name": name})
    return doc.get("content") if doc else None

async def update_db_prompt(name: str, content: str):
    await prompts.update_one(
        {"name": name},
        {"$set": {"content": content, "updated_at": datetime.now()}},
        upsert=True
    )

async def save_message(user_id: str, role: str, content: str, thought: str = None):
    doc = {
        "user_id": user_id,
        "role": role,
        "content": content,
        "timestamp": datetime.utcnow()
    }
    if thought:
        doc["thought"] = thought
    await conversations.insert_one(doc)

async def get_recent_history(user_id: str, limit: int = 15):
    cursor = conversations.find({"user_id": user_id}).sort("timestamp", -1).limit(limit)
    history = await cursor.to_list(length=limit)
    return history[::-1]

async def count_messages(user_id: str):
    return await conversations.count_documents({"user_id": user_id})

async def delete_oldest_messages(user_id: str, count: int):
    # Find IDs of oldest messages
    cursor = conversations.find({"user_id": user_id}).sort("timestamp", 1).limit(count)
    old_msgs = await cursor.to_list(length=count)
    ids = [m["_id"] for m in old_msgs]
    if ids:
        await conversations.delete_many({"_id": {"$in": ids}})

async def get_all_memories():
    cursor = memories.find({}).sort("timestamp", -1)       
    return await cursor.to_list(length=100)

async def delete_memory(memory_id: str):
    from bson import ObjectId
    await memories.delete_one({"_id": ObjectId(memory_id)})

async def get_all_reminders():
    cursor = reminders.find({}).sort("datetime", 1)        
    return await cursor.to_list(length=100)
