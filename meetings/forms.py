from django import forms
from django.contrib.auth import get_user_model
from .models import Meeting

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
