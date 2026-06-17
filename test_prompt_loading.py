import asyncio
from app.database.mongodb import get_db_prompt, update_db_prompt
from app.agents.ai_agent import get_ai_prompt
from app.agents.memory_agent import get_memory_prompt
from app.agents.reminder_agent import get_reminder_prompt
from app.agents.planner_agent import get_planner_prompt
from app.agents.summarizer_agent import get_summarizer_prompt
from app.agents.router_agent import get_router_prompt

async def test_prompts():
    print("Testing prompt loading...")
    
    # Test AI Agent
    ai_prompt = await get_ai_prompt()
    print(f"AI Prompt (should be default initially): {ai_prompt[:50]}...")
    
    # Update AI prompt in DB
    new_ai_content = "New AI Prompt from DB"
    await update_db_prompt("AI_AGENT", new_ai_content)
    
    # Fetch again
    ai_prompt_updated = await get_ai_prompt()
    print(f"AI Prompt (should be from DB): {ai_prompt_updated}")
    
    assert ai_prompt_updated == new_ai_content
    print("AI prompt test passed!")

    # Cleanup (optional, but good for repeatability)
    await update_db_prompt("AI_AGENT", None) # This might need a different way if we don't want to leave it there

if __name__ == "__main__":
    try:
        asyncio.run(test_prompts())
    except Exception as e:
        print(f"Test failed as expected: {e}")
