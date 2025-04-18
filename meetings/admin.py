from django.contrib import admin
from .models import Meeting

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('title', 'host', 'scheduled_time', 'duration', 'recording_enabled')
    list_filter = ('recording_enabled',)
    filter_horizontal = ('participants',)
    prepopulated_fields = {'room_name': ('title',)}
