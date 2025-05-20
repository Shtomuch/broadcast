from django.db.models.signals import post_save, pre_save # Додаємо pre_save
from django.dispatch import receiver
from .models import Meeting
from .tasks import send_meeting_reminder_email # Імпорт вашого завдання
from datetime import timedelta
from broadcast.celery import app as celery_app # Для скасування завдань

# Для скасування завдань, якщо Celery ініціалізований
try:
    from broadcast.celery import app as celery_app # Замініть 'broadcast' на назву вашого проекту
except ImportError:
    celery_app = None


@receiver(pre_save, sender=Meeting)
def cancel_previous_reminder_on_time_change(sender, instance, **kwargs):
    if not instance.pk: # Об'єкт ще не створений
        return
    if not celery_app: # Celery не доступний
        return

    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return # Старий об'єкт не знайдено (малоймовірно в pre_save, але для безпеки)

    # Перевіряємо, чи змінився час або чи зустріч вже відбулася/нагадування відправлено
    time_changed = old_instance.scheduled_time != instance.scheduled_time
    reminder_was_relevant = not old_instance.reminder_sent and old_instance.scheduled_time > timezone.now()

    if time_changed and old_instance.celery_task_id and reminder_was_relevant:
        celery_app.control.revoke(old_instance.celery_task_id)
        instance.celery_task_id = None # Готуємось до нового ID або його відсутності
        instance.reminder_sent = False # Скидаємо прапорець, якщо час змінився


@receiver(post_save, sender=Meeting)
def schedule_meeting_reminder(sender, instance, created, **kwargs):
    # Не планувати, якщо зустріч вже відбулася або нагадування відправлено
    if instance.reminder_sent or instance.scheduled_time <= timezone.now():
        # Якщо завдання було, але зустріч минула, а нагадування не відправлено - скасувати
        if instance.celery_task_id and not instance.reminder_sent and celery_app:
             celery_app.control.revoke(instance.celery_task_id)
             Meeting.objects.filter(pk=instance.pk).update(celery_task_id=None)
        return

    # Визначаємо час для нагадування (наприклад, за 7 хвилин до початку)
    reminder_delay_minutes = getattr(settings, 'MEETING_REMINDER_DELAY_MINUTES', 10)
    reminder_time = instance.scheduled_time - timedelta(minutes=reminder_delay_minutes)

    current_time = timezone.now()
    if reminder_time > current_time:
        # Скасувати попереднє завдання, якщо воно існує і відрізняється (на випадок множинних save())
        # Логіка скасування попереднього завдання перенесена в pre_save для більшої надійності
        # при зміні часу. Тут ми просто плануємо нове, якщо старе було скасоване або його не було.

        task = send_meeting_reminder_email.apply_async(
            args=[str(instance.id)], # Передаємо ID як рядок, оскільки UUID не завжди добре серіалізується в JSON за замовчуванням
            eta=reminder_time
        )
        # Оновлюємо ID завдання в моделі без виклику post_save знову, щоб уникнути рекурсії
        Meeting.objects.filter(pk=instance.pk).update(celery_task_id=task.id, reminder_sent=False)
    elif instance.celery_task_id and celery_app: # Час нагадування вже минув, але завдання є
        # Скасувати, якщо воно ще не виконалося
        celery_app.control.revoke(instance.celery_task_id)
        Meeting.objects.filter(pk=instance.pk).update(celery_task_id=None)