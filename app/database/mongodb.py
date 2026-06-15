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

async def save_message(user_id: str, role: str, content: str):
    await conversations.insert_one({
        "user_id": user_id,
        "role": role,
        "content": content,
        "timestamp": datetime.utcnow()
    })

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
