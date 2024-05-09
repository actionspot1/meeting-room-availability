from django import forms
from datetime import datetime, timedelta
from .utils.room_capacity_utils import LARGE_ROOM_MAX_CAPACITY


class EventForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()

    number_of_people = forms.IntegerField(
        label="Number of People Attending - including yourself (Max: 10)",
        min_value=1,
        max_value=LARGE_ROOM_MAX_CAPACITY,
        initial=1,
    )

    start_datetime = forms.DateTimeField(
        label="Start Date and Time",
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        initial=datetime.now().replace(minute=0, second=0) + timedelta(hours=1),
    )
    end_datetime = forms.DateTimeField(
        label="End Date and Time",
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        initial=datetime.now().replace(minute=0, second=0) + timedelta(hours=2),
    )

    def clean(self):
        cleaned_data = super().clean()
        start_datetime = cleaned_data.get("start_datetime")
        end_datetime = cleaned_data.get("end_datetime")

        if start_datetime and end_datetime:
            if start_datetime >= end_datetime:
                raise forms.ValidationError("End time must be after start time.")
