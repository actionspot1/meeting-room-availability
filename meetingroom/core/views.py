from django.http import HttpResponse, HttpRequest
from django.shortcuts import render
from googleapiclient.errors import HttpError
from datetime import datetime
from typing import List, Tuple
from .forms import UpdateEventForm

from .utils import (
    get_appointments,
    is_current_time_between,
    handle_error,
    render_reservation_form,
    process_reservation_form,
)


def index(req: HttpRequest) -> HttpResponse:
    try:
        appointments: List[Tuple[datetime, datetime, int, str, str, str]] = (
            get_appointments()
        )
        is_available: bool = not (
            appointments
            and is_current_time_between(appointments[0][0], appointments[0][1])
        )
        context: dict[str, bool] = {"is_available": is_available}
        return render(req, "index.html", context)
    except HttpError as error:
        return handle_error(req, error, "index")


def book_reservation(req: HttpRequest) -> HttpResponse:

    if req.method != "POST":
        return render_reservation_form(req)

    return process_reservation_form(req)


def reschedule(req: HttpRequest) -> HttpResponse:
    if req.method != "POST":
        return render(req, "update_event.html", {"form": UpdateEventForm})

    form: UpdateEventForm = UpdateEventForm(req.POST)
    if not form.is_valid():
        return render(req, "update_event.html", {"form": form})
