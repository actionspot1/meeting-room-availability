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


def get_meetings(calendar_service) -> List[Tuple[datetime, datetime]]:
    events_items: list = calendar_service.get_events()
    meetings: List[Tuple[datetime, datetime]] = get_sorted_meetings(events_items)
    print("booked meetings", meetings)
    return meetings


def get_available_times(meetings: List[Tuple[datetime, datetime]]):
    available_times = []
    business_opening = "8 AM"
    for i in range(1, len(meetings)):
        prev_end = meetings[i - 1][1]
        curr_start = meetings[i][0]

        prev_end_12hr = prev_end.strftime("%#I:%M %p")
        curr_start_12hr = curr_start.strftime("%#I:%M %p")

        if prev_end >= curr_start:
            continue
        available_times.append([prev_end_12hr, curr_start_12hr])

    print(available_times)
    if not available_times and len(meetings) == 1:
        available_times = "the whole day is available"

    return available_times
