import json
from json import JSONDecodeError

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import ChatRoom, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.slug = self.scope["url_route"]["kwargs"]["slug"]
        self.room_group_name = f"chat_{self.slug}"

        self.room = await database_sync_to_async(ChatRoom.objects.get)(slug=self.slug)

        user = self.scope["user"]

        if not user.is_authenticated:
            await self.close()
            return

        if self.room.is_private:
            has_access = await database_sync_to_async(
                lambda: self.room.participants.filter(pk=user.pk).exists()
            )()
            if not has_access:
                await self.close()
                return

        # додати до групи каналів
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:  # <‑‑ пропускаємо ping/порожні
            return
        try:
            data = json.loads(text_data)
        except JSONDecodeError:
            # можна залогувати й проігнорувати
            return

        msg = await self._save_message(data.get("message", ""))
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "author": msg["author"],
                "content": msg["content"],
                "created": msg["created"],
                "file_url": msg.get("file_url", ""),
            },
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def _save_message(self, content, file=None):
        message = Message.objects.create(
            room=self.room,
            author=self.scope["user"],
            content=content,
            file=file,
        )
        return {
            "author": self.scope["user"].get_username(),
            "content": content,
            "created": message.created.strftime("%H:%M"),
            "file_url": message.file.url if message.file else "",
        }
