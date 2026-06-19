import pytest
from app.database import mongodb

@pytest.mark.asyncio
async def test_memory_relevance_overlap():
    user_id = "test_user_mem"
    
    # Pre-populate database with memories
    await mongodb.save_memory_task(user_id, "sports", "I love playing basketball")
    await mongodb.save_memory_task(user_id, "languages", "My favorite programming language is Rust")
    await mongodb.save_memory_task(user_id, "food", "I prefer drinking green tea in the morning")

    # Query matching Rust
    res_rust = await mongodb.get_relevant_memories(user_id, "What programming language should I write this in?")
    assert len(res_rust) > 0
    assert "Rust" in res_rust[0]["value"]

    # Query matching basketball
    res_sports = await mongodb.get_relevant_memories(user_id, "Tell me about basketball")
    assert len(res_sports) > 0
    assert "basketball" in res_sports[0]["value"]
    
    # Query with no overlap falls back to returning the 3 most recent
    res_fallback = await mongodb.get_relevant_memories(user_id, "something random")
    assert len(res_fallback) == 3

    # Clean up
    await mongodb.memories.delete_many({"user_id": user_id})

