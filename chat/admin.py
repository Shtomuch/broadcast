# chat/admin.py
from django.contrib import admin
from .models import ChatRoom, Message

@admin.register(ChatRoom)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("name", "is_private", "host")

admin.site.register(Message)
