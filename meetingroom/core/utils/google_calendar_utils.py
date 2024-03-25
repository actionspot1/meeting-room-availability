from datetime import datetime, time, date
from typing import List, Tuple, Type
from django.utils import timezone
from core.forms import EventForm
from .google_calendar_service import GoogleCalendarService

calendar_service: GoogleCalendarService = GoogleCalendarService()


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
    current_time = datetime.now(local_timezone).time()
    return start_time <= current_time <= end_time


def get_current_datetime() -> datetime:
    local_timezone = timezone.get_current_timezone()
    return datetime.now(local_timezone).astimezone()


def get_business_hours(date: datetime) -> Tuple[datetime, datetime]:
    start_time = datetime.strptime("8:00 AM", "%I:%M %p").time()
    end_time = datetime.strptime("7:00 PM", "%I:%M %p").time()

    start_datetime = datetime.combine(date.date(), start_time)
    end_datetime = datetime.combine(date.date(), end_time)

    return (start_datetime, end_datetime)


def get_appointments() -> List[Tuple[datetime, datetime]]:
    appointments_data: list = calendar_service.get_events()
    appointments: List[Tuple[datetime, datetime]] = sort_appointments(appointments_data)

    if not appointments:
        return []

    # appointments = [convert_datetime_to_time(start_end) for start_end in appointments]
    print("get_appointments(): ", appointments)
    return appointments


def get_available_time_slots(appointments: List[Tuple[datetime, datetime]]) -> List:
    if not appointments:
        return []

    current_time: datetime = get_current_datetime()
    print("current time", current_time)

    business_hours = get_business_hours(current_time)
    local_timezone = timezone.get_current_timezone()
    business_hours = tuple(dt.replace(tzinfo=local_timezone) for dt in business_hours)
    print("business hours: ", business_hours)

    available_time_slots = []

    if business_hours[0] < current_time <= appointments[0][0]:
        available_time_slots.append([current_time, appointments[0][0]])

    for i in range(1, len(appointments)):
        previous_end = appointments[i - 1][1]
        current_start = appointments[i][0]

        if previous_end >= current_start:
            continue
        available_time_slots.append([previous_end, current_start])

    if appointments[-1][1] <= business_hours[1]:
        available_time_slots.append([appointments[-1][1], business_hours[1]])
    print("available time slots", available_time_slots)

    return available_time_slots


def format_time_slots(time_slots: List[Tuple[datetime, datetime]]) -> List[List[str]]:
    return [
        [start.strftime("%#I:%M %p"), end.strftime("%#I:%M %p")]
        for start, end in time_slots
    ]


def validate_form_data(form: EventForm) -> bool:
    return all(
        [
            form.cleaned_data.get("name"),
            form.cleaned_data.get("start_time"),
            form.cleaned_data.get("end_time"),
            form.cleaned_data.get("email"),
        ]
    )


def get_formatted_time_objects(form: EventForm) -> Tuple[time, time]:
    start_time_str = form.cleaned_data.get("start_time")
    end_time_str = form.cleaned_data.get("end_time")

    start_time = (
        datetime.strptime(start_time_str, "%H:%M").time() if start_time_str else time()
    )
    end_time = (
        datetime.strptime(end_time_str, "%H:%M").time() if end_time_str else time()
    )

    return start_time, end_time


def get_aware_datetime_objects(
    today: date, start_time: time, end_time: time
) -> Tuple[datetime, datetime]:
    start_datetime = timezone.make_aware(
        datetime.combine(today, start_time), timezone.get_current_timezone()
    )
    end_datetime = timezone.make_aware(
        datetime.combine(today, end_time), timezone.get_current_timezone()
    )
    return start_datetime, end_datetime


def format_datetime(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S%z")


def format_time(start_time: time, end_time: time) -> Tuple[str, str]:
    return start_time.strftime("%#I:%M %p"), end_time.strftime("%#I:%M %p")


def appointments_overlap(
    start_time: time,
    end_time: time,
    appointments: List[Tuple[time, time]],
) -> bool:
    if end_time < get_current_time():
        return True

    if not appointments:
        return False

    for time_slot in appointments:
        if (
            start_time < time_slot[0]
            and end_time >= time_slot[0]
            or time_slot[0] <= start_time < time_slot[1]
        ):
            return True
    return False


def create_event(
    name: str, email: str, start_datetime_formatted: str, end_datetime_formatted: str
):
    calendar_service.create_event(
        name, email, start_datetime_formatted, end_datetime_formatted
    )
