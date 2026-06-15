import os
import httpx
from dotenv import load_dotenv
from app.utils.logger import get_logger

load_dotenv()
logger = get_logger("llm")

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NVIDIA_MODEL = os.getenv("NVIDIA_MODEL", "meta/llama-3.1-8b-instruct")
INVOKE_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

async def call_llm(messages: list, model: str = None, max_tokens: int = 1024):
    """
    Calls NVIDIA NIM API with support for conversation history.
    """
    if not model:
        model = NVIDIA_MODEL
        
    logger.info(f"LLM Call - Model: {model}")
        
    if not NVIDIA_API_KEY:
        logger.error("NVIDIA_API_KEY not found in environment variables.")
        return "Error: NVIDIA_API_KEY is missing."

    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Accept": "application/json"
    }

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.2,
        "top_p": 0.7,
        "stream": False
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(INVOKE_URL, headers=headers, json=payload, timeout=60.0)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Error calling NVIDIA NIM: {e}")
            return f"Error: Could not reach AI assistant. {str(e)}"
