from django import forms
from datetime import datetime, timedelta
from .utils.room_capacity_utils import LARGE_ROOM_MAX_CAPACITY
from django.utils import timezone


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


class UpdateEventForm(forms.Form):
    # name = forms.CharField(max_length=100, required=False)
    email = forms.EmailField(required=True)
    location = forms.CharField(max_length=100)

    number_of_people = forms.IntegerField(
        label=f"Number of People Attending - including yourself. Leave blank if unchanged. Max: {LARGE_ROOM_MAX_CAPACITY})",
        max_value=LARGE_ROOM_MAX_CAPACITY,
        required=False,
    )

    cur_start_datetime = forms.DateTimeField(
        label="Current Scheduled Start Date and Time",
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        # required=False,
        initial=datetime.now().replace(minute=0, second=0, microsecond=0)
        + timedelta(hours=1),
    )

    cur_end_datetime = forms.DateTimeField(
        label="Current Scheduled End Date and Time",
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        # required=False,
        initial=datetime.now().replace(minute=0, second=0, microsecond=0)
        + timedelta(hours=2),
    )

    new_start_datetime = forms.DateTimeField(
        label="New Start Date and Time",
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        required=True,
        initial=datetime.now().replace(minute=0, second=0, microsecond=0)
        + timedelta(hours=1),
    )

    new_end_datetime = forms.DateTimeField(
        label="New End Date and Time",
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        required=True,
        initial=datetime.now().replace(minute=0, second=0, microsecond=0)
        + timedelta(hours=2),
    )

    def clean(self):
        cleaned_data = super().clean()
        new_start_datetime = cleaned_data.get("new_start_datetime")
        new_end_datetime = cleaned_data.get("new_end_datetime")

        if new_start_datetime and new_end_datetime:
            if new_start_datetime >= new_end_datetime:
                raise forms.ValidationError(
                    "New end time must be after new start time."
                )
            if new_start_datetime < timezone.now():
                raise forms.ValidationError("New start time must be in the future.")
