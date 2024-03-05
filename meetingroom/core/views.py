from django.http import HttpResponse, HttpRequest
from django.shortcuts import render
from googleapiclient.errors import HttpError
from .utils import *
from .forms import EventForm
from datetime import datetime, date, time
from typing import Optional

calendar_service: GoogleCalendarService = GoogleCalendarService()


def index(req: HttpRequest) -> HttpResponse:
    try:
        events_items: list = calendar_service.get_events()
        meetings: List[Tuple[datetime, datetime]] = get_sorted_meetings(events_items)
        print("booked meetings", meetings)

        is_available: bool = not (meetings and is_time_now_between(*meetings[0]))

        context: dict[str, bool] = {"is_available": is_available}

        return render(req, "index.html", context)

    except HttpError as error:
        print(f"An error occurred: {error}")
        return HttpResponse("An error occurred. Please try again later.", status=500)


def book_reservation(req: HttpRequest) -> HttpResponse:
    try:
        events_items: list = calendar_service.get_events()
        meetings: List[Tuple[datetime, datetime]] = get_sorted_meetings(events_items)
        print("booked meetings", meetings)

        available_times = []
        business_opening = "8 AM"
        for i in range(1, len(meetings)):
            prev_end = meetings[i - 1][1]
            curr_start = meetings[i][0]

            prev_end_12hr = prev_end.strftime("%#I:%M %p")
            curr_start_12hr = curr_start.strftime("%#I:%M %p")

            if prev_end >= curr_start:
                continue
            available_times.append([prev_end_12hr, curr_start_12hr])

        print(available_times)

        if not available_times and len(meetings) == 1:
            available_times = "the whole day is available"

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return HttpResponse(str(e), status=500)

    if req.method != "POST":
        form: EventForm = EventForm()
        context = {"form": form, "available_times": available_times}
        return render(req, "create_event.html", context)

    form: EventForm = EventForm(req.POST)
    context = {"form": form, "available_times": available_times}
    if not form.is_valid():
        return render(req, "create_event.html", context)

    name: str = form.cleaned_data.get("name", "")
    start_time_str: Optional[str] = form.cleaned_data.get("start_time")
    end_time_str: Optional[str] = form.cleaned_data.get("end_time")
    email: str = form.cleaned_data.get("email", "")

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
        start_datetime: datetime = datetime.combine(today, start_time)
        end_datetime: datetime = datetime.combine(today, end_time)

        start_formatted: str = start_datetime.strftime("%Y-%m-%dT%H:%M:%S%z")
        end_formatted: str = end_datetime.strftime("%Y-%m-%dT%H:%M:%S%z")

        if not all([name, start_time_str, end_time_str, email]):
            return render(req, "error.html", {"error_message": "Missing required data"})

        calendar_service.create_event(name, email, start_formatted, end_formatted)
        return render(req, "success.html", {"message": "Event scheduled successfully"})

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return HttpResponse(str(e), status=500)
