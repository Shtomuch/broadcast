from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Meeting

User = get_user_model()

class MeetingsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='host', password='pass')
        self.client.login(username='host', password='pass')

    def test_create_and_list(self):
        resp = self.client.post(reverse('meetings:create'), {
            'title': 'Тестова зустріч',
            'description': 'Опис',
            'scheduled_time': '2025-05-01T10:00',
            'duration': 45,
            'participants': [],
            'recording_enabled': False
        })
        self.assertRedirects(resp, reverse('meetings:list'))
        m = Meeting.objects.get(title='Тестова зустріч')
        # тепер подивимось список
        list_resp = self.client.get(reverse('meetings:list'))
        self.assertContains(list_resp, 'Тестова зустріч')

    def test_detail_and_join(self):
        m = Meeting.objects.create(
            host=self.user,
            title='X',
            scheduled_time='2025-06-01T12:00',
            duration=30
        )
        # detail
        d = self.client.get(reverse('meetings:detail', kwargs={'slug': m.room_name}))
        self.assertEqual(d.status_code, 200)
        # join
        j = self.client.get(reverse('meetings:join', kwargs={'slug': m.room_name}))
        self.assertEqual(j.status_code, 200)
        self.assertContains(j, m.title)
