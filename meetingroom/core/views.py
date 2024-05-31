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
    appointments_overlap,
    update_event,
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

    (
        email,
        location,
        number_of_people,
        cur_start_datetime,
        cur_end_datetime,
        new_start_datetime,
        new_end_datetime,
    ) = (
        form.cleaned_data.get("email", ""),
        form.cleaned_data.get("location"),
        form.cleaned_data.get("number_of_people"),
        form.cleaned_data.get("cur_start_datetime"),
        form.cleaned_data.get("cur_end_datetime"),
        form.cleaned_data.get("new_start_datetime"),
        form.cleaned_data.get("new_end_datetime"),
    )
    print(
        email,
        location,
        number_of_people,
        cur_start_datetime,
        cur_end_datetime,
        new_start_datetime,
        new_end_datetime,
    )
    if not all(
        [
            email,
            location,
            # number_of_people,
            cur_start_datetime,
            cur_end_datetime,
            new_start_datetime,
            new_end_datetime,
        ]
    ):
        return render(req, "error.html", {"error_message": "missing required data"})

    try:
        appointments: List[Tuple[datetime, datetime, int, str, str, str]] = (
            get_appointments()
        )
        event_id: str = ""
        for (
            event_start_datetime,
            event_end_datetime,
            additional_guests,
            location_summary,
            event_email,
            app_event_id,
        ) in appointments:
            if (
                email == event_email
                and cur_start_datetime == event_start_datetime
                and cur_end_datetime == event_end_datetime
                and location.lower() == location_summary.lower()
            ):
                event_id = app_event_id
                if number_of_people is None:
                    number_of_people = additional_guests + 1
                break
        print("number of people", number_of_people)
        if event_id == "":
            return render(req, "error.html", {"error_message": "schedule not found"})
        print("event id", event_id)

        has_overlap, new_location = appointments_overlap(
            new_start_datetime, new_end_datetime, number_of_people, event_id
        )
        print("location", new_location)
        if has_overlap:
            return render(req, "update_event.html", {"has_time_conflict": True})

        new_start_datetime_formatted: str = new_start_datetime.strftime(
            "%Y-%m-%dT%H:%M:%S%z"
        )
        new_end_datetime_formatted: str = new_end_datetime.strftime(
            "%Y-%m-%dT%H:%M:%S%z"
        )
        update_event(
            event_id,
            new_start_datetime_formatted,
            new_end_datetime_formatted,
            number_of_people,
            new_location,
        )
        return render(req, "success.html", {"message": "Event scheduled successfully"})

    except Exception as e:
        return handle_error(req, e, "reschedule")
