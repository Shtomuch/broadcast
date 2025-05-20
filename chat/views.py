from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import redirect_to_login
from django.db import models
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, CreateView, TemplateView, View, DeleteView, FormView
)
from django.http import HttpResponseForbidden, JsonResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .forms import ChatRoomForm, PasswordForm
from .models import ChatRoom, Message

class RoomListView(LoginRequiredMixin, ListView):
    model = ChatRoom
    template_name = "chat/rooms_list.html"
    context_object_name = "rooms"

    def get_queryset(self):
        u = self.request.user
        return ChatRoom.objects.filter(
            models.Q(host=u) | models.Q(participants=u)
        ).distinct().order_by("name")

class RoomCreateView(LoginRequiredMixin, CreateView):
    model = ChatRoom
    form_class = ChatRoomForm            # ← було fields = [...]
    template_name = "chat/room_create.html"
    success_url = reverse_lazy("chat:rooms")


    def form_valid(self, form):
        form.instance.host = self.request.user
        response = super().form_valid(form)
        if form.instance.is_private:
            form.instance.participants.add(self.request.user)
        return response

class RoomJoinView(TemplateView):
    template_name = "chat/room_detail.html"

    def dispatch(self, request, *args, **kwargs):
        self.room = get_object_or_404(ChatRoom, slug=kwargs["slug"])
        user = request.user

        # 1) приватна — спочатку питаємо пароль
        if self.room.is_private:
            if not request.session.get(f"room_pass_{self.room.pk}"):
                return redirect("chat:pwd_prompt", slug=self.room.slug)

        # 2) додаємо в participants, якщо залогінений
        if user.is_authenticated and not self.room.participants.filter(pk=user.pk).exists():
            self.room.participants.add(user)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["room"] = self.room
        return ctx

class LeaveRoomView(LoginRequiredMixin, View):
    def post(self, request, slug):
        room = get_object_or_404(ChatRoom, slug=slug)
        room.participants.remove(request.user)
        return redirect("chat:rooms")


class RoomPasswordView(LoginRequiredMixin, FormView):
    template_name = "chat/room_password.html"
    form_class    = PasswordForm

    def dispatch(self, request, *args, **kwargs):
        # Отримуємо кімнату, щоб перевіряти пароль і додавати в participants
        self.room = get_object_or_404(ChatRoom, slug=kwargs["slug"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Перевіряємо пароль
        raw = form.cleaned_data["password"]
        if self.room.check_password(raw):
            # Запам’ятовуємо в сесії, щоб не питати знову
            self.request.session[f"room_pass_{self.room.pk}"] = True
            # Додаємо користувача до списку учасників
            self.room.participants.add(self.request.user)
            # Переходимо до самої кімнати
            return redirect("chat:join", slug=self.room.slug)

        # Якщо невірний — повертаємо форму з помилкою
        form.add_error("password", "Невірний пароль")
        return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "room": self.room,
        }
class RoomDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = ChatRoom
    template_name = "chat/room_confirm_delete.html"
    success_url = reverse_lazy("chat:rooms")

    def test_func(self):
        # тільки власник (host) може видаляти
        return self.get_object().host == self.request.user


class FileUploadView(LoginRequiredMixin, View):
    def post(self, request, slug):
        room = get_object_or_404(ChatRoom, slug=slug)
        if room.is_private and request.user not in room.participants.all() and room.host != request.user:
            return HttpResponseForbidden()
        file = request.FILES.get("file")
        content = request.POST.get("content", "")
        if not file and not content:
            return HttpResponseForbidden()
        msg = Message.objects.create(room=room, author=request.user, content=content, file=file)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"chat_{room.slug}",
            {
                "type": "chat_message",
                "author": msg.author.username,
                "content": msg.content,
                "file_url": msg.file.url if msg.file else "",
                "created": msg.created.strftime("%H:%M"),
            },
        )
        return JsonResponse({
            "author": msg.author.username,
            "content": msg.content,
            "file_url": msg.file.url if msg.file else "",
            "created": msg.created.strftime("%H:%M"),
        })



