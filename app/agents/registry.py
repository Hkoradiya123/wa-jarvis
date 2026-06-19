from app.agents.router_agent import AgentType
from app.agents.ai_agent import get_ai_prompt
from app.agents.memory_agent import get_memory_prompt
from app.agents.reminder_agent import get_reminder_prompt
from app.agents.planner_agent import get_planner_prompt
from app.agents.search_agent import get_search_prompt
from app.agents.summarizer_agent import get_summarizer_prompt

# Mapping AgentType enums to their prompt retrieval functions
AGENT_PROMPT_REGISTRY = {
    AgentType.AI_AGENT: get_ai_prompt,
    AgentType.MEMORY_AGENT: get_memory_prompt,
    AgentType.REMINDER_AGENT: get_reminder_prompt,
    AgentType.PLANNER_AGENT: get_planner_prompt,
    AgentType.SEARCH_AGENT: get_search_prompt,
}

async def get_agent_prompt(agent_type_str: str) -> str:
    """
    Looks up prompt loader for the specified agent name from the registry.
    Defaults to AI_AGENT prompt if not found.
    """
    try:
        # Convert string to AgentType Enum
        agent_type = AgentType(agent_type_str)
    except ValueError:
        agent_type = AgentType.AI_AGENT

    prompt_fn = AGENT_PROMPT_REGISTRY.get(agent_type, get_ai_prompt)
    return await prompt_fn()
