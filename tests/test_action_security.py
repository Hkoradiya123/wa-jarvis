import pytest
from app.main import execute_agent_action

@pytest.mark.asyncio
async def test_action_whitelist_security():
    # Valid whitelisted action
    action_save = '{"action": "SAVE_MEMORY", "category": "preference", "value": "I like coffee"}'
    res = await execute_agent_action("user1", action_save)
    assert "✅ Memory saved" in res

    # Unsafe action
    action_delete = '{"action": "DELETE_ALL_MEMORIES"}'
    res = await execute_agent_action("user1", action_delete)
    assert "Rejected unsafe" in res

    # PII rejection
    action_pii = '{"action": "SAVE_MEMORY", "category": "credentials", "value": "My password is password123"}'
    res = await execute_agent_action("user1", action_pii)
    assert "Sensitive information" in res
