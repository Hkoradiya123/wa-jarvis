import pytest
from app.agents.router_agent import RouterResponse, AgentType
from app.main import get_ai_response
from unittest.mock import patch, AsyncMock

def test_router_pydantic_parsing():
    # Valid structured JSON
    r1 = RouterResponse.model_validate_json('{"agent": "SEARCH_AGENT"}')
    assert r1.agent == AgentType.SEARCH_AGENT

    # Invalid structured JSON raises validation error
    with pytest.raises(Exception):
        RouterResponse.model_validate_json('{"agent": "INVALID_AGENT"}')

@pytest.mark.asyncio
async def test_get_ai_response_routing_fallback():
    # Mock call_llm to return messy/lowercase agent format
    with patch("app.main.call_llm", new_callable=AsyncMock) as mock_call:
        mock_call.side_effect = [
            '{"agent": "search_agent"}', # Router mock
            'FastAPI today', # Search query optimizer mock
            '<thought>Searching</thought><answer>Here is information about FastAPI.</answer>' # Search agent response mock
        ]
        
        # We also mock search_and_summarize to avoid hitting the live web
        with patch("app.main.search_and_summarize", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = "FastAPI is a modern web framework."
            
            res = await get_ai_response("user123", "FastAPI current status")
            assert "FastAPI" in res
