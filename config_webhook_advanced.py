import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

OPENWA_API_URL = os.getenv("OPENWA_API_URL", "http://localhost:2785")
OPENWA_API_KEY = os.getenv("OPENWA_API_KEY", "dev-admin-key")
SESSION_ID = os.getenv("SESSION_ID")
WEBHOOK_URL = "https://bloating-repurpose-riches.ngrok-free.dev/webhook"

async def advanced_setup():
    print("🚀 Attempting Advanced Webhook Configuration...")
    url = f"{OPENWA_API_URL}/api/sessions/{SESSION_ID}/webhooks"
    headers = {"Authorization": f"Bearer {OPENWA_API_KEY}"}
    
    # We attempt to pass advanced flags that some Open-WA versions support
    payload = {
        "url": WEBHOOK_URL,
        "events": ["*"],
        "options": {
            "skipMe": False,
            "onAnyMessage": True
        }
    }
    
    async with httpx.AsyncClient() as client:
        try:
            print(f"Targeting Session: {SESSION_ID}")
            response = await client.post(url, json=payload, headers=headers, timeout=10.0)
            if response.status_code in [200, 201]:
                print("✅ Advanced Webhook registered! (skipMe=False)")
                print("👉 Try sending a message to yourself now.")
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    if not SESSION_ID:
        print("❌ Error: SESSION_ID not found in .env. Run discover_session.py first.")
    else:
        asyncio.run(advanced_setup())
