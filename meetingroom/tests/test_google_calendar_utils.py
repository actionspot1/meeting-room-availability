from datetime import datetime, timedelta
from core.utils.google_calendar_utils import (
    parse_iso_datetime,
    sort_appointments,
    is_current_time_between,
    get_current_datetime,
    get_appointments,
    format_time_slots,
    appointments_overlap,
    create_event,
)
from core.utils.google_calendar_service import GoogleCalendarService
from django.utils import timezone


# Dummy data for testing
APPOINTMENTS_DATA: list[dict[str, dict[str, str]]] = [
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
    expected_result: datetime = datetime(2024, 4, 2, 10, 0)
    assert parse_iso_datetime(datetime_str) == expected_result


def test_sort_appointments():
    appointments: list[dict[str, dict[str, str]]] = [
        {
            "start": {"dateTime": "2024-04-02T10:00:00"},
            "end": {"dateTime": "2024-04-02T11:00:00"},
        },
        {
            "start": {"dateTime": "2024-04-02T13:00:00"},
            "end": {"dateTime": "2024-04-02T14:00:00"},
        },
        {
            "start": {"dateTime": "2024-10-02T13:00:00"},
            "end": {"dateTime": "2024-10-02T14:00:00"},
        },
    ]
    sorted_appointments = sort_appointments(appointments)
    assert len(sorted_appointments) == 3
    assert (
        sorted_appointments[0][0]
        <= sorted_appointments[0][1]
        <= sorted_appointments[1][0]
        <= sorted_appointments[1][1]
        <= sorted_appointments[2][0]
        <= sorted_appointments[2][1]
    )


def test_is_current_time_between(mocker):
    current_time = timezone.localtime(timezone.now())
    start_time: datetime = current_time - timedelta(hours=1)
    end_time: datetime = current_time + timedelta(hours=1)

    mocked_datetime = mocker.patch("datetime.datetime")
    mocked_datetime.now.return_value = current_time

    assert is_current_time_between(start_time, end_time)

    start_time: datetime = current_time - timedelta(days=1)
    end_time: datetime = current_time + timedelta(days=1)

    mocked_datetime = mocker.patch("datetime.datetime")
    mocked_datetime.now.return_value = current_time

    assert is_current_time_between(start_time, end_time)


def test_get_current_datetime(mocker):
    current_time: datetime = timezone.localtime(timezone.now())
    mocked_datetime = mocker.patch("datetime.datetime")
    mocked_datetime.now.return_value = current_time
    print(get_current_datetime())
    print(current_time)
    assert get_current_datetime() == timezone.localtime(timezone.now())


# def test_get_business_hours():
#     cur_date = datetime.now()
#     start_datetime, end_datetime = get_business_hours(cur_date)
#     assert start_datetime.time() == datetime.strptime("8:00 AM", "%I:%M %p").time()
#     assert end_datetime.time() == datetime.strptime("7:00 PM", "%I:%M %p").time()


def test_get_appointments(mocker):
    google_calendar_service_mock = mocker.patch.object(
        GoogleCalendarService, "get_events"
    )
    google_calendar_service_mock.return_value = APPOINTMENTS_DATA
    assert get_appointments() == [
        (datetime(2024, 4, 2, 10, 0), datetime(2024, 4, 2, 11, 0)),
        (datetime(2024, 4, 2, 13, 0), datetime(2024, 4, 2, 14, 0)),
    ]


def test_format_time_slots():
    time_slots = [(datetime.now(), datetime.now() + timedelta(hours=1))]
    formatted_slots = format_time_slots(time_slots)
    assert isinstance(formatted_slots, list)
    assert len(formatted_slots) == 1


# def test_appointments_overlap():
#     current_timezone = timezone.get_current_timezone()
#     start_time = timezone.localtime(timezone.now(), current_timezone)
#     end_time = start_time + timedelta(hours=1)
#     appointments = [
#         (start_time - timedelta(minutes=30), end_time + timedelta(minutes=30))
#     ]
#     assert appointments_overlap(start_time, end_time, appointments)

#     appointments = [(start_time, end_time - timedelta(minutes=30))]
#     assert appointments_overlap(start_time, end_time, appointments)

#     current_datetime = datetime.now(current_timezone)
#     tomorrow_datetime = current_datetime + timedelta(days=1)
#     appointments = [(tomorrow_datetime, tomorrow_datetime + timedelta(hours=1))]
#     assert not appointments_overlap(start_time, end_time, appointments)


def test_appointments_overlap_empty(mocker):
    mocker.patch(
        "core.utils.google_calendar_utils.get_appointments",
        return_value=[],
    )
    insert_start_datetime: datetime = datetime.now(
        timezone.get_current_timezone()
    ).replace(minute=0, second=0)
    insert_end_datetime: datetime = datetime.now(
        timezone.get_current_timezone()
    ).replace(minute=0, second=0) + timedelta(hours=1, minutes=30)
    number_of_people: int = 4

    assert appointments_overlap(
        insert_start_datetime, insert_end_datetime, number_of_people
    ) == (False, "Launchpad") or appointments_overlap(
        insert_start_datetime, insert_end_datetime, number_of_people
    ) == (
        False,
        "Wall Street",
    )

    number_of_people = 9
    expected_result: tuple[bool, str] = (False, "Radio City")
    assert (
        appointments_overlap(
            insert_start_datetime, insert_end_datetime, number_of_people
        )
        == expected_result
    )


def test_appointments_overlap_wall_street_booked(mocker):
    meeting_start: datetime = datetime.now(timezone.get_current_timezone()).replace(
        minute=0, second=0
    ) + timedelta(hours=1)
    meeting_end: datetime = datetime.now(timezone.get_current_timezone()).replace(
        minute=0, second=0
    ) + timedelta(hours=2)

    mocker.patch(
        "core.utils.google_calendar_utils.get_appointments",
        return_value=[
            (
                meeting_start,
                meeting_end,
                4,
                "Wall Street",
            )
        ],
    )
    insert_start_datetime: datetime = datetime.now(
        timezone.get_current_timezone()
    ).replace(minute=0, second=0)
    insert_end_datetime: datetime = datetime.now(
        timezone.get_current_timezone()
    ).replace(minute=0, second=0) + timedelta(hours=1, minutes=30)
    number_of_people: int = 4
    expected_result: tuple[bool, str] = (False, "Launchpad")

    assert (
        appointments_overlap(
            insert_start_datetime, insert_end_datetime, number_of_people
        )
        == expected_result
    )

    insert_start_datetime: datetime = datetime.now(
        timezone.get_current_timezone()
    ).replace(minute=0, second=0) - timedelta(minutes=30)
    insert_end_datetime: datetime = datetime.now(
        timezone.get_current_timezone()
    ).replace(minute=0, second=0) + timedelta(hours=1, minutes=30)

    assert (
        appointments_overlap(
            insert_start_datetime, insert_end_datetime, number_of_people
        )
        == expected_result
    )

    meeting_start: datetime = datetime.now(timezone.get_current_timezone()).replace(
        minute=0, second=0
    ) + timedelta(days=1, hours=1)
    meeting_end: datetime = datetime.now(timezone.get_current_timezone()).replace(
        minute=0, second=0
    ) + timedelta(days=1, hours=2)

    mocker.patch(
        "core.utils.google_calendar_utils.get_appointments",
        return_value=[
            (
                meeting_start,
                meeting_end,
                4,
                "Wall Street",
            )
        ],
    )

    insert_start_datetime: datetime = datetime.now(
        timezone.get_current_timezone()
    ).replace(minute=0, second=0) + timedelta(days=1)
    insert_end_datetime: datetime = datetime.now(
        timezone.get_current_timezone()
    ).replace(minute=0, second=0) + timedelta(days=1, hours=1, minutes=30)

    assert (
        appointments_overlap(
            insert_start_datetime, insert_end_datetime, number_of_people
        )
        == expected_result
    )


def test_appointments_overlap_both_booked(mocker):
    meeting_start: datetime = datetime.now(timezone.get_current_timezone()).replace(
        minute=0, second=0
    ) + timedelta(hours=1)
    meeting_end: datetime = datetime.now(timezone.get_current_timezone()).replace(
        minute=0, second=0
    ) + timedelta(hours=2)

    mocker.patch(
        "core.utils.google_calendar_utils.get_appointments",
        return_value=[
            (
                meeting_start,
                meeting_end,
                3,
                "Wall Street",
            ),
            (meeting_start, meeting_end, 3, "Launchpad"),
        ],
    )

    insert_start_datetime: datetime = datetime.now(
        timezone.get_current_timezone()
    ).replace(minute=0, second=0)
    insert_end_datetime: datetime = datetime.now(
        timezone.get_current_timezone()
    ).replace(minute=0, second=0) + timedelta(hours=1, minutes=30)
    number_of_people: int = 4
    expected_result: tuple[bool, str] = (True, "Both")

    assert (
        appointments_overlap(
            insert_start_datetime, insert_end_datetime, number_of_people
        )
        == expected_result
    )

    insert_start_datetime: datetime = datetime.now(
        timezone.get_current_timezone()
    ).replace(minute=0, second=0) - timedelta(minutes=30)
    insert_end_datetime: datetime = datetime.now(
        timezone.get_current_timezone()
    ).replace(minute=0, second=0) + timedelta(hours=1, minutes=30)

    assert (
        appointments_overlap(
            insert_start_datetime, insert_end_datetime, number_of_people
        )
        == expected_result
    )

    meeting_start: datetime = datetime.now(timezone.get_current_timezone()).replace(
        minute=0, second=0
    ) + timedelta(days=1, hours=1)
    meeting_end: datetime = datetime.now(timezone.get_current_timezone()).replace(
        minute=0, second=0
    ) + timedelta(days=1, hours=2)

    mocker.patch(
        "core.utils.google_calendar_utils.get_appointments",
        return_value=[
            (
                meeting_start,
                meeting_end,
                3,
                "Wall Street",
            ),
            (meeting_start, meeting_end, 3, "Launchpad"),
        ],
    )

    insert_start_datetime: datetime = datetime.now(
        timezone.get_current_timezone()
    ).replace(minute=0, second=0) + timedelta(days=1)
    insert_end_datetime: datetime = datetime.now(
        timezone.get_current_timezone()
    ).replace(minute=0, second=0) + timedelta(days=1, hours=1, minutes=30)

    assert (
        appointments_overlap(
            insert_start_datetime, insert_end_datetime, number_of_people
        )
        == expected_result
    )


def test_appointments_overlap_radio_city_booked(mocker):
    meeting_start: datetime = datetime.now(timezone.get_current_timezone()).replace(
        minute=0, second=0
    ) + timedelta(hours=1)
    meeting_end: datetime = datetime.now(timezone.get_current_timezone()).replace(
        minute=0, second=0
    ) + timedelta(hours=2)

    mocker.patch(
        "core.utils.google_calendar_utils.get_appointments",
        return_value=[
            (
                meeting_start,
                meeting_end,
                4,
                "Radio City",
            ),
        ],
    )

    insert_start_datetime: datetime = datetime.now(
        timezone.get_current_timezone()
    ).replace(minute=0, second=0)
    insert_end_datetime: datetime = datetime.now(
        timezone.get_current_timezone()
    ).replace(minute=0, second=0) + timedelta(hours=1, minutes=30)
    number_of_people: int = 5
    expected_result: tuple[bool, str] = (True, "Radio City")

    assert (
        appointments_overlap(
            insert_start_datetime, insert_end_datetime, number_of_people
        )
        == expected_result
    )

    insert_start_datetime: datetime = datetime.now(
        timezone.get_current_timezone()
    ).replace(minute=0, second=0) - timedelta(minutes=30)
    insert_end_datetime: datetime = datetime.now(
        timezone.get_current_timezone()
    ).replace(minute=0, second=0) + timedelta(hours=1, minutes=30)

    assert (
        appointments_overlap(
            insert_start_datetime, insert_end_datetime, number_of_people
        )
        == expected_result
    )

    meeting_start: datetime = datetime.now(timezone.get_current_timezone()).replace(
        minute=0, second=0
    ) + timedelta(days=1, hours=1)
    meeting_end: datetime = datetime.now(timezone.get_current_timezone()).replace(
        minute=0, second=0
    ) + timedelta(days=1, hours=2)

    mocker.patch(
        "core.utils.google_calendar_utils.get_appointments",
        return_value=[
            (
                meeting_start,
                meeting_end,
                4,
                "Radio City",
            ),
        ],
    )

    insert_start_datetime: datetime = datetime.now(
        timezone.get_current_timezone()
    ).replace(minute=0, second=0) + timedelta(days=1)
    insert_end_datetime: datetime = datetime.now(
        timezone.get_current_timezone()
    ).replace(minute=0, second=0) + timedelta(days=1, hours=1, minutes=30)

    assert (
        appointments_overlap(
            insert_start_datetime, insert_end_datetime, number_of_people
        )
        == expected_result
    )


def test_appointments_overlap_end_of_func():
    pass


def test_create_event(mocker):
    google_calendar_service_mock = mocker.patch.object(
        GoogleCalendarService, "create_event"
    )

    name: str = "Test Event"
    email: str = "test@example.com"
    start_datetime_formatted: str = datetime.now().isoformat()
    end_datetime_formatted: str = (datetime.now() + timedelta(hours=1)).isoformat()
    number_of_people: int = 4
    location_summary: str = "Launchpad"

    create_event(
        name,
        email,
        start_datetime_formatted,
        end_datetime_formatted,
        number_of_people,
        location_summary,
    )

    google_calendar_service_mock.assert_called_once_with(
        name,
        email,
        start_datetime_formatted,
        end_datetime_formatted,
        number_of_people - 1,
        location_summary,
    )
