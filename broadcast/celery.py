# your_project_name/celery.py
import os
from celery import Celery

# Встановлюємо змінну оточення для налаштувань Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'broadcast.settings')

app = Celery('broadcast')

# Використовуємо конфігурацію Django для Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматично знаходимо завдання в усіх зареєстрованих додатках Django
app.autodiscover_tasks()