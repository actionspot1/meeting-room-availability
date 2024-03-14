from django.http import HttpResponse, HttpRequest
from django.shortcuts import render
from googleapiclient.errors import HttpError
from django.utils import timezone
from datetime import datetime, date, time
from typing import Optional

from .utils import *
from .forms import EventForm


def handle_error(
    req: HttpRequest, error: Exception, status_code: int = 500
) -> HttpResponse:
    print(f"An error occurred: {str(error)}")
    return HttpResponse(str(error), status=status_code)


def index(req: HttpRequest) -> HttpResponse:
    try:
        appointments = get_appointments()
        is_available: bool = not (
            appointments and is_current_time_between(*appointments[0])
        )
        context: dict[str, bool] = {"is_available": is_available}
        return render(req, "index.html", context)
    except HttpError as error:
        return handle_error(req, error)


def book_reservation(req: HttpRequest) -> HttpResponse:
    try:
        appointments = get_appointments()
        business_hours: Tuple[time, time] = get_business_hours()
        available_time_slots = get_available_time_slots(appointments)
        available_time_slots_formatted = format_time_slots(available_time_slots)
    except Exception as e:
        return handle_error(req, e)

    if req.method != "POST":
        form: EventForm = EventForm()
        context = {
            "form": form,
            "available_time_slots": available_time_slots_formatted,
            "business_hours": business_hours,
            "now": get_current_time(),
        }
        return render(req, "create_event.html", context)

    form: EventForm = EventForm(req.POST)
    context = {
        "form": form,
        "available_time_slots": available_time_slots_formatted,
        "business_hours": business_hours,
        "now": get_current_time(),
    }

    if not form.is_valid():
        return render(req, "create_event.html", context)

    name: str = form.cleaned_data.get("name", "")
    start_time_str: Optional[str] = form.cleaned_data.get("start_time")
    end_time_str: Optional[str] = form.cleaned_data.get("end_time")
    email: str = form.cleaned_data.get("email", "")

    if not all([name, start_time_str, end_time_str, email]):
        return render(req, "error.html", {"error_message": "Missing required data"})

    try:
        start_time: time = (
            datetime.strptime(start_time_str, "%H:%M").time()
            if start_time_str
            else time()
        )
        end_time: time = (
            datetime.strptime(end_time_str, "%H:%M").time() if end_time_str else time()
        )

        start_datetime, end_datetime = get_aware_datetime_objects(
            date.today(), start_time, end_time
        )

        start_datetime_formatted: str = start_datetime.strftime("%Y-%m-%dT%H:%M:%S%z")
        end_datetime_formatted: str = end_datetime.strftime("%Y-%m-%dT%H:%M:%S%z")

        if appointments_overlap(start_time, end_time, appointments):
            context["has_time_conflict"] = True
            return render(req, "create_event.html", context)

        create_event(name, email, start_datetime_formatted, end_datetime_formatted)
        return render(req, "success.html", {"message": "Event scheduled successfully"})
    except Exception as e:
        return handle_error(req, e)
