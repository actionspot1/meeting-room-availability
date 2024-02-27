from django.http import HttpResponse
from datetime import datetime, date, timedelta
from django.utils import timezone

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

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
        local_timezone = timezone.get_current_timezone()
        print(local_timezone)
        now = datetime.datetime.now(local_timezone)
        start_time = (now).isoformat()
        end_of_day = datetime.datetime.combine(now.date(), datetime.time(hour=23, minute=59, second=59)).astimezone(local_timezone).isoformat()
        print(start_time)
        print(end_of_day)
        events_result = (
            service.events().list(
                calendarId="primary",
                timeMin = start_time,
                timeMax = end_of_day
            )
            .execute()
        )
        events = events_result.get("items", [])
        print(events)
        # print(events[1]['start'])
        # print(events[1]['end'])

        if not events:
            return HttpResponse("Available")

        # Prints the start and name of the next 10 events
        # for event in events:
        #     start = event["start"].get("dateTime", event["start"].get("date"))
        #     print(start, event["summary"])
        return HttpResponse(events)

    except HttpError as error:
        print(f"An error occurred: {error}")
        return HttpResponse("An error occurred. Please try again later.", status=500)