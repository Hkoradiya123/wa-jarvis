import httpx
import pytest
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:7860"
PASSWORD = os.getenv("DASHBOARD_PASSWORD", "testpassword")

@pytest.mark.asyncio
async def test_get_prompts_exists():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/prompts", headers={"X-Password": PASSWORD})
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_post_prompt_exists():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/prompts/AI_AGENT", 
            json={"content": "test prompt"},
            headers={"X-Password": PASSWORD}
        )
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_system_status_exists():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/system/status", headers={"X-Password": PASSWORD})
        assert response.status_code == 200
