from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth import exceptions

from django.utils import timezone
from datetime import datetime, time
import os.path


class GoogleCalendarService:
    _instance = None

    SCOPES = ["https://www.googleapis.com/auth/calendar"]

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.service = cls._instance.authenticate()
        return cls._instance

    def authenticate(self):
        creds = self.load_credentials(self.SCOPES)

        if not creds or not creds.valid:
            creds = self.refresh_credentials(creds)

        return build("calendar", "v3", credentials=creds) if creds else None

    def load_credentials(self, scopes: list):
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", scopes)
        return creds

    def refresh_credentials(self, creds):
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            creds = self.run_local_server()
            self.save_credentials(creds)
        return creds

    def run_local_server(self):
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", self.SCOPES
        )
        return flow.run_local_server(port=0)

    def save_credentials(self, creds):
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    def create_event(self, name: str, email: str, start_time: str, end_time: str):
        if not self.service or not all([name, email, start_time, end_time]):
            print("Google Calendar API authentication failed or missing parameters.")
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
            return []

        try:
            local_timezone = timezone.get_current_timezone()
            now: datetime = datetime.now(local_timezone)
            start_time: str = now.isoformat()
            end_of_day: str = (
                datetime.combine(now.date(), time(hour=23, minute=59, second=59))
                .astimezone(local_timezone)
                .isoformat()
            )
            events_result = self.list_events(start_time, end_of_day)

            events_items = events_result.get("items", [])
            return events_items

        except exceptions.GoogleAuthError as auth_error:
            print(f"Google Authentication Error: {auth_error}")
            return []

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            print("get event")
            return []

    def list_events(self, start_time: str, end_time: str):
        events = self.service.events()
        return events.list(
            calendarId="primary", timeMin=start_time, timeMax=end_time
        ).execute()
