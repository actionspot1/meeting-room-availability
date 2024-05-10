from .google_calendar_utils import (
    get_current_datetime,
    appointments_overlap,
    create_event,
)
from datetime import time, datetime
from typing import List, Tuple, Optional
from django.http import HttpResponse, HttpRequest
from ..forms import EventForm
from django.shortcuts import render
from .utils import handle_error


def render_reservation_form(
    req: HttpRequest,
) -> HttpResponse:
    context = {
        "form": EventForm(),
        "now": get_current_datetime(),
    }
    return render(req, "create_event.html", context)


def validate_form_data(form_data: dict) -> Optional[str]:
    name, start_datetime_str, end_datetime_str, email, number_of_people = (
        form_data.get("name", ""),
        form_data.get("start_datetime"),
        form_data.get("end_datetime"),
        form_data.get("email", ""),
        form_data.get("number_of_people", ""),
    )
    if not all([name, start_datetime_str, end_datetime_str, email, number_of_people]):
        return "Missing required data"
    return None


def get_form_data(form_data: dict) -> Tuple[datetime, datetime, str, str, int]:

    start_datetime: datetime = form_data.get("start_datetime")
    end_datetime: datetime = form_data.get("end_datetime")
    name, email = form_data.get("name", ""), form_data.get("email", "")
    number_of_people: int = form_data.get("number_of_people", "")
    return start_datetime, end_datetime, name, email, number_of_people


def process_reservation_form(
    req: HttpRequest,
) -> HttpResponse:
    form = EventForm(req.POST)
    context = {
        "form": form,
        "now": get_current_datetime(),
    }

    if not form.is_valid():
        return render(req, "create_event.html", context)

    errors: str | None = validate_form_data(form.cleaned_data)
    if errors:
        return render(req, "error.html", {"error message": errors})

    try:
        start_datetime, end_datetime, name, email, number_of_people = get_form_data(
            form.cleaned_data
        )

        if appointments_overlap(start_datetime, end_datetime, number_of_people)[0]:
            context["has_time_conflict"] = True
            return render(req, "create_event.html", context)

        start_datetime_formatted: str = start_datetime.strftime("%Y-%m-%dT%H:%M:%S%z")
        end_datetime_formatted: str = end_datetime.strftime("%Y-%m-%dT%H:%M:%S%z")

        location: str = appointments_overlap(
            start_datetime, end_datetime, number_of_people
        )[1]

        create_event(
            name,
            email,
            start_datetime_formatted,
            end_datetime_formatted,
            number_of_people,
            location,
        )
        return render(req, "success.html", {"message": "Event scheduled successfully"})
    except Exception as e:
        return handle_error(req, e, "process reservation form")
