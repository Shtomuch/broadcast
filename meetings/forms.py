from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Meeting
from django.utils.timezone import now

User = get_user_model()


class MeetingForm(forms.ModelForm):
    scheduled_time = forms.DateTimeField(
        label="Заплановано на",
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M'
        )
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Встановлюємо мінімально допустимий час для scheduled_time на поточний час
        # Формат для атрибута 'min' у datetime-local: YYYY-MM-DDTHH:MM
        now_str = timezone.now().strftime('%Y-%m-%dT%H:%M')
        self.fields['scheduled_time'].widget.attrs['min'] = now_str

    def clean_scheduled_time(self):  # Більш специфічний метод clean_ для поля
        scheduled_time = self.cleaned_data.get('scheduled_time')

        if scheduled_time and scheduled_time <= timezone.now():
            raise forms.ValidationError("Дата та час зустрічі повинні бути пізнішими за поточний час.")

        return scheduled_time