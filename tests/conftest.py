import pytest_asyncio
import asyncio
from app.database import mongodb

@pytest_asyncio.fixture(autouse=True)
async def reinit_mongo_client():
    from motor.motor_asyncio import AsyncIOMotorClient
    loop = asyncio.get_running_loop()
    
    mongodb.client = AsyncIOMotorClient(mongodb.MONGO_URL, io_loop=loop)
    mongodb.db = mongodb.client.whatsapp_jarvis
    mongodb.conversations = mongodb.db.conversations
    mongodb.memories = mongodb.db.memories
    mongodb.reminders = mongodb.db.reminders
    mongodb.prompts = mongodb.db.prompts
    mongodb.users = mongodb.db.users
    mongodb.ai_chats = mongodb.db.ai_chats
