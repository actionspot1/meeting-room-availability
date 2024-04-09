from datetime import datetime, time
from django.http import HttpRequest
from django.http.response import HttpResponse
from core.utils.reservation_utils import (
    render_reservation_form,
    validate_form_data,
    get_form_data,
    process_reservation_form,
)


def test_render_reservation_form():
    req = HttpRequest()
    business_hours = (time(8, 0), time(17, 0))
    response = render_reservation_form(req, business_hours)
    assert isinstance(response, HttpResponse)


def test_validate_form_data():
    form_data = {
        "name": "Test Event",
        "start_datetime": "2024-04-02T10:00:00",
        "end_datetime": "2024-04-02T11:00:00",
        "email": "test@example.com",
    }
    assert validate_form_data(form_data) is None  # Test with valid form data
    form_data["name"] = ""  # Make name empty to test missing required data
    assert validate_form_data(form_data) == "Missing required data"


def test_get_form_data():
    form_data = {
        "name": "Test Event",
        "start_datetime": datetime(2024, 4, 2, 10, 0, 0),
        "end_datetime": datetime(2024, 4, 2, 11, 0, 0),
        "email": "test@example.com",
    }

    start_datetime, end_datetime, name, email = get_form_data(form_data)

    assert isinstance(start_datetime, datetime)
    assert isinstance(end_datetime, datetime)
    assert name == "Test Event"
    assert email == "test@example.com"


def test_process_reservation_form(mocker):
    req = HttpRequest()
    req.POST = {
        "name": "Test Event",
        "start_datetime": "2024-04-02T10:00:00",
        "end_datetime": "2024-04-02T11:00:00",
        "email": "test@example.com",
    }
    mock_event_form_class = mocker.patch("core.forms.EventForm")
    form_instance = mocker.MagicMock()
    form_instance.is_valid.return_value = True
    form_instance.cleaned_data = req.POST
    mock_event_form_class.return_value = form_instance

    business_hours = (datetime(2024, 4, 2, 8, 0), datetime(2024, 4, 2, 17, 0))
    appointments = [(datetime(2024, 4, 2, 9, 0), datetime(2024, 4, 2, 9, 30))]

    response = process_reservation_form(req, business_hours, appointments)
    assert isinstance(response, HttpResponse)
