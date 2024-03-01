from datetime import datetime
from typing import List, Tuple
from django.utils import timezone


def get_formatted_datetime(datetime_str: str) -> datetime:
    return datetime.fromisoformat(datetime_str)


def get_sorted_meetings(events_items: List[dict]) -> List[Tuple[datetime, datetime]]:
    meetings = [
        (
            get_formatted_datetime(event["start"]["dateTime"]),
            get_formatted_datetime(event["end"]["dateTime"]),
        )
        for event in events_items
    ]
    return sorted(meetings)


def is_time_now_between(start_time: datetime, end_time: datetime) -> bool:
    local_timezone = timezone.get_current_timezone()
    now = datetime.now(local_timezone)
    return start_time <= now <= end_time
