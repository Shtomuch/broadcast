from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from django.utils.text import slugify
from uuid import uuid4

User = settings.AUTH_USER_MODEL

class ChatRoom(models.Model):
    name        = models.CharField(max_length=100)
    slug        = models.SlugField(unique=True, editable=False)
    host        = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_rooms")
    participants = models.ManyToManyField(User, related_name="chat_rooms", blank=True)
    is_private = models.BooleanField(default=False)
    password_hash = models.CharField(max_length=128, blank=True)  # ← нове поле

    def set_password(self, raw):
        self.password_hash = make_password(raw)

    def check_password(self, raw):
        return check_password(raw, self.password_hash)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{uuid4().hex[:6]}")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Message(models.Model):
    room      = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    author    = models.ForeignKey(User, on_delete=models.CASCADE)
    content   = models.TextField(blank=True)
    file      = models.FileField(upload_to="chat_files/", blank=True, null=True)
    created   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created"]
