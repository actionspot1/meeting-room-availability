import pytest
from datetime import datetime, time, date, timedelta
from django.utils import timezone
from unittest.mock import MagicMock, patch
from core.utils import (
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


@pytest.fixture
def mocked_calendar_service():
    with patch("core.utils.calendar_service") as mocked_service:
        yield mocked_service


def test_parse_iso_datetime():
    # Test valid input
    assert parse_iso_datetime("2024-04-01T08:00:00") == datetime(2024, 4, 1, 8, 0)

    # Test invalid input
    with pytest.raises(ValueError):
        parse_iso_datetime("2024-04-01 08:00:00")


def test_sort_appointments():
    # Test sorting of appointments
    appointments = [
        {
            "start": {"dateTime": "2024-04-01T08:00:00"},
            "end": {"dateTime": "2024-04-01T09:00:00"},
        },
        {
            "start": {"dateTime": "2024-04-01T10:00:00"},
            "end": {"dateTime": "2024-04-01T11:00:00"},
        },
        {
            "start": {"dateTime": "2024-04-01T09:00:00"},
            "end": {"dateTime": "2024-04-01T10:00:00"},
        },
    ]
    sorted_appointments = sort_appointments(appointments)
    assert len(sorted_appointments) == 3
    assert sorted_appointments[0] == (
        datetime(2024, 4, 1, 8, 0),
        datetime(2024, 4, 1, 9, 0),
    )
    assert sorted_appointments[1] == (
        datetime(2024, 4, 1, 9, 0),
        datetime(2024, 4, 1, 10, 0),
    )
    assert sorted_appointments[2] == (
        datetime(2024, 4, 1, 10, 0),
        datetime(2024, 4, 1, 11, 0),
    )


def test_is_current_time_between():
    current_datetime: datetime = timezone.localtime(timezone.now())

    start_time: datetime = timezone.make_aware(
        datetime.combine(current_datetime.date(), time(hour=8, minute=0)),
        timezone=current_datetime.tzinfo,
    )
    end_time: datetime = timezone.make_aware(
        datetime.combine(current_datetime.date(), time(hour=18, minute=0)),
        timezone=current_datetime.tzinfo,
    )
    assert is_current_time_between(start_time, end_time) == True

    # Test when current time is not between start and end times
    start_time: datetime = timezone.make_aware(
        datetime.combine(current_datetime.date(), time(hour=10, minute=0)),
        timezone=current_datetime.tzinfo,
    )
    end_time: datetime = timezone.make_aware(
        datetime.combine(current_datetime.date(), time(hour=12, minute=0)),
        timezone=current_datetime.tzinfo,
    )
    assert is_current_time_between(start_time, end_time) == False


def test_get_current_datetime():
    # Test that the current datetime is obtained
    current_datetime = get_current_datetime()
    assert isinstance(current_datetime, datetime)


def test_get_business_hours():
    # Test getting business hours for a specific date
    cur_date = datetime(2024, 4, 1)
    start_time, end_time = get_business_hours(cur_date)
    assert start_time == datetime(2024, 4, 1, 8, 0)
    assert end_time == datetime(2024, 4, 1, 19, 0)


def test_get_appointments(mocked_calendar_service):
    # Mock the calendar service to return sample data
    mocked_calendar_service.get_events.return_value = [
        {
            "start": {"dateTime": "2024-04-01T08:00:00"},
            "end": {"dateTime": "2024-04-01T09:00:00"},
        },
        {
            "start": {"dateTime": "2024-04-01T10:00:00"},
            "end": {"dateTime": "2024-04-01T11:00:00"},
        },
    ]

    # Test getting appointments
    appointments = get_appointments()
    assert len(appointments) == 2
    assert appointments[0] == (datetime(2024, 4, 1, 8, 0), datetime(2024, 4, 1, 9, 0))
    assert appointments[1] == (datetime(2024, 4, 1, 10, 0), datetime(2024, 4, 1, 11, 0))


def test_get_available_time_slots():
    # Mock appointments data
    appointments = [
        (datetime(2024, 4, 1, 9, 0), datetime(2024, 4, 1, 10, 0)),
        (datetime(2024, 4, 1, 11, 0), datetime(2024, 4, 1, 12, 0)),
    ]

    # Test getting available time slots
    available_time_slots = get_available_time_slots(appointments)
    assert len(available_time_slots) == 2
    assert available_time_slots[0] == [
        datetime(2024, 4, 1, 10, 0),
        datetime(2024, 4, 1, 11, 0),
    ]
    assert available_time_slots[1] == [
        datetime(2024, 4, 1, 12, 0),
        datetime(2024, 4, 1, 19, 0),
    ]


def test_format_time_slots():
    # Mock time slots data
    time_slots = [
        (datetime(2024, 4, 1, 8, 0), datetime(2024, 4, 1, 9, 0)),
        (datetime(2024, 4, 1, 10, 0), datetime(2024, 4, 1, 11, 0)),
    ]

    # Test formatting time slots
    formatted_time_slots = format_time_slots(time_slots)
    assert len(formatted_time_slots) == 2
    assert formatted_time_slots[0] == ["8:00 AM", "9:00 AM"]
    assert formatted_time_slots[1] == ["10:00 AM", "11:00 AM"]


def test_appointments_overlap():
    # Test for overlapping appointments
    appointments = [
        (datetime(2024, 4, 1, 8, 0), datetime(2024, 4, 1, 9, 0)),
        (datetime(2024, 4, 1, 10, 0), datetime(2024, 4, 1, 11, 0)),
    ]
    start_time = datetime(2024, 4, 1, 8, 30)
    end_time = datetime(2024, 4, 1, 9, 30)
    assert appointments_overlap(start_time, end_time, appointments) == True

    # Test for non-overlapping appointments
    start_time = datetime(2024, 4, 1, 9, 30)
    end_time = datetime(2024, 4, 1, 10, 30)
    assert appointments_overlap(start_time, end_time, appointments) == False


def test_create_event(mocked_calendar_service):
    # Test creating an event
    create_event(
        "Meeting", "john@example.com", "2024-04-01T08:00:00", "2024-04-01T09:00:00"
    )
    mocked_calendar_service.create_event.assert_called_once_with(
        "Meeting", "john@example.com", "2024-04-01T08:00:00", "2024-04-01T09:00:00"
    )
