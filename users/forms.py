from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class SignUpForm(UserCreationForm):
    email = forms.EmailField(label="Електронна пошта", required=True)
    first_name = forms.CharField(label="Ім'я", max_length=30, required=False)
    last_name = forms.CharField(label="Прізвище", max_length=30, required=False)
    department = forms.CharField(label="Відділ", max_length=100, required=False)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name',
            'department', 'password1', 'password2'
        )
