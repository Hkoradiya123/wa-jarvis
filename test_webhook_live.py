import httpx
import asyncio
import json

async def test():
    url = "https://jinksqspider-wa-ai.hf.space/webhook"
    
    messages = [
        "//jarvis hello",
        "//jarvis what is the time?",
        "//jarvis remember my name is admin"
    ]

    async with httpx.AsyncClient() as client:
        for msg in messages:
            print(f"Sending: {msg}")
            payload = {
                "event": "message",
                "data": {
                    "from": "test_user_123",
                    "body": msg,
                    "fromMe": False
                }
            }
            try:
                response = await client.post(url, json=payload, timeout=10.0)
                print(f"Status: {response.status_code}, Body: {response.text}")
            except Exception as e:
                print(f"Error: {e}")
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(test())
