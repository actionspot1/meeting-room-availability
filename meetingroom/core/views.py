from django.http import HttpResponse, HttpRequest
from django.shortcuts import render
from googleapiclient.errors import HttpError
from django.utils import timezone
from datetime import datetime, date, time
from typing import Optional

from .utils import *
from .forms import EventForm


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
        appointments: List[Tuple[datetime, datetime]] = get_appointments()
        business_hours, available_time_slots_formatted = get_reservation_info(
            appointments
        )
    except Exception as e:
        return handle_error(req, e)

    if req.method != "POST":
        return render_reservation_form(
            req, available_time_slots_formatted, business_hours
        )

    return process_reservation_form(
        req, available_time_slots_formatted, business_hours, appointments
    )
