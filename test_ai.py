import asyncio
import time
from app.utils.llm import call_llm

async def test_speed():
    print("🚀 Testing NVIDIA NIM Speed...")
    system_prompt = "You are a helpful assistant."
    user_message = "Hello, how are you? AND TELL ME WHAT IS FAST API."
    
    start_time = time.time()
    
    print("⏳ Sending request to NVIDIA NIM...")
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
    response = await call_llm(messages, max_tokens=100)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print("-" * 30)
    print(f"🤖 AI Response: {response}")
    print(f"⏱️ Time Taken: {duration:.2f} seconds")
    print("-" * 30)
    
    if duration > 10:
        print("⚠️ Warning: AI response is slow. Consider checking your internet or using a different NVIDIA model.")
    else:
        print("✅ Speed looks good!")

if __name__ == "__main__":
    asyncio.run(test_speed())
