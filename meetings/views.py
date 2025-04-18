from django.conf import settings
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.exceptions import PermissionDenied

from .models import Meeting
from .forms import MeetingForm

class MeetingListView(LoginRequiredMixin, ListView):
    model = Meeting
    template_name = 'meetings/list.html'
    context_object_name = 'meetings'

    def get_queryset(self):
        user = self.request.user
        return Meeting.objects.filter(host=user) | Meeting.objects.filter(participants=user)

class MeetingCreateView(LoginRequiredMixin, CreateView):
    form_class = MeetingForm
    template_name = 'meetings/create.html'
    success_url = reverse_lazy('meetings:list')

    def form_valid(self, form):
        form.instance.host = self.request.user
        return super().form_valid(form)

class MeetingDetailView(LoginRequiredMixin, DetailView):
    model = Meeting
    template_name = 'meetings/detail.html'
    context_object_name = 'meeting'

class MeetingJoinView(LoginRequiredMixin, TemplateView):
    template_name = 'meetings/join.html'

    def dispatch(self, request, *args, **kwargs):
        # Завантажуємо зустріч
        meeting = get_object_or_404(Meeting, room_name=kwargs['slug'])
        # Перевірка: або ви — хост, або ви в participants
        is_participant = meeting.participants.filter(pk=request.user.pk).exists()
        if request.user != meeting.host and not is_participant:
            raise PermissionDenied("Ви не запрошені на цю зустріч.")
        # Все ок — зберігаємо meeting в атрибуті, щоб не діставати двічі
        self.meeting = meeting
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # беремо вже запопнене у dispatch
        ctx['meeting'] = self.meeting
        ctx['JITSI_DOMAIN'] = getattr(settings, 'JITSI_DOMAIN', 'meet.jit.si')
        return ctx
