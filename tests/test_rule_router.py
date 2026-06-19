import pytest
from app.main import determine_agent_by_rules
from app.agents.router_agent import AgentType

def test_determine_agent_by_rules():
    # Greetings
    assert determine_agent_by_rules("hello") == AgentType.AI_AGENT.value
    assert determine_agent_by_rules("Yo  ") == AgentType.AI_AGENT.value

    # Reminders
    assert determine_agent_by_rules("please remind me to buy milk") == AgentType.REMINDER_AGENT.value
    assert determine_agent_by_rules("set alarm for 6 AM") == AgentType.REMINDER_AGENT.value

    # Memory
    assert determine_agent_by_rules("remember that my color is red") == AgentType.MEMORY_AGENT.value
    assert determine_agent_by_rules("forget my preferences") == AgentType.MEMORY_AGENT.value

    # Search
    assert determine_agent_by_rules("search the web for OpenAI") == AgentType.SEARCH_AGENT.value
    assert determine_agent_by_rules("what is the weather in Paris?") == AgentType.SEARCH_AGENT.value

    # Planner
    assert determine_agent_by_rules("plan my day today") == AgentType.PLANNER_AGENT.value

    # Fallback to LLM (None)
    assert determine_agent_by_rules("what is the chemical formula of water?") is None
