import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from datetime import datetime, timezone

async def seed_memories():
    """Connects to the database and inserts sample memories."""
    load_dotenv()
    mongo_url = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongo_url)
    db = client.whatsapp_jarvis
    memories_collection = db.memories

    print("Checking for existing memories...")
    count = await memories_collection.count_documents({})
    if count > 0:
        print(f"Found {count} existing memories. Seeding not required.")
        return

    print("No memories found. Seeding database with sample data...")

    sample_memories = [
        {
            "user_id": "user1",
            "category": "personal",
            "value": "My favorite color is blue.",
            "timestamp": datetime.now(timezone.utc)
        },
        {
            "user_id": "user1",
            "category": "work",
            "value": "The project deadline is next Friday.",
            "timestamp": datetime.now(timezone.utc)
        },
        {
            "user_id": "user2",
            "category": "reminder",
            "value": "Buy milk on the way home.",
            "timestamp": datetime.now(timezone.utc)
        }
    ]

    result = await memories_collection.insert_many(sample_memories)
    print(f"Successfully inserted {len(result.inserted_ids)} memories.")

if __name__ == "__main__":
    # In Python 3.7+, you can use asyncio.run()
    # For older versions, you might need to use loop = asyncio.get_event_loop(); loop.run_until_complete(...)
    asyncio.run(seed_memories())
