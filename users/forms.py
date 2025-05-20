# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
# Якщо ви плануєте перекладати власні повідомлення, використовуйте gettext_lazy
# from django.utils.translation import gettext_lazy as _

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
        ) # password1 and password2 додаються автоматично UserCreationForm
        # Якщо ви хочете змінити порядок, password1 та password2 можна додати сюди явно
        # fields = ("username", "email", "first_name", "last_name", "department", "password1", "password2")

        # Забираємо стандартні help_texts, якщо вони не потрібні або будуть замінені
        help_texts = {field_name: "" for field_name in fields}
        # Якщо вам потрібні кастомні повідомлення про помилки для полів UserCreationForm,
        # які не перекладаються автоматично:
        # error_messages = {
        #     'password2': {
        #         'password_mismatch': _("Паролі не співпадають."),
        #     },
        # }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "username": "Ваш логін",
            "email": "example@example.com",
            "first_name": "Ім'я",
            "last_name": "Прізвище",
            "department": "Назва відділу",
            "password1": "Введіть пароль",       # Плейсхолдер для поля пароля 1
            "password2": "Підтвердіть пароль",  # Плейсхолдер для поля пароля 2
        }

        # Поля password1 та password2 додаються UserCreationForm, тому ми звертаємось до self.fields
        # після виклику super().__init__()
        password_fields = ['password1', 'password2']
        for field_name in password_fields:
            if field_name in self.fields:
                self.fields[field_name].label = placeholders.get(field_name, '') # Змінюємо label, щоб використати текст з placeholders
                # Ви можете також оновити help_text тут, якщо це потрібно:
                # self.fields[field_name].help_text = _("Ваш пароль має містити...")


        for name, field in self.fields.items():
            # Формуємо класи для поля
            current_classes = field.widget.attrs.get("class", "")
            new_classes = "form-control" # Стандартний клас Bootstrap
            if self.errors.get(name):
                new_classes += " is-invalid" # Додаємо клас, якщо поле має помилки

            field.widget.attrs.update({
                "class": new_classes,
                "placeholder": placeholders.get(name, field.label), # Використовуємо label як запасний варіант
            })
            # Ви вже очистили help_text через Meta.help_texts, але якщо потрібно індивідуально:
            # field.help_text = ""