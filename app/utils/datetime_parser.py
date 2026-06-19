import re
from datetime import datetime, timedelta, time, timezone

def parse_datetime(dt_str: str) -> datetime:
    dt_str = dt_str.strip().lower()
    now = datetime.now()
    
    # 1. Check relative: "in 5 minutes", "in 1 hour", etc.
    rel_match = re.match(r'in\s+(\d+)\s+(minute|hour|day)s?', dt_str)
    if rel_match:
        val = int(rel_match.group(1))
        unit = rel_match.group(2)
        if unit == 'minute':
            return now + timedelta(minutes=val)
        elif unit == 'hour':
            return now + timedelta(hours=val)
        elif unit == 'day':
            return now + timedelta(days=val)
            
    # 2. Check "tomorrow at 6 pm" or "tomorrow 6 pm" or "tomorrow 6pm"
    if 'tomorrow' in dt_str:
        tomorrow = now + timedelta(days=1)
        # Check if there is a time component, e.g. "6 pm" or "18:00"
        time_match = re.search(r'(\d+)\s*(:(\d+))?\s*(pm|am)?', dt_str.replace('tomorrow', '').strip())
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(3)) if time_match.group(3) else 0
            am_pm = time_match.group(4)
            if am_pm == 'pm' and hour < 12:
                hour += 12
            elif am_pm == 'am' and hour == 12:
                hour = 0
            return datetime.combine(tomorrow.date(), time(hour, minute))
        return datetime.combine(tomorrow.date(), time(9, 0)) # Default tomorrow at 9 AM
        
    # 3. Use dateutil parser fallback for standard dates
    import dateutil.parser
    try:
        parsed = dateutil.parser.parse(dt_str)
        # If it doesn't have tzinfo, assume local time
        return parsed
    except:
        # Fallback to returning now + 1 hour if parsing fails completely
        return now + timedelta(hours=1)
