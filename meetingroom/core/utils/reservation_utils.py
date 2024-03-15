from .google_calendar_utils import (
    get_business_hours,
    get_available_time_slots,
    format_time_slots,
    get_current_time,
    appointments_overlap,
    create_event,
    get_aware_datetime_objects,
)
from datetime import time, datetime, date
from typing import List, Tuple, Optional
from django.http import HttpResponse, HttpRequest
from ..forms import EventForm
from django.shortcuts import render
from .utils import handle_error


def get_reservation_info(
    appointments: List[Tuple[time, time]]
) -> Tuple[Tuple[time, time], List[str]]:
    business_hours = get_business_hours()
    available_time_slots = get_available_time_slots(appointments)
    available_time_slots_formatted = format_time_slots(available_time_slots)
    return business_hours, available_time_slots_formatted


def render_reservation_form(
    req: HttpRequest,
    available_time_slots_formatted: List[str],
    business_hours: Tuple[time, time],
) -> HttpResponse:
    context = {
        "form": EventForm(),
        "available_time_slots": available_time_slots_formatted,
        "business_hours": business_hours,
        "now": get_current_time(),
    }
    return render(req, "create_event.html", context)


def validate_form_data(form_data: dict) -> Optional[str]:
    name, start_datetime_str, end_datetime_str, email = (
        form_data.get("name", ""),
        form_data.get("start_datetime"),
        form_data.get("end_datetime"),
        form_data.get("email", ""),
    )
    if not all([name, start_datetime_str, end_datetime_str, email]):
        return "Missing required data"
    return None


def get_form_data(form_data: dict) -> Tuple[time, time, str, str]:
    start_datetime = (
        datetime.strptime(form_data["start_datetime"], "%H:%M").time()
        if form_data["start_datetime"]
        else time()
    )
    end_datetime = (
        datetime.strptime(form_data["end_datetime"], "%H:%M").time()
        if form_data["end_datetime"]
        else time()
    )
    name, email = form_data.get("name", ""), form_data.get("email", "")
    return start_datetime, end_datetime, name, email


def process_reservation_form(
    req: HttpRequest,
    available_time_slots_formatted: List[str],
    business_hours: Tuple[time, time],
    appointments: List[Tuple[time, time]],
) -> HttpResponse:
    form = EventForm(req.POST)
    context = {
        "form": form,
        "available_time_slots": available_time_slots_formatted,
        "business_hours": business_hours,
        "now": get_current_time(),
    }

    if not form.is_valid():
        return render(req, "create_event.html", context)

    errors = validate_form_data(form.cleaned_data)
    if errors:
        return render(req, "error.html", {"error message": errors})

    try:
        start_datetime, end_datetime, name, email = get_form_data(form.cleaned_data)

        if appointments_overlap(start_datetime, end_datetime, appointments):
            context["has_time_conflict"] = True
            return render(req, "create_event.html", context)

        # start_datetime, end_datetime = get_aware_datetime_objects(
        #     date.today(), start_datetime, end_datetime
        # )

        start_datetime_formatted = start_datetime.strftime("%Y-%m-%dT%H:%M:%S%z")
        end_datetime_formatted = end_datetime.strftime("%Y-%m-%dT%H:%M:%S%z")

        create_event(name, email, start_datetime_formatted, end_datetime_formatted)
        return render(req, "success.html", {"message": "Event scheduled successfully"})
    except Exception as e:
        return handle_error(req, e)
