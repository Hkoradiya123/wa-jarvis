import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv(override=True)

OPENWA_API_URL = os.getenv("OPENWA_API_URL", "http://localhost:2785")
OPENWA_API_KEY = os.getenv("OPENWA_API_KEY")
SESSION_ID = os.getenv("SESSION_ID", "default")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "http://127.0.0.1:8000/webhook")

async def setup_webhook():
    """
    Registers the FastAPI webhook URL with the Open-WA gateway using authentication.
    """
    url = f"{OPENWA_API_URL.rstrip('/')}/api/sessions/{SESSION_ID}/webhooks"
    
    # We must include the API key in the headers
    headers = {
        "Authorization": f"Bearer {OPENWA_API_KEY}"
    }
    
    payload = {
        "url": WEBHOOK_URL,
        "events": ["*"]
    }
    
    print(f"Connecting to Open-WA at: {OPENWA_API_URL}")
    print(f"Registering Webhook: {WEBHOOK_URL}")
    print(f"Using API Key: {OPENWA_API_KEY[:5]}...{OPENWA_API_KEY[-5:] if OPENWA_API_KEY else ''}")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers, timeout=10.0)
            if response.status_code == 200 or response.status_code == 201:
                print("✅ Success! Open-WA will now send messages to your FastAPI app.")
            else:
                print(f"❌ Failed. Status Code: {response.status_code}")
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"❌ Error: Could not connect to Open-WA. {str(e)}")

if __name__ == "__main__":
    if not OPENWA_API_KEY or OPENWA_API_KEY == "your_wa_api_key_here":
        print("❌ Error: OPENWA_API_KEY is not set in .env file.")
    else:
        asyncio.run(setup_webhook())
