from django import forms
from .models import ChatRoom

class ChatRoomForm(forms.ModelForm):
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="Пароль (лише для приватної кімнати)",
    )

    class Meta:
        model = ChatRoom
        fields = ["name", "is_private", "password"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "is_private": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def save(self, commit=True):
        room = super().save(commit=False)
        if room.is_private and self.cleaned_data["password"]:
            room.set_password(self.cleaned_data["password"])
        if commit:
            room.save()
            self.save_m2m()
        return room

class PasswordForm(forms.Form):
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'current-password',
        })
    )