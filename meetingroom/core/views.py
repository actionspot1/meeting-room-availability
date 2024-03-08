from django.http import HttpResponse, HttpRequest
from django.shortcuts import render
from googleapiclient.errors import HttpError
from django.utils import timezone
from datetime import datetime, date, time
from typing import Optional

from .utils import *
from .forms import EventForm


calendar_service: GoogleCalendarService = GoogleCalendarService()


def index(req: HttpRequest) -> HttpResponse:
    try:
        appointments = get_appointments(calendar_service)

        is_available: bool = not (
            appointments and is_current_time_between(*appointments[0])
        )

        context: dict[str, bool] = {"is_available": is_available}

        return render(req, "index.html", context)

    except HttpError as error:
        print(f"An error occurred: {error}")
        return HttpResponse("An error occurred. Please try again later.", status=500)


def book_reservation(req: HttpRequest) -> HttpResponse:
    try:
        appointments = get_appointments(calendar_service)
        business_hours: Tuple[time, time] = get_business_hours()

        available_time_slots = get_available_time_slots(appointments)

        available_time_slots_formatted = []
        print("available_time_slots")
        for time_slot in available_time_slots:
            start = time_slot[0].strftime("%#I:%M %p")
            end = time_slot[1].strftime("%#I:%M %p")

            available_time_slots_formatted.append([start, end])

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return HttpResponse(str(e), status=500)

    if req.method != "POST":
        form: EventForm = EventForm()
        context = {
            "form": form,
            "available_time_slots": available_time_slots_formatted,
            "business_hours": business_hours,
        }
        return render(req, "create_event.html", context)

    form: EventForm = EventForm(req.POST)
    context = {
        "form": form,
        "available_time_slots": available_time_slots_formatted,
        "business_hours": business_hours,
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

        today: date = date.today()
        start_datetime: datetime = timezone.make_aware(
            datetime.combine(today, start_time), timezone.get_current_timezone()
        )
        # print("start_datetime: ", start_datetime)
        end_datetime: datetime = timezone.make_aware(
            datetime.combine(today, end_time), timezone.get_current_timezone()
        )
        # print("end_datetime: ", end_datetime)

        start_datetime_formatted: str = start_datetime.strftime("%Y-%m-%dT%H:%M:%S%z")
        end_datetime_formatted: str = end_datetime.strftime("%Y-%m-%dT%H:%M:%S%z")

        start_time_formatted: str = start_time.strftime("%#I %M %p")
        end_time_formatted: str = end_time.strftime("%#I %M %p")

        # TODO: check if there is an overlap
        """
        1. need to compare with datetime objects => make sure we use datetimeobjects only, not strings
                                                 => create function for printing strings of datetime objects

        """
        if appointments:
            for time_slots in available_time_slots:
                if (
                    start_time < time_slots[0]
                    and end_time >= time_slots[0]
                    or time_slots[0] <= start_time < time_slots[1]
                ):
                    context["has_time_conflict"] = True
                    return render(req, "create_event.html", context)

        calendar_service.create_event(
            name, email, start_datetime_formatted, end_datetime_formatted
        )
        return render(req, "success.html", {"message": "Event scheduled successfully"})

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return HttpResponse(str(e), status=500)
