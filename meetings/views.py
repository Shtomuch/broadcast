from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, CreateView, DetailView, UpdateView, View, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model

from .models import Meeting
from .forms import MeetingForm

User = get_user_model()

class MeetingListView(LoginRequiredMixin, ListView):
    """Показуємо тільки ті зустрічі, які створив сам користувач."""
    model = Meeting
    template_name = 'meetings/list.html'
    context_object_name = 'meetings'

    def get_queryset(self):
        return Meeting.objects.filter(host=self.request.user)


class MeetingCreateView(LoginRequiredMixin, CreateView):
    """Створення нової зустрічі."""
    form_class = MeetingForm
    template_name = 'meetings/create.html'
    success_url = reverse_lazy('meetings:list')

    def form_valid(self, form):
        form.instance.host = self.request.user
        return super().form_valid(form)


class MeetingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редагування зустрічі."""
    model = Meeting
    form_class = MeetingForm
    template_name = 'meetings/update.html'
    context_object_name = 'meeting'
    slug_field = 'room_name'
    slug_url_kwarg = 'slug'

    def test_func(self):
        # лише хост може редагувати
        return self.get_object().host == self.request.user


class MeetingDetailView(LoginRequiredMixin, DetailView):
    """Перегляд деталей зустрічі."""
    model = Meeting
    template_name = 'meetings/detail.html'
    context_object_name = 'meeting'

    def get_object(self, queryset=None):
        return get_object_or_404(Meeting, room_name=self.kwargs['slug'])


class MeetingDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Meeting
    template_name = 'meetings/confirm_delete.html'
    slug_field = 'room_name'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('meetings:list')

    def test_func(self):
        return self.get_object().host == self.request.user


class MeetingJoinView(View):
    """Opens the Jitsi meeting in an embedded page."""

    def get(self, request, slug):
        meeting = get_object_or_404(Meeting, room_name=slug)
        if request.user.is_authenticated and request.user != meeting.host \
           and not meeting.participants.filter(pk=request.user.pk).exists():
            meeting.participants.add(request.user)
        return render(request, 'meetings/jitsi.html', {
            'meeting': meeting,
            'jitsi_domain': settings.JITSI_DOMAIN,
        })
