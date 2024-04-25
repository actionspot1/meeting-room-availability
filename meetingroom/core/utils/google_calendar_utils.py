from datetime import datetime
from typing import List, Tuple
from django.utils import timezone
from .google_calendar_service import GoogleCalendarService

calendar_service: GoogleCalendarService = GoogleCalendarService()


def parse_iso_datetime(datetime_str: str) -> datetime:
    return datetime.fromisoformat(datetime_str)


def sort_appointments(
    appointments: List[dict],
) -> List[Tuple[datetime, datetime, int, str]]:
    # sorted_appointments: list[tuple[datetime, datetime, int, str]] = [
    #     (
    #         parse_iso_datetime(appointment["start"]["dateTime"]),
    #         parse_iso_datetime(appointment["end"]["dateTime"]),
    #         appointment["additionalGuests"],
    #         appointment["summary"],
    #     )
    #     for appointment in appointments
    # ]

    sorted_appointments: list[tuple[datetime, datetime, int, str]] = []
    for appointment in appointments:
        # print("appointment", appointment)
        # print("attendees", appointment["attendees"][0]["additionalGuests"])
        if not appointment["start"].get("dateTime") or not appointment["end"].get(
            "dateTime"
        ):
            print("Skipping due to missing start or end time")
            continue
        sorted_appointments.append(
            (
                parse_iso_datetime(appointment["start"]["dateTime"]),
                parse_iso_datetime(appointment["end"]["dateTime"]),
                appointment["attendees"][0].get("additionalGuests", -1),
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
    appointments_data: list = calendar_service.get_events()
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


# events: sort events
def appointments_overlap(
    start_datetime: datetime, end_datetime: datetime, number_of_people: int
) -> Tuple[bool, str]:

    if end_datetime.date() != start_datetime.date():
        return (True, "Error")

    if end_datetime < get_current_datetime():
        return (True, "Error")

    # appointments = calendar_service.get_events()
    appointments: List[Tuple[datetime, datetime, int, str]] = get_appointments()

    if not appointments:
        return (False, "Launchpad")

    # for appointment in appointments:
    #     print(appointment)
    #     parse_iso_datetime(appointment["start"]["dateTime"])
    #     parse_iso_datetime(appointment["end"]["dateTime"])
    # appointments.sort(key=appointments["start"]["dateTime"])
    # print("appointments", appointments)

    is_launchpad_booked: bool = False
    is_wall_street_booked: bool = False

    for time_slot in appointments:
        print("time slot", time_slot)
        print("additional guests", time_slot[2])

        if 1 <= number_of_people <= 4 and 4 - 1 < time_slot[2] <= 10:
            continue
        if 4 < number_of_people <= 10 and 1 - 1 <= time_slot[2] <= 4 - 1:
            continue

        # if 4 < number_of_people <= 10 and time_slot["summary"] == "Radio City":
        #     if (
        #         (start_datetime < time_slot[0] < end_datetime)
        #         or (time_slot[0] <= start_datetime < time_slot[1])
        #         or (time_slot[0] < end_datetime <= time_slot[1])
        #     ):
        #         return (True, "Radio City")
        # elif 1 <= number_of_people <= 4:
        #     if (
        #         (start_datetime < time_slot[0] < end_datetime)
        #         or (time_slot[0] <= start_datetime < time_slot[1])
        #         or (time_slot[0] < end_datetime <= time_slot[1])
        #     ) and time_slot["summary"] == "Launchpad":
        #         is_launchpad_booked = True
        #     elif (
        #         (start_datetime < time_slot[0] < end_datetime)
        #         or (time_slot[0] <= start_datetime < time_slot[1])
        #         or (time_slot[0] < end_datetime <= time_slot[1])
        #     ) and time_slot["summary"] == "Wall Street":
        #         is_wall_street_booked = True

        if (
            (start_datetime < time_slot[0] < end_datetime)
            or (time_slot[0] <= start_datetime < time_slot[1])
            or (time_slot[0] < end_datetime <= time_slot[1])
        ):

            if 4 < number_of_people <= 10 and time_slot[3] == "Radio City":
                return (True, "Radio City")

            if 1 <= number_of_people <= 4:
                if time_slot[3] == "Launchpad":
                    is_launchpad_booked = True
                elif time_slot[3] == "Wall Street":
                    is_wall_street_booked = True

        if is_launchpad_booked and is_wall_street_booked:
            return (True, "Both")

    if 1 <= number_of_people <= 4:
        if not is_launchpad_booked:
            return (False, "Launchpad")
        if not is_wall_street_booked:
            return (False, "Wall Street")
    elif 4 < number_of_people <= 10:
        return (False, "Wall Street")

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
