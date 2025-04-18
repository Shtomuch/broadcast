from django.contrib import admin
from .models import ChatRoom, Message

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_private", "created_at")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("participants",)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("room", "user", "timestamp", "short_content")
    readonly_fields = ("timestamp",)

    def short_content(self, obj):
        return obj.content[:40] or obj.attachment.name
    short_content.short_description = "Повідомлення"
