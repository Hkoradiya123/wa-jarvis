import httpx
import pytest
import pytest_asyncio
from app.main import app
from app.database import mongodb

@pytest_asyncio.fixture(autouse=True)
async def seed_test_admin():
    await mongodb.seed_admin()


HEADERS = {
    "X-Username": "admin",
    "X-Password": "Hkoradiya.jarvis"
}

@pytest.mark.asyncio
async def test_get_prompts_exists():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.get("/api/prompts", headers=HEADERS)
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_post_prompt_exists():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.post(
            "/api/prompts/TEST_AGENT", 
            json={"content": "test prompt"},
            headers=HEADERS
        )
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_system_status_exists():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.get("/api/system/status", headers=HEADERS)
        assert response.status_code == 200


