import pytest
from app.agents.registry import get_agent_prompt
from app.agents.router_agent import AgentType

from app.database import mongodb

@pytest.mark.asyncio
async def test_agent_registry_retrieval():
    # Clear db custom prompts to ensure it falls back to defaults
    await mongodb.prompts.delete_many({})
    
    # Retrieve AI_AGENT prompt
    ai_prompt = await get_agent_prompt("AI_AGENT")
    assert "Jarvis" in ai_prompt


    # Retrieve MEMORY_AGENT prompt
    mem_prompt = await get_agent_prompt("MEMORY_AGENT")
    assert "long-term memory" in mem_prompt

    # Retrieve unknown agent returns AI_AGENT prompt fallback
    fallback_prompt = await get_agent_prompt("GIBBERISH_AGENT")
    assert "Jarvis" in fallback_prompt
