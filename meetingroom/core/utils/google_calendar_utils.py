from datetime import datetime
from typing import List, Tuple
from django.utils import timezone
from .google_calendar_service import GoogleCalendarService
from .room_capacity_utils import SMALL_ROOM_MAX_CAPACITY, LARGE_ROOM_MAX_CAPACITY
import random

calendar_service: GoogleCalendarService = GoogleCalendarService()


def parse_iso_datetime(datetime_str: str) -> datetime:
    return datetime.fromisoformat(datetime_str)


def sort_appointments(
    appointments: List[dict],
) -> List[Tuple[datetime, datetime, int, str]]:

    sorted_appointments: list[tuple[datetime, datetime, int, str]] = []
    for appointment in appointments:

        if not appointment["start"].get("dateTime") or not appointment["end"].get(
            "dateTime"
        ):
            print("Skipping due to missing start or end time")
            continue
        sorted_appointments.append(
            (
                parse_iso_datetime(appointment["start"]["dateTime"]),
                parse_iso_datetime(appointment["end"]["dateTime"]),
                appointment["attendees"][0].get("additionalGuests", 0),
                appointment["summary"],
            )
        )
    print("sorted appointments", sorted_appointments)

    return sorted(sorted_appointments)


def is_current_time_between(start_time: datetime, end_time: datetime) -> bool:
    local_timezone = timezone.get_current_timezone()
    current_time: datetime = datetime.now(local_timezone)
    return start_time <= current_time <= end_time


def get_current_datetime() -> datetime:
    local_timezone = timezone.get_current_timezone()
    return datetime.now(local_timezone).astimezone()


def get_appointments() -> List[Tuple[datetime, datetime, int, str]]:
    appointments_data: list = calendar_service.get_events_list()
    appointments: List[Tuple[datetime, datetime, int, str]] = sort_appointments(
        appointments_data
    )

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
    start_datetime: datetime, end_datetime: datetime, number_of_people: int
) -> Tuple[bool, str]:

    if number_of_people < 1 or number_of_people > LARGE_ROOM_MAX_CAPACITY:
        return (True, "Error")

    if end_datetime.date() != start_datetime.date():
        return (True, "Error")

    if end_datetime < get_current_datetime():
        return (True, "Error")

    appointments: List[Tuple[datetime, datetime, int, str]] = get_appointments()

    if not appointments:
        if 1 <= number_of_people <= SMALL_ROOM_MAX_CAPACITY:
            rand_int = random.randint(0, 1)
            if rand_int == 1:
                return (False, "Launchpad")
            return (False, "Wall Street")
        if SMALL_ROOM_MAX_CAPACITY < number_of_people <= LARGE_ROOM_MAX_CAPACITY:
            return (False, "Radio City")

    is_launchpad_booked: bool = False
    is_wall_street_booked: bool = False

    for time_slot in appointments:
        print("time slot", time_slot)
        print("additional guests", time_slot[2])

        if (
            1 <= number_of_people <= SMALL_ROOM_MAX_CAPACITY
            and SMALL_ROOM_MAX_CAPACITY - 1 < time_slot[2] <= LARGE_ROOM_MAX_CAPACITY
        ):
            continue
        if (
            SMALL_ROOM_MAX_CAPACITY < number_of_people <= LARGE_ROOM_MAX_CAPACITY
            and 1 - 1 <= time_slot[2] <= SMALL_ROOM_MAX_CAPACITY - 1
        ):
            continue

        if (
            (start_datetime < time_slot[0] < end_datetime)
            or (time_slot[0] <= start_datetime < time_slot[1])
            or (time_slot[0] < end_datetime <= time_slot[1])
        ):

            if (
                SMALL_ROOM_MAX_CAPACITY < number_of_people <= LARGE_ROOM_MAX_CAPACITY
                and time_slot[3] == "Radio City"
            ):
                return (True, "Radio City")

            if 1 <= number_of_people <= SMALL_ROOM_MAX_CAPACITY:
                if time_slot[3] == "Launchpad":
                    is_launchpad_booked = True
                elif time_slot[3] == "Wall Street":
                    is_wall_street_booked = True

        if is_launchpad_booked and is_wall_street_booked:
            return (True, "Both")

    if 1 <= number_of_people <= SMALL_ROOM_MAX_CAPACITY:
        if not is_launchpad_booked:
            return (False, "Launchpad")
        if not is_wall_street_booked:
            return (False, "Wall Street")
    elif SMALL_ROOM_MAX_CAPACITY < number_of_people <= LARGE_ROOM_MAX_CAPACITY:
        return (False, "Radio City")

    return (True, "end of func")


def create_event(
    name: str,
    email: str,
    start_datetime_formatted: str,
    end_datetime_formatted: str,
    number_of_people: int,
    location_summary: str,
):
    calendar_service.create_event(
        name,
        email,
        start_datetime_formatted,
        end_datetime_formatted,
        number_of_people - 1,
        location_summary,
    )
