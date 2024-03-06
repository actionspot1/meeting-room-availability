from datetime import datetime
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


def is_current_time_between(start_time: datetime, end_time: datetime) -> bool:
    local_timezone = timezone.get_current_timezone()
    current_time = datetime.now(local_timezone)
    return start_time <= current_time <= end_time


def get_appointments(calendar_service) -> List[Tuple[datetime, datetime]]:
    appointments_data: list = calendar_service.get_events()
    appointments: List[Tuple[datetime, datetime]] = sort_appointments(appointments_data)
    print("booked appointments", appointments)
    return appointments


def get_available_time_slots(appointments: List[Tuple[datetime, datetime]]):
    available_time_slots = []
    business_hours = [
        "8:00 AM",
        "7:00 PM",
    ]

    if len(appointments) == 1:
        available_time_slots = [
            ["now", appointments[0][0].strftime("%#I:%M %p")],
            [appointments[-1][1].strftime("%#I:%M %p"), business_hours[1]],
        ]
        return available_time_slots

    for i in range(1, len(appointments)):
        previous_end = appointments[i - 1][1]
        current_start = appointments[i][0]

        previous_end_12hr = previous_end.strftime("%#I:%M %p")
        current_start_12hr = current_start.strftime("%#I:%M %p")

        if previous_end >= current_start:
            continue
        available_time_slots.append([previous_end_12hr, current_start_12hr])

    if datetime.strptime(available_time_slots[-1][-1], "%#I:%M %p") < datetime.strptime(
        business_hours[1], "%#I:%M %p"
    ):
        available_time_slots.append([[available_time_slots[-1][-1]], business_hours[1]])
    print("available time slots", available_time_slots)

    return available_time_slots
