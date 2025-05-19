from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class SignUpForm(UserCreationForm):
    email = forms.EmailField(label="Електронна пошта", required=True)
    first_name = forms.CharField(label="Ім'я", max_length=30, required=False)
    last_name = forms.CharField(label="Прізвище", max_length=30, required=False)
    department = forms.CharField(label="Відділ", max_length=100, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "department",
            "password1",
            "password2",
        )
        help_texts = {field: "" for field in fields}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "username": "Логін",
            "email": "example@example.com",
            "first_name": "Ім'я",
            "last_name": "Прізвище",
            "department": "Відділ",
            "password1": "Пароль",
            "password2": "Підтвердження паролю",
        }
        for name, field in self.fields.items():
            field.widget.attrs.update({
                "class": "input",
                "placeholder": placeholders.get(name, ""),
            })
            field.help_text = ""
