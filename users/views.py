from django.contrib import messages  # Для сповіщень
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView  # Додано UpdateView

from .forms import SignUpForm, UserProfileEditForm  # Додано UserProfileEditForm
from .models import User  # Переконайтесь, що модель User імпортовано


class UserSignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'users/signup.html'
    success_url = reverse_lazy('users:login')


class UserLoginView(LoginView):
    template_name = 'users/login.html'


class UserLogoutView(LogoutView):
    next_page = reverse_lazy('users:login')


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile.html'


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile.html'
    # Додатковий контекст не потрібен, оскільки user доступний у шаблоні через request


class UserProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileEditForm
    template_name = 'users/profile_edit.html'  # Новий шаблон для редагування
    success_url = reverse_lazy('users:profile')  # Куди перенаправити після успішного оновлення

    def get_object(self, queryset=None):
        # Користувач може редагувати лише власний профіль
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Ваш профіль було успішно оновлено!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Будь ласка, виправте помилки у формі.')
        return super().form_invalid(form)
