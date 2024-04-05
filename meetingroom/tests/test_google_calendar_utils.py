import pytest
from datetime import datetime, timedelta
from core.forms import EventForm
from core.utils.google_calendar_utils import (
    parse_iso_datetime,
    sort_appointments,
    is_current_time_between,
    get_current_datetime,
    get_business_hours,
    get_appointments,
    get_available_time_slots,
    format_time_slots,
    appointments_overlap,
    create_event,
)
from core.utils.google_calendar_service import GoogleCalendarService
from django.utils import timezone

# Dummy data for testing
APPOINTMENTS_DATA = [
    {
        "start": {"dateTime": "2024-04-02T10:00:00"},
        "end": {"dateTime": "2024-04-02T11:00:00"},
    },
    {
        "start": {"dateTime": "2024-04-02T13:00:00"},
        "end": {"dateTime": "2024-04-02T14:00:00"},
    },
]


def test_parse_iso_datetime():
    datetime_str = "2024-04-02T10:00:00"
    expected_result = datetime(2024, 4, 2, 10, 0)
    assert parse_iso_datetime(datetime_str) == expected_result


def test_sort_appointments():
    sorted_appointments = sort_appointments(APPOINTMENTS_DATA)
    assert len(sorted_appointments) == 2
    assert sorted_appointments[0][0] <= sorted_appointments[1][0]


def test_is_current_time_between(mocker):
    current_time = timezone.localtime(timezone.now())
    start_time = current_time - timedelta(hours=1)
    end_time = current_time + timedelta(hours=1)

    mocked_datetime = mocker.patch("datetime.datetime")
    mocked_datetime.now.return_value = current_time

    assert is_current_time_between(start_time, end_time)


def test_get_current_datetime(mocker):
    current_time: datetime = timezone.localtime(timezone.now())
    mocked_datetime = mocker.patch("datetime.datetime")
    mocked_datetime.now.return_value = current_time
    print(get_current_datetime())
    print(current_time)
    assert get_current_datetime() == current_time


def test_get_business_hours():
    cur_date = datetime.now()
    start_datetime, end_datetime = get_business_hours(cur_date)
    assert start_datetime.time() == datetime.strptime("8:00 AM", "%I:%M %p").time()
    assert end_datetime.time() == datetime.strptime("7:00 PM", "%I:%M %p").time()


def test_get_appointments(mocker):
    google_calendar_service_mock = mocker.patch.object(
        GoogleCalendarService, "get_events"
    )
    google_calendar_service_mock.return_value = APPOINTMENTS_DATA
    assert get_appointments() == [
        (datetime(2024, 4, 2, 10, 0), datetime(2024, 4, 2, 11, 0)),
        (datetime(2024, 4, 2, 13, 0), datetime(2024, 4, 2, 14, 0)),
    ]


# def test_get_available_time_slots():
#     current_timezone = timezone.get_current_timezone()
#     current_datetime = datetime.now(current_timezone)
#     next_month_datetime = current_datetime + timedelta(days=30)
#     next_month_1pm = next_month_datetime.replace(
#         hour=13, minute=0, second=0, microsecond=0
#     )

#     appointments: list[tuple[datetime, datetime]] = [
#         (next_month_1pm, next_month_1pm + timedelta(hours=1))
#     ]
#     assert get_available_time_slots(appointments) == [
#         (
#             next_month_datetime.replace(hour=8, minute=0, second=0, microsecond=0),
#             next_month_datetime.replace(hour=13, minute=0, second=0, microsecond=0),
#         ),
#         (
#             next_month_datetime.replace(hour=14, minute=0, second=0, microsecond=0),
#             next_month_datetime.replace(hour=19, minute=0, second=0, microsecond=0),
#         ),
#     ]


def test_format_time_slots():
    time_slots = [(datetime.now(), datetime.now() + timedelta(hours=1))]
    formatted_slots = format_time_slots(time_slots)
    assert isinstance(formatted_slots, list)
    assert len(formatted_slots) == 1


def test_appointments_overlap():
    current_timezone = timezone.get_current_timezone()
    start_time = timezone.localtime(timezone.now(), current_timezone)
    end_time = start_time + timedelta(hours=1)
    appointments = [
        (start_time - timedelta(minutes=30), end_time + timedelta(minutes=30))
    ]
    assert appointments_overlap(start_time, end_time, appointments)


def test_create_event(mocker):
    google_calendar_service_mock = mocker.patch.object(
        GoogleCalendarService, "create_event"
    )
    name = "Test Event"
    email = "test@example.com"
    start_datetime_formatted = datetime.now().isoformat()
    end_datetime_formatted = (datetime.now() + timedelta(hours=1)).isoformat()

    create_event(name, email, start_datetime_formatted, end_datetime_formatted)

    google_calendar_service_mock.assert_called_once_with(
        name, email, start_datetime_formatted, end_datetime_formatted
    )
