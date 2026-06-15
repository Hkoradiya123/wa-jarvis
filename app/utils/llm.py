import os
import httpx
from dotenv import load_dotenv
from app.utils.logger import get_logger

load_dotenv()
logger = get_logger("llm")

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
INVOKE_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

# Fallback model list (Prioritizing high performance, then reasoning, then speed)
MODELS = [
    os.getenv("LLM_MODEL_1", "meta/llama-3.3-70b-instruct"),         # Strongest standard model
    os.getenv("LLM_MODEL_2", "nvidia/llama-3.1-nemotron-70b-instruct"), # NVIDIA's optimized frontier model
    os.getenv("LLM_MODEL_3", "meta/llama-3.1-8b-instruct")           # Fast and reliable fallback
]

async def call_llm(messages: list, model: str = None, max_tokens: int = 1024):
    """
    Calls NVIDIA NIM API with support for conversation history and fallback models.
    """
    if not NVIDIA_API_KEY:
        logger.error("NVIDIA_API_KEY not found in environment variables.")
        return "Error: NVIDIA_API_KEY is missing."

    # If a specific model is requested, try only that one
    models_to_try = [model] if model else MODELS

    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Accept": "application/json"
    }

    for current_model in models_to_try:
        logger.info(f"Attempting LLM Call - Model: {current_model}")
        
        payload = {
            "model": current_model,
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
                content = data["choices"][0]["message"]["content"]
                logger.info(f"Success with model: {current_model}")
                return content
            except Exception as e:
                logger.warning(f"Failed with model {current_model}: {str(e)}")
                # If this was the last model or an explicit model request, return error
                if current_model == models_to_try[-1]:
                    logger.error(f"All LLM models failed. Last error: {str(e)}")
                    return f"Error: All AI models failed to respond. {str(e)}"
                
                logger.info("Retrying with next fallback model...")
                continue
