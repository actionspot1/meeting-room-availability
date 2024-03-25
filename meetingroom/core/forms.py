from django import forms
from datetime import datetime, timedelta


class EventForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    # start_time = forms.TimeField(label="Start Time")
    # end_time = forms.TimeField(label="End Time")

    # timefield
    # def clean(self):
    #     cleaned_data = super().clean()
    #     start_time = cleaned_data.get("start_time")
    #     end_time = cleaned_data.get("end_time")

    #     if start_time and end_time and start_time >= end_time:
    #         raise forms.ValidationError("End time must be after start time.")

    start_time = forms.ChoiceField(choices=(), label="Start Time")
    end_time = forms.ChoiceField(choices=(), label="End Time")

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.fields["start_time"].choices = self.get_time_choices()
        self.fields["end_time"].choices = self.get_time_choices()

    def get_time_choices(self):
        # Generate a list of tuples where each tuple has a 24-hour format value and a 12-hour format label
        choices = []
        current_time = datetime.strptime("08:00", "%H:%M")
        while current_time <= datetime.strptime("23:45", "%H:%M"):
            time_value = current_time.strftime("%H:%M")  # 24-hour format
            label = current_time.strftime("%I:%M %p")  # 12-hour format
            choices.append((time_value, label))
            current_time += timedelta(minutes=15)
        return choices

    # customfield
    def clean(self):
        cleaned_data = super().clean()
        start_time = datetime.strptime(cleaned_data.get("start_time"), "%H:%M").time()
        end_time = datetime.strptime(cleaned_data.get("end_time"), "%H:%M").time()

        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("End time must be after start time.")
