from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotAllowed, JsonResponse
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.generics import get_object_or_404

from .models import ChatRoom, Message


class RoomListView(LoginRequiredMixin, ListView):
    model = ChatRoom
    template_name = "chat/room.html"
    context_object_name = "rooms"

    def get_queryset(self):
        qs = super().get_queryset().filter(
            is_private=False
        ) | self.request.user.chatrooms.all()
        return qs.distinct()


class RoomDetailView(LoginRequiredMixin, DetailView):
    model = ChatRoom
    template_name = "chat/room_detail.html"
    context_object_name = "room"

    def get_queryset(self):
        # доступ в приватні кімнати тільки учасникам
        qs = super().get_queryset()
        if not self.request.user.is_superuser:
            qs = qs.filter(
                is_private=False
            ) | qs.filter(participants=self.request.user)
        return qs.distinct()

@login_required
def upload_attachment(request, slug):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    room = get_object_or_404(ChatRoom, slug=slug)
    # доступ до приватних кімнат
    if room.is_private and request.user not in room.participants.all():
        return JsonResponse({'error': 'Forbidden'}, status=403)

    upload = request.FILES.get('file')
    if not upload:
        return JsonResponse({'error': 'No file uploaded'}, status=400)

    # створюємо запис в БД з attachment
    message = Message.objects.create(
        room=room,
        user=request.user,
        content='',             # тексту немає
        attachment=upload
    )

    # готуємо подію для WebSocket‑групи
    timestamp = timezone.localtime(message.timestamp).strftime("%H:%M")
    event = {
        'type': 'chat_message',      # обробляє ChatConsumer.chat_message
        'message': '',               # без тексту
        'username': request.user.username,
        'timestamp': timestamp,
        'attachment_url': message.attachment.url,
    }

    # відсилаємо всім учасникам кімнати через channel layer
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"chat_{slug}",
        event
    )

    # повертаємо JSON з URL і метаданими
    return JsonResponse({
        'attachment_url': message.attachment.url,
        'username': request.user.username,
        'timestamp': timestamp,
    })