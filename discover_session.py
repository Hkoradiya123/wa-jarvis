import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv(override=True)

OPENWA_API_URL = os.getenv("OPENWA_API_URL", "http://localhost:2785")
OPENWA_API_KEY = os.getenv("OPENWA_API_KEY", "dev-admin-key")

async def discover_and_update_session():
    print("🕵️  Discovering active Open-WA sessions...")
    url = f"{OPENWA_API_URL}/api/sessions"
    headers = {"Authorization": f"Bearer {OPENWA_API_KEY}"}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                sessions = response.json()
                if not sessions:
                    print("❌ No active sessions found in Open-WA.")
                    return

                # Find the first connected or ready session
                active_session = None
                for s in sessions:
                    if s.get("status") in ["CONNECTED", "ready"]:
                        active_session = s
                        break
                
                if not active_session:
                    print("⚠️  No CONNECTED sessions found. Found these instead:")
                    for s in sessions:
                        print(f" - ID: {s.get('id')} | Status: {s.get('status')}")
                    return

                new_id = active_session.get("id")
                print(f"✅ Found active session! ID: {new_id}")
                
                # Update .env file
                env_path = ".env"
                with open(env_path, "r") as f:
                    lines = f.readlines()
                
                with open(env_path, "w") as f:
                    for line in lines:
                        if line.startswith("SESSION_ID="):
                            f.write(f"SESSION_ID={new_id}\n")
                        else:
                            f.write(line)
                
                print(f"📝 Updated .env with SESSION_ID={new_id}")
                print("🚀 You can now restart your bot!")
                
            else:
                print(f"❌ Failed to reach Open-WA. {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(discover_and_update_session())
