import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

OPENWA_API_URL = os.getenv("OPENWA_API_URL", "http://localhost:2785")
OPENWA_API_KEY = os.getenv("OPENWA_API_KEY", "dev-admin-key")
SESSION_ID = os.getenv("SESSION_ID", "433b737a-134a-4a61-9a15-e2f623ca59f8")
WEBHOOK_URL = "https://bloating-repurpose-riches.ngrok-free.dev/webhook"

async def debug_setup():
    print("🛠️  Refreshing Webhook with ALL events...")
    url = f"{OPENWA_API_URL}/api/sessions/{SESSION_ID}/webhooks"
    headers = {"Authorization": f"Bearer {OPENWA_API_KEY}"}
    
    # We explicitly list all possible message-related events
    payload = {
        "url": WEBHOOK_URL,
        "events": [
            "message",
            "message.received",
            "message.sent",
            "message.any",
            "*"
        ]
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # First, let's see current webhooks
            curr = await client.get(url, headers=headers)
            print(f"Current Webhooks: {curr.text}")
            
            # Now update
            response = await client.post(url, json=payload, headers=headers, timeout=10.0)
            if response.status_code in [200, 201]:
                print("✅ Webhook updated! Now send a message to yourself and check the FastAPI log.")
            else:
                print(f"❌ Failed: {response.status_code} | {response.text}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_setup())
