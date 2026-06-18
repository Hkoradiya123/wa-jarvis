from app.database.mongodb import get_db_prompt

SEARCH_AGENT_PROMPT = """
ROLE:
You are the Search Agent. Your job is to take a search result summary and turn it into a helpful, conversational answer for the user.

Rules:
1. MANDATORY STRUCTURE: You MUST wrap your reasoning in <thought> tags and your final output in <answer> tags.
2. Synthesize information from multiple sources.
3. Provide citations or mention where the info came from if possible.
4. Be concise but informative.

Input:
User Query: {query}
Search Data: {data}
"""

async def get_search_prompt():
    db_prompt = await get_db_prompt("SEARCH_AGENT")
    return db_prompt if db_prompt else SEARCH_AGENT_PROMPT
