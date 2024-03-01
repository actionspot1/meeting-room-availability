# meeting-room-availability
This is based in Django and requires google cloud. This project checks if a calendar event is currently in progress. If it is, a message will display saying unavailable. Otherwise, a message will display saying available.

1. Install a virtual environment using `pip install virtualenv`
2. Type this command `python -m venv /path/to/new/virtual/environment` (https://docs.python.org/3/library/venv.html)
3. Install django by following this guide: https://www.djangoproject.com/download/
4. follow this guide to obtain a credentials.json file: https://developers.google.com/calendar/api/quickstart/python (read everything up to Install the Google client library)
5. run python manage.py runserver
6. add some events onto google calendar with the account you used for google cloud.
7. launch localhost:8000
