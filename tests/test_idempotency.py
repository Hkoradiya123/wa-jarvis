import pytest
import uuid
from app.database.mongodb import save_message, init_db_indexes, conversations

@pytest.mark.asyncio
async def test_save_message_idempotency():
    # Initialize unique index
    await init_db_indexes()
    
    user_id = f"test_user_{uuid.uuid4()}"
    msg_id = f"msg_{uuid.uuid4()}"
    
    # First save should succeed
    res1 = await save_message(user_id, "user", "Hello first time!", message_id=msg_id)
    assert res1 is True
    
    # Second save with same message_id should fail (idempotent skip)
    res2 = await save_message(user_id, "user", "Hello first time!", message_id=msg_id)
    assert res2 is False

    # Clean up
    await conversations.delete_many({"user_id": user_id})
