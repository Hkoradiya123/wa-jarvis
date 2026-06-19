import pytest
import time
from app.utils.mcp_tools import search_and_summarize, SEARCH_CACHE
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_search_cache_ttl():
    SEARCH_CACHE.clear()
    
    # Mock web_search
    with patch("app.utils.mcp_tools.web_search", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = [{"title": "FastAPI", "href": "https://fastapi.tiangolo.com", "body": "FastAPI body"}]
        
        # First call: Cache miss
        res1 = await search_and_summarize("FastAPI")
        assert "FastAPI" in res1
        assert mock_search.call_count == 1
        
        # Second call: Cache hit (mock should not be called again)
        res2 = await search_and_summarize("FastAPI")
        assert res2 == res1
        assert mock_search.call_count == 1

        # Test expiration
        SEARCH_CACHE["fastapi"] = (res1, time.time() - 10) # Set expiry in the past
        res3 = await search_and_summarize("FastAPI")
        assert mock_search.call_count == 2
