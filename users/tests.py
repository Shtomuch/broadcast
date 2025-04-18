from django.test import TestCase
from django.urls import reverse

from .models import User


class UserAppTests(TestCase):
    def setUp(self):
        self.credentials = {'username': 'john', 'password': 'secretpass'}
        User.objects.create_user(**self.credentials)

    def test_signup_page(self):
        resp = self.client.get(reverse('users:signup'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '<form')

    def test_signup_creates_user(self):
        resp = self.client.post(reverse('users:signup'), {
            'username': 'alice',
            'password1': 'ComplexPass123',
            'password2': 'ComplexPass123',
            'email': 'alice@example.com'
        })
        self.assertRedirects(resp, reverse('users:login'))
        self.assertTrue(User.objects.filter(username='alice').exists())

    def test_login_page(self):
        resp = self.client.get(reverse('users:login'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '<form')

    def test_login_and_profile(self):
        self.assertTrue(self.client.login(**self.credentials))
        resp = self.client.get(reverse('users:profile'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'john')

    def test_profile_requires_login(self):
        resp = self.client.get(reverse('users:profile'))
        login_url = reverse('users:login')
        self.assertRedirects(resp, f"{login_url}?next={reverse('users:profile')}")
