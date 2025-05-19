import uuid
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

User = settings.AUTH_USER_MODEL

class Meeting(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    host = models.ForeignKey(User, related_name='hosted_meetings',
                             on_delete=models.CASCADE, verbose_name="Організатор")
    title = models.CharField("Тема зустрічі", max_length=200)
    description = models.TextField("Опис", blank=True)
    room_name = models.SlugField("Назва кімнати", max_length=255, unique=True, blank=True)
    jitsi_room = models.CharField("Jitsi room", max_length=50, blank=True, editable=False)
    scheduled_time = models.DateTimeField("Заплановано на")
    duration = models.PositiveIntegerField("Тривалість (хвилин)", default=60)
    participants = models.ManyToManyField(User, related_name='meetings',
                                          blank=True, verbose_name="Учасники")
    recording_enabled = models.BooleanField("Увімкнути запис", default=False)
    recording_url = models.URLField("URL запису", blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")

    class Meta:
        ordering = ['-scheduled_time']
        verbose_name = "Зустріч"
        verbose_name_plural = "Зустрічі"

    def save(self, *args, **kwargs):
        if not self.room_name:
            base = slugify(self.title) or "meeting"
            self.room_name = f"{base}-{uuid.uuid4().hex[:6]}"
        if not self.jitsi_room:
            self.jitsi_room = f"TeamMeet_{timezone.now().strftime('%Y%m%d_%H%M%S')}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.scheduled_time})"

    def get_absolute_url(self):
        return reverse('meetings:detail', kwargs={'slug': self.room_name})

    @property
    def jitsi_url(self) -> str:
        domain = settings.JITSI_DOMAIN
        return f"https://{domain}/{self.jitsi_room}"
