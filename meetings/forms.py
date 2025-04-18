from django import forms
from .models import Meeting

class MeetingForm(forms.ModelForm):
    scheduled_time = forms.DateTimeField(
        label="Заплановано на",
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )

    class Meta:
        model = Meeting
        fields = [
            'title', 'description', 'scheduled_time',
            'duration', 'participants', 'recording_enabled'
        ]
