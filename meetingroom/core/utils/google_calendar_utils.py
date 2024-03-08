from datetime import datetime, time
from typing import List, Tuple
from django.utils import timezone


def parse_iso_datetime(datetime_str: str) -> datetime:
    return datetime.fromisoformat(datetime_str)


def sort_appointments(appointments: List[dict]) -> List[Tuple[datetime, datetime]]:
    sorted_appointments = [
        (
            parse_iso_datetime(appointment["start"]["dateTime"]),
            parse_iso_datetime(appointment["end"]["dateTime"]),
        )
        for appointment in appointments
    ]
    return sorted(sorted_appointments)


def convert_datetime_to_time(
    appointment: Tuple[datetime, datetime]
) -> Tuple[time, time]:
    return appointment[0].time(), appointment[1].time()


def is_current_time_between(start_time: datetime, end_time: datetime) -> bool:
    local_timezone = timezone.get_current_timezone()
    current_time = datetime.now(local_timezone)
    return start_time <= current_time <= end_time


def get_current_time() -> time:
    local_timezone = timezone.get_current_timezone()
    return datetime.now(local_timezone).astimezone().time()


def get_business_hours() -> Tuple[time, time]:
    return (
        datetime.strptime("8:00 AM", "%I:%M %p").time(),
        datetime.strptime("7:00 PM", "%I:%M %p").time(),
    )


def get_appointments(calendar_service) -> List[Tuple[time, time]]:
    appointments_data: list = calendar_service.get_events()
    appointments: List[Tuple[datetime, datetime]] = sort_appointments(appointments_data)

    if not appointments:
        return []

    appointments = [convert_datetime_to_time(start_end) for start_end in appointments]
    print("appointments: ", appointments)
    return appointments


def get_available_time_slots(appointments: List[Tuple[time, time]]) -> List:
    if not appointments:
        return []

    business_hours = get_business_hours()
    local_timezone = timezone.get_current_timezone()
    business_hours = tuple(dt.replace(tzinfo=local_timezone) for dt in business_hours)
    print("business hours: ", business_hours)

    current_time = get_current_time()
    print("current time", current_time)

    available_time_slots = []

    if business_hours[0] < current_time <= appointments[0][0]:
        available_time_slots.append([current_time, appointments[0][0]])

    for i in range(1, len(appointments)):
        previous_end = appointments[i - 1][1]
        current_start = appointments[i][0]

        if previous_end >= current_start:
            continue
        available_time_slots.append([previous_end, current_start])

    if available_time_slots and available_time_slots[-1][-1] <= business_hours[1]:
        available_time_slots.append([available_time_slots[-1][-1], business_hours[1]])
    print("available time slots", available_time_slots)

    return available_time_slots
