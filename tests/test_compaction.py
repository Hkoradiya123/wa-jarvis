import pytest
from app.database import mongodb
import uuid

@pytest.mark.asyncio
async def test_compaction_soft_delete():
    user_id = f"test_user_comp_{uuid.uuid4()}"
    
    # 1. Insert 5 messages
    for i in range(5):
        await mongodb.save_message(user_id, "user", f"message {i}")
        
    assert await mongodb.count_messages(user_id) == 5
    
    # 2. Archive/compact oldest 2 messages
    await mongodb.delete_oldest_messages(user_id, 2)
    
    # 3. Active count should be 3
    assert await mongodb.count_messages(user_id) == 3
    
    # 4. Recent history should only return the 3 active ones
    recent = await mongodb.get_recent_history(user_id, limit=10)
    assert len(recent) == 3
    assert recent[0]["content"] == "message 2"
    
    # 5. Check database directly - items should still exist in collection but marked as archived
    db_items = await mongodb.conversations.find({"user_id": user_id}).to_list(length=10)
    assert len(db_items) == 5
    archived_count = sum(1 for item in db_items if item.get("archived") is True)
    assert archived_count == 2
    
    # Clean up
    await mongodb.conversations.delete_many({"user_id": user_id})

