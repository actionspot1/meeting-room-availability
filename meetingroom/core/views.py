from django.http import HttpResponse, HttpRequest
from django.shortcuts import render
from googleapiclient.errors import HttpError
from datetime import datetime
from typing import List, Tuple

from .utils import (
    get_appointments,
    is_current_time_between,
    handle_error,
    render_reservation_form,
    process_reservation_form,
)


def index(req: HttpRequest) -> HttpResponse:
    try:
        appointments: List[Tuple[datetime, datetime]] = get_appointments()
        is_available: bool = not (
            appointments and is_current_time_between(*appointments[0])
        )
        context: dict[str, bool] = {"is_available": is_available}
        return render(req, "index.html", context)
    except HttpError as error:
        return handle_error(req, error, "index")


def book_reservation(req: HttpRequest) -> HttpResponse:
    try:
        appointments: List[Tuple[datetime, datetime]] = get_appointments()
    except Exception as e:
        return handle_error(req, e, "book reservation")

    if req.method != "POST":
        return render_reservation_form(req)

    return process_reservation_form(req, appointments)
