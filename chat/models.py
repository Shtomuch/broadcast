import uuid
from django.conf import settings
from django.db import models
from django.urls import reverse

User = settings.AUTH_USER_MODEL

class ChatRoom(models.Model):
    """
    Кімната чату — може бути загальною (public) або приватною між учасниками.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("Назва", max_length=150)
    slug = models.SlugField("Слаг", max_length=150, unique=True)
    is_private = models.BooleanField("Приватний", default=False)
    participants = models.ManyToManyField(User, related_name="chatrooms", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Кімната"
        verbose_name_plural = "Кімнати"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("chat:room_detail", kwargs={"slug": self.slug})


class Message(models.Model):
    """
    Повідомлення у чаті. Може містити текст або файл.
    """
    room = models.ForeignKey(ChatRoom, related_name="messages", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="messages", on_delete=models.CASCADE)
    content = models.TextField("Текст повідомлення", blank=True)
    attachment = models.FileField("Файл", upload_to="chat_files/", blank=True, null=True)
    timestamp = models.DateTimeField("Час відправки", auto_now_add=True)

    class Meta:
        ordering = ("timestamp",)
        verbose_name = "Повідомлення"
        verbose_name_plural = "Повідомлення"

    def __str__(self):
        snippet = self.content[:20] or (self.attachment.name if self.attachment else "")
        return f"{self.user}: {snippet}"
