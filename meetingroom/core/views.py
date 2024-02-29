from datetime import datetime, time

import os.path
from django.http import HttpResponse
from django.utils import timezone




from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

#from .utils.min_start_time import min_start_time
from django.shortcuts import render

def index(request):
    SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)
        # Call the Calendar API
        events = service.events()
        local_timezone = timezone.get_current_timezone()
        print(local_timezone)
        now = datetime.now(local_timezone)
        start_time = (now).isoformat()
        end_of_day = datetime.combine(now.date(), time(hour=23, minute=59, second=59)).astimezone(local_timezone).isoformat()
        print(start_time)
        print(end_of_day)
        events_result = (
            events.list(
                calendarId="primary",
                timeMin = start_time,
                timeMax = end_of_day,
            )
            .execute()
        )

        events_items = events_result.get("items", [])
        meetings = []
        for event in events_items:
            start = event['start']['dateTime']
            end = event['end']['dateTime']

            start_datetime = datetime.fromisoformat(start)
            end_datetime = datetime.fromisoformat(end)

            start_12hr = start_datetime.strftime("%#I:%M %p")
            end_12hr = end_datetime.strftime("%#I:%M %p")

            meetings.append([start_12hr, end_12hr])


        meetings.sort()
        print(meetings)

        return render(request, 'index.html', {'meetings': meetings})
        
        #next_booked_start_time = min_start_time(events)

        #return HttpResponse(events_items)

    except HttpError as error:
        print(f"An error occurred: {error}")
        return HttpResponse("An error occurred. Please try again later.", status=500)
    
