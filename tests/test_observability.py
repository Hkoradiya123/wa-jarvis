import pytest
import json
import uuid
from app.main import process_message, estimate_tokens
from unittest.mock import patch, AsyncMock

def test_estimate_tokens():
    assert estimate_tokens("hello") == 1
    assert estimate_tokens("") == 0
    assert estimate_tokens("hello world fast") == 4

@pytest.mark.asyncio
async def test_process_message_logging():
    msg_id = f"test_msg_obs_{uuid.uuid4()}"
    payload = {
        "id": msg_id,
        "body": "//jarvis explain Docker",
        "from": "test_user_obs",
        "fromMe": False
    }

    # Mock call_llm
    with patch("app.main.call_llm", new_callable=AsyncMock) as mock_call:
        mock_call.side_effect = [
            '{"agent": "AI_AGENT"}', # Router
            '<thought>Reasoning</thought><answer>Hello there!</answer>' # AI Agent response
        ]
        
        # Patch logger.info to capture structured json output
        with patch("app.main.logger.info") as mock_info:
            await process_message(payload)
            
            # Find the json logging call
            log_calls = [c[0][0] for c in mock_info.call_args_list if isinstance(c[0][0], str) and "message_processed" in c[0][0]]
            assert len(log_calls) == 1
            
            log_data = json.loads(log_calls[0])
            assert log_data["event"] == "message_processed"
            assert log_data["request_id"] == msg_id
            assert log_data["agent_type"] == "AI_AGENT"
            assert log_data["latency_ms"] >= 0
            assert log_data["input_tokens"] > 0
            assert log_data["output_tokens"] > 0

