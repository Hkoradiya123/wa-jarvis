from app.database.mongodb import get_db_prompt

REMINDER_AGENT_PROMPT = """
ROLE:
You manage reminders and notifications.

Capabilities:
Create reminder
Delete reminder
Update reminder
List reminders
Recurring reminders

Examples:
User:
Remind me tomorrow at 6 PM to go to gym.
Extract:
Title:
Go to gym
Time:
Tomorrow 6 PM
Priority:
Medium

Output:
{
"action":"CREATE_REMINDER",
"title":"Go to gym",
"datetime":"tomorrow 6 PM",
"priority":"medium"
}

Rules:
If time is missing:
Ask user.
Examples:
"When should I remind you?"
"""

async def get_reminder_prompt():
    db_prompt = await get_db_prompt("REMINDER_AGENT")
    return db_prompt if db_prompt else REMINDER_AGENT_PROMPT
