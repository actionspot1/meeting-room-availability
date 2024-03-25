from datetime import datetime
from django.utils import timezone


def get_current_datetime():
    return datetime.now(timezone.get_current_timezone())
