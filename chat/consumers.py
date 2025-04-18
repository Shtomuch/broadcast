import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone
from .models import ChatRoom, Message
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.slug = self.scope["url_route"]["kwargs"]["slug"]
        self.room_group_name = f"chat_{self.slug}"

        # перевіряємо, що користувач має доступ
        self.room = await database_sync_to_async(ChatRoom.objects.get)(slug=self.slug)
        user = self.scope["user"]
        if not user.is_authenticated or (self.room.is_private and user not in await database_sync_to_async(lambda: self.room.participants.all())()):
            await self.close()
            return

        # додати до групи каналів
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        # вихід із групи
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg = data.get("message", "").strip()
        file_info = data.get("file")  # якщо будемо підключати файл via base64 / URL

        user = self.scope["user"]
        # зберігаємо в БД
        message = await database_sync_to_async(Message.objects.create)(
            room=self.room, user=user, content=msg
        )

        # розсилаємо всім у кімнаті
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": msg,
                "username": user.username,
                "timestamp": timezone.localtime(message.timestamp).strftime("%H:%M"),
                "attachment_url": None,
            }
        )

    async def chat_message(self, event):
        # надсилаємо json назад клієнту
        await self.send(text_data=json.dumps(event))
