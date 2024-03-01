from datetime import datetime, time
from django.http import HttpResponse
from django.utils import timezone


from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from django.shortcuts import render
from .forms import EventForm
from .utils.google_calendar_service import GoogleCalendarService


def index(req):

    try:

        calendar_service = GoogleCalendarService()
        events_items = calendar_service.get_events()
        meetings = []
        for event in events_items:
            start: str = event["start"]["dateTime"]
            end = event["end"]["dateTime"]

            start_datetime = datetime.fromisoformat(start)
            end_datetime = datetime.fromisoformat(end)

            # start_12hr = start_datetime.strftime("%#I:%M %p")
            # end_12hr = end_datetime.strftime("%#I:%M %p")
            # meetings.append([start_12hr, end_12hr])

            meetings.append([start_datetime, end_datetime])

        meetings.sort()
        print("booked meetings", meetings)

        is_available: bool = True
        local_timezone = timezone.get_current_timezone()
        now = datetime.now(local_timezone)
        if meetings and meetings[0][0] <= now <= meetings[0][1]:
            is_available = False

        context = {"is_available": is_available}

        return render(req, "index.html", context)

    except HttpError as error:
        print(f"An error occurred: {error}")
        return HttpResponse("An error occurred. Please try again later.", status=500)


# def book_reservation(req):
#     # if not (req.end and req.start and req.organizer.displayName and req.organizer.email):
#     #     return HttpResponse("Send all required fields: start, end, name, and email.", status=400)
#     if req.method != "POST":
#         form = EventForm()
#         return render(req, "create_event.html", {"form": form})

#     form = EventForm(req.POST)
#     if not form.is_valid():
#         return render(req, "create_event.html", {"form": form})

#     name = form.cleaned_data["name"]
#     start_time = form.cleaned_data["start_time"].isoformat()
#     end_time = form.cleaned_data["end_time"].isoformat()
#     email = form.cleaned_data["email"]

#     if not all([name, start_time, end_time, email]):
#         return render(req, "error.html", {"error_message": "Missing required data"})

#     try:
#         create_event_in_google_calendar(name, email, start_time, end_time)

#     except Exception as e:
#         print(f"An error occurred: {str(e)}")
#         return HttpResponse(e, status=500)
