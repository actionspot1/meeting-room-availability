from django import forms
from datetime import datetime, timedelta


class EventForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()

    start_datetime = forms.DateTimeField(
        label="Start Date and Time",
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
    )
    end_datetime = forms.DateTimeField(
        label="End Date and Time",
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
    )

    # def __init__(self, *args, **kwargs):
    #     super(EventForm, self).__init__(*args, **kwargs)

    # custom validation
    def clean(self):
        cleaned_data = super().clean()
        start_datetime = cleaned_data.get("start_datetime")
        end_datetime = cleaned_data.get("end_datetime")

        if start_datetime and end_datetime:
            if start_datetime >= end_datetime:
                raise forms.ValidationError("End time must be after start time.")
