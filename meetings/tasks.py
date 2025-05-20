from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from django.apps import apps  # Для безпечного імпорту моделі
from datetime import timedelta
import uuid


@shared_task(bind=True, max_retries=3)
def send_meeting_reminder_email(self, meeting_id_str: str):  # meeting_id тепер UUID, передаємо як рядок
    MeetingModel = apps.get_model('meetings', 'Meeting')  # Замініть 'your_app_name'
    meeting_id = uuid.UUID(meeting_id_str)  # Конвертуємо рядок назад в UUID

    try:
        meeting = MeetingModel.objects.get(id=meeting_id)

        if meeting.reminder_sent or meeting.scheduled_time < timezone.now():
            return f"Reminder for meeting {meeting_id} (ID: {meeting.id}) already sent or meeting is in the past."

        organizer = meeting.host  # Поле називається 'host'
        if not organizer.email:
            return f"Organizer {organizer.username} for meeting {meeting.id} has no email address."

        subject = f"Нагадування: Ваша зустріч '{meeting.title}' незабаром"

        time_until_meeting = meeting.scheduled_time - timezone.now()
        minutes_until_meeting = max(0, int(time_until_meeting.total_seconds() / 60))  # Не показувати від'ємні значення

        html_message = render_to_string('meetings/meeting_reminder.html', {
            'organizer': organizer,  # Передаємо організатора
            'meeting': meeting,
            'minutes_until_meeting': minutes_until_meeting,
        })

        send_mail(
            subject,
            '',  # plain_message
            settings.DEFAULT_FROM_EMAIL,
            [organizer.email],
            html_message=html_message,
            fail_silently=False
        )

        meeting.reminder_sent = True
        meeting.celery_task_id = None  # Очищаємо ID завдання після успішної відправки
        meeting.save(update_fields=['reminder_sent', 'celery_task_id'])
        return f"Reminder sent for meeting '{meeting.title}' (ID: {meeting.id}) to {organizer.email}"

    except MeetingModel.DoesNotExist:
        return f"Meeting with ID {meeting_id} not found."
    except Exception as exc:
        # Логування помилки (використовуйте стандартний логер Django або Celery)
        print(f"Error sending reminder for meeting {meeting_id}: {exc}")
        raise self.retry(exc=exc,
                         countdown=60 * (self.request.retries + 1))  # Збільшуємо час очікування при повторних спробах