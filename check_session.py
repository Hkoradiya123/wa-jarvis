import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

OPENWA_API_URL = os.getenv("OPENWA_API_URL", "http://localhost:2785")
OPENWA_API_KEY = os.getenv("OPENWA_API_KEY", "dev-admin-key")
SESSION_ID = os.getenv("SESSION_ID", "default")

async def check_session():
    print("🔍 Checking WhatsApp Session Status...")
    url = f"{OPENWA_API_URL}/api/sessions/{SESSION_ID}"
    headers = {"Authorization": f"Bearer {OPENWA_API_KEY}"}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                status = data.get("status", "UNKNOWN")
                print(f"✅ Session Name: {SESSION_ID}")
                print(f"📊 Status: {status}")
                
                if status == "CONNECTED":
                    print("🌟 WhatsApp is ACTIVE and READY!")
                elif status == "QR":
                    print("⚠️  ACTION REQUIRED: You need to scan the QR code on the dashboard (http://localhost:2886).")
                else:
                    print(f"❓ Status is {status}. Try restarting Open-WA.")
            else:
                print(f"❌ Failed to reach Open-WA. Status Code: {response.status_code}")
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"❌ Error: Could not connect to Open-WA. Is it running on port 2785? {e}")

if __name__ == "__main__":
    asyncio.run(check_session())
