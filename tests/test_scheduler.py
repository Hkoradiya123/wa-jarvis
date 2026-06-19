import pytest
from datetime import datetime, timedelta
from app.utils.datetime_parser import parse_datetime
from app.main import check_reminders_loop, send_whatsapp_message
from app.database.mongodb import reminders
from unittest.mock import patch, AsyncMock
import asyncio

def test_parse_datetime_relative():
    # Test relative minute
    t1 = parse_datetime("in 10 minutes")
    diff = t1 - datetime.now()
    assert 9 * 60 < diff.total_seconds() < 11 * 60

    # Test relative hour
    t2 = parse_datetime("in 2 hours")
    diff2 = t2 - datetime.now()
    assert 1.9 * 3600 < diff2.total_seconds() < 2.1 * 3600

    # Test tomorrow parsing
    t3 = parse_datetime("tomorrow 6 PM")
    assert t3.hour == 18
    assert t3.minute == 0
    assert (t3.date() - datetime.now().date()).days == 1

@pytest.mark.asyncio
async def test_check_reminders_loop_trigger():
    # Add a mock reminder that is due
    user_id = "test_user_scheduler"
    title = "Buy milk"
    
    # Insert pending reminder with datetime in the past
    past_time_str = (datetime.now() - timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
    reminder_id = await reminders.insert_one({
        "user_id": user_id,
        "title": title,
        "datetime": past_time_str,
        "priority": "high",
        "status": "pending"
    })
    
    # Mock send_whatsapp_message
    with patch("app.main.send_whatsapp_message", new_callable=AsyncMock) as mock_send:
        # We patch asyncio.sleep to break the infinite loop after 1 run
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            mock_sleep.side_effect = Exception("Break Loop")
            
            try:
                await check_reminders_loop()
            except Exception as e:
                assert str(e) == "Break Loop"
                
        # Verify it was sent and status updated
        assert mock_send.call_count == 1
        assert "Buy milk" in mock_send.call_args[0][1]
        
        # Verify status in database is now 'sent'
        updated = await reminders.find_one({"_id": reminder_id.inserted_id})
        assert updated["status"] == "sent"
        
    # Clean up
    await reminders.delete_many({"user_id": user_id})
