from django import forms
from django.contrib.auth import get_user_model
from .models import Meeting
from django.utils import timezone

User = get_user_model()

class MeetingForm(forms.ModelForm):


    scheduled_time = forms.DateTimeField(
        label="Заплановано на",
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )

    class Meta:
        model = Meeting
        fields = [
            'title',
            'description',
            'scheduled_time',
            'duration',
            'recording_enabled',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        scheduled_time = cleaned_data.get('scheduled_time')

        if scheduled_time and scheduled_time <= timezone.now():
            raise forms.ValidationError("The meeting date and time must be later than the current time.")

        return cleaned_data

