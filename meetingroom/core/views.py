from datetime import datetime, time
from django.http import HttpResponse
from django.utils import timezone

from googleapiclient.errors import HttpError

from django.shortcuts import render
from .utils import *
from .forms import EventForm


calendar_service = GoogleCalendarService()


def index(req):

    try:

        events_items = calendar_service.get_events()
        meetings = get_sorted_meetings(events_items)
        print("booked meetings", meetings)

        is_available: bool = not (meetings and is_time_now_between(*meetings[0]))

        context = {"is_available": is_available}

        return render(req, "index.html", context)

    except HttpError as error:
        print(f"An error occurred: {error}")
        return HttpResponse("An error occurred. Please try again later.", status=500)


def book_reservation(req):
    # if not (req.end and req.start and req.organizer.displayName and req.organizer.email):
    #     return HttpResponse("Send all required fields: start, end, name, and email.", status=400)
    if req.method != "POST":
        form = EventForm()
        return render(req, "create_event.html", {"form": form})

    form = EventForm(req.POST)
    if not form.is_valid():
        return render(req, "create_event.html", {"form": form})

    name = form.cleaned_data["name"]
    start_time = form.cleaned_data["start_time"].isoformat()
    end_time = form.cleaned_data["end_time"].isoformat()
    email = form.cleaned_data["email"]

    if not all([name, start_time, end_time, email]):
        return render(req, "error.html", {"error_message": "Missing required data"})

    try:
        calendar_service.create_event(name, email, start_time, end_time)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return HttpResponse(e, status=500)
