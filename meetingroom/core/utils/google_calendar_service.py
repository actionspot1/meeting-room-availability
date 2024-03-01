from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth import exceptions

from django.utils import timezone
from datetime import datetime, time
import os.path


class GoogleCalendarService:

    def __init__(self):
        self.service = self.authenticate()

    def authenticate(self):
        SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open("token.json", "w") as token:
                    token.write(creds.to_json())
        return build("calendar", "v3", credentials=creds)

    def create_event(self, name: str, email: str, start_time: str, end_time: str):
        if not self.service:
            print("Google Calendar API authentication failed.")
            return

        if not all(
            [
                name,
                email,
                start_time,
                end_time,
            ]
        ):
            print("Missing required parameters.")
            return

        try:
            event = {
                "start": {"dateTime": start_time, "timeZone": "America/Los_Angeles"},
                "end": {"dateTime": end_time, "timeZone": "America/Los_Angeles"},
                "attendees": [{"displayName": name, "email": email}],
            }
            self.service.events().insert(calendarId="primary", body=event).execute()

        except exceptions.GoogleAuthError as auth_error:
            print(f"Google Authentication Error: {auth_error}")

        except Exception as e:
            print(f"An error occurred: {str(e)}")

    def get_events(self):
        if not self.service:
            print("Google Calendar API authentication failed.")
            return None

        try:
            events = self.service.events()
            local_timezone = timezone.get_current_timezone()
            print(local_timezone)
            now = datetime.now(local_timezone)
            start_time = (now).isoformat()
            end_of_day = (
                datetime.combine(now.date(), time(hour=23, minute=59, second=59))
                .astimezone(local_timezone)
                .isoformat()
            )
            print(start_time)
            print(end_of_day)
            events_result = events.list(
                calendarId="primary",
                timeMin=start_time,
                timeMax=end_of_day,
            ).execute()

            events_items = events_result.get("items", [])
            return events_items

        except exceptions.GoogleAuthError as auth_error:
            print(f"Google Authentication Error: {auth_error}")
            return None

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return None
