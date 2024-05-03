import pytest
from django.core.exceptions import ValidationError
from core.forms import EventForm
from django.utils.timezone import now
from datetime import timedelta


def test_valid_event_form():
    # Valid data: End datetime is after start datetime
    form_data = {
        "name": "Test Event",
        "email": "test@example.com",
        "number_of_people": 5,
        "start_datetime": now() + timedelta(days=1),
        "end_datetime": now() + timedelta(days=1, hours=2),
    }
    form = EventForm(data=form_data)
    assert form.is_valid()


def test_invalid_event_form_end_before_start():
    # Invalid data: End datetime is before start datetime
    form_data = {
        "name": "Test Event",
        "email": "test@example.com",
        "number_of_people": 5,
        "start_datetime": "2024-04-02T11:00:00",
        "end_datetime": "2024-04-02T10:00:00",
    }
    form = EventForm(data=form_data)

    # Print debug message before full_clean() call
    print("Before full_clean() call")

    assert not form.is_valid()

    # Print debug message after is_valid() check
    print("After is_valid() check")

    try:
        form.full_clean()
    except ValidationError as e:
        # Print the validation error message
        print("Validation error message:", e)

    # Print debug message after full_clean() call
    print("After full_clean() call")

    with pytest.raises(ValidationError):
        form.full_clean()


def test_invalid_number_of_people():
    form_data = {
        "name": "Test Event",
        "email": "test@example.com",
        "number_of_people": 11,  # More people than allowed
        "start_datetime": now() + timedelta(days=1),
        "end_datetime": now() + timedelta(days=1, hours=2),
    }
    form = EventForm(data=form_data)
    assert form.is_valid() == False
    assert (
        "Ensure this value is less than or equal to 10."
        in form.errors["number_of_people"]
    )


def test_invalid_event_form_missing_datetime():
    # Invalid data: Missing start or end datetime
    form_data = {
        "name": "Test Event",
        "email": "test@example.com",
        "start_datetime": "2024-04-02T10:00:00",
        # 'end_datetime' is missing
    }
    form = EventForm(data=form_data)
    assert not form.is_valid()
    with pytest.raises(ValidationError):
        form.full_clean()


def test_invalid_event_form_missing_both_datetimes():
    # Invalid data: Missing both start and end datetime
    form_data = {
        "name": "Test Event",
        "email": "test@example.com",
        # Both 'start_datetime' and 'end_datetime' are missing
    }
    form = EventForm(data=form_data)
    assert not form.is_valid()
    with pytest.raises(ValidationError):
        form.full_clean()


def test_invalid_event_form_equal_datetimes():
    # Invalid data: Start datetime is equal to end datetime
    form_data = {
        "name": "Test Event",
        "email": "test@example.com",
        "start_datetime": "2024-04-02T10:00:00",
        "end_datetime": "2024-04-02T10:00:00",
    }
    form = EventForm(data=form_data)
    assert not form.is_valid()
    with pytest.raises(ValidationError):
        form.full_clean()
