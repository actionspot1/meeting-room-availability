from datetime import datetime
from typing import List, Tuple
from django.utils import timezone
from .google_calendar_service import GoogleCalendarService

calendar_service: GoogleCalendarService = GoogleCalendarService()


def parse_iso_datetime(datetime_str: str) -> datetime:
    return datetime.fromisoformat(datetime_str)


def sort_appointments(appointments: List[dict]) -> List[Tuple[datetime, datetime]]:
    sorted_appointments: list[tuple[datetime, datetime]] = [
        (
            parse_iso_datetime(appointment["start"]["dateTime"]),
            parse_iso_datetime(appointment["end"]["dateTime"]),
        )
        for appointment in appointments
    ]
    return sorted(sorted_appointments)


def is_current_time_between(start_time: datetime, end_time: datetime) -> bool:
    local_timezone = timezone.get_current_timezone()
    current_time: datetime = datetime.now(local_timezone)
    return start_time <= current_time <= end_time


def get_current_datetime() -> datetime:
    local_timezone = timezone.get_current_timezone()
    return datetime.now(local_timezone).astimezone()


def get_business_hours(cur_date: datetime) -> Tuple[datetime, datetime]:
    start_time = datetime.strptime("8:00 AM", "%I:%M %p").time()
    end_time = datetime.strptime("7:00 PM", "%I:%M %p").time()

    start_datetime: datetime = datetime.combine(cur_date.date(), start_time)
    end_datetime: datetime = datetime.combine(cur_date.date(), end_time)

    return (start_datetime, end_datetime)


def get_appointments() -> List[Tuple[datetime, datetime]]:
    appointments_data: list = calendar_service.get_events()
    appointments: List[Tuple[datetime, datetime]] = sort_appointments(appointments_data)

    if not appointments:
        return []

    print("get_appointments(): ", appointments)
    return appointments


def format_time_slots(time_slots: List[Tuple[datetime, datetime]]) -> List[List[str]]:
    return [
        [start.strftime("%#I:%M %p"), end.strftime("%#I:%M %p")]
        for start, end in time_slots
    ]


def appointments_overlap(
    start_time: datetime,
    end_time: datetime,
    appointments: List[Tuple[datetime, datetime]],
) -> bool:

    if end_time.date() != start_time.date():
        return True

    if end_time < get_current_datetime():
        return True

    if not appointments:
        return False

    for time_slot in appointments:
        if (
            (start_time < time_slot[0] < end_time)
            or (time_slot[0] <= start_time < time_slot[1])
            or (time_slot[0] < end_time <= time_slot[1])
        ):
            return True

    return False


def create_event(
    name: str, email: str, start_datetime_formatted: str, end_datetime_formatted: str
):
    calendar_service.create_event(
        name, email, start_datetime_formatted, end_datetime_formatted
    )
