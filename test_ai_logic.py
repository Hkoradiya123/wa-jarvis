import asyncio
import os
import json
from app.main import process_message
from app.database.mongodb import conversations, memories, reminders, prompts
from datetime import datetime

async def test_full_ai_pipeline():
    print("🧠 Testing Full AI Pipeline Logic...")
    
    # Mock payload
    payload = {
        "from": "test_user_ai_test",
        "body": "//jarvis what is the best way to learn python?",
        "fromMe": False
    }

    print(f"📥 Simulating message: {payload['body']}")
    
    # We need to mock the send_whatsapp_message to see the result
    # For this test, we'll just check the database for the result
    
    try:
        await process_message(payload)
        
        print("🔍 Checking database for response...")
        # Get the latest assistant message for this user
        resp = await conversations.find_one(
            {"user_id": payload["from"], "role": "assistant"},
            sort=[("timestamp", -1)]
        )
        
        if resp:
            print("-" * 30)
            print(f"🤔 AI Thought: {resp.get('thought', 'None')}")
            print(f"💬 AI Answer: {resp['content']}")
            print("-" * 30)
            print("✅ Internal processing logic verified.")
        else:
            print("❌ No response found in history. Test failed.")
            
    except Exception as e:
        print(f"❌ Error during processing: {e}")

if __name__ == "__main__":
    asyncio.run(test_full_ai_pipeline())
