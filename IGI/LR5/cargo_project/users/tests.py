"""Tests for the users app."""
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse

from .models import UserProfile
from .validators import validate_age_adult, validate_phone


class ValidatorTests(TestCase):
    def test_phone_valid(self):
        validate_phone('+375 (29) 123-45-67')

    def test_phone_invalid(self):
        for bad in ['+375 (29) 12345-67', '+375 29 123-45-67', '+375 (28) 123-45-67', 'abc']:
            with self.assertRaises(ValidationError):
                validate_phone(bad)

    def test_age_18plus(self):
        validate_age_adult(date.today() - timedelta(days=20 * 365))

    def test_age_too_young(self):
        with self.assertRaises(ValidationError):
            validate_age_adult(date.today() - timedelta(days=10 * 365))

    def test_birthday_future(self):
        with self.assertRaises(ValidationError):
            validate_age_adult(date.today() + timedelta(days=1))

    def test_birthday_none(self):
        with self.assertRaises(ValidationError):
            validate_age_adult(None)


class SignupTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_signup_page_loads(self):
        resp = self.client.get(reverse('users:signup'))
        self.assertEqual(resp.status_code, 200)

    def test_signup_creates_profile(self):
        resp = self.client.post(reverse('users:signup'), {
            'username': 'newuser',
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'email': 'newuser@example.com',
            'password1': 'TestPass!12345',
            'password2': 'TestPass!12345',
            'phone': '+375 (29) 111-22-33',
            'birth_date': (date.today() - timedelta(days=20 * 365)).isoformat(),
            'role': 'client',
            'timezone': 'Europe/Minsk',
        })
        self.assertIn(resp.status_code, (302, 200))
        self.assertTrue(User.objects.filter(username='newuser').exists())
        u = User.objects.get(username='newuser')
        self.assertTrue(hasattr(u, 'profile'))
        self.assertEqual(u.profile.role, 'client')

    def test_signup_rejects_minor(self):
        resp = self.client.post(reverse('users:signup'), {
            'username': 'kid',
            'first_name': 'Малыш',
            'last_name': 'Малышев',
            'email': 'kid@example.com',
            'password1': 'TestPass!12345',
            'password2': 'TestPass!12345',
            'phone': '+375 (29) 111-22-33',
            'birth_date': (date.today() - timedelta(days=5 * 365)).isoformat(),
            'role': 'client',
            'timezone': 'Europe/Minsk',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(User.objects.filter(username='kid').exists())

    def test_login_logout(self):
        u = User.objects.create_user('u1', password='Pass!12345')
        UserProfile.objects.create(
            user=u, role='client', phone='+375 (29) 100-00-00',
            birth_date=date.today() - timedelta(days=25 * 365),
            timezone='Europe/Minsk',
        )
        ok = self.client.login(username='u1', password='Pass!12345')
        self.assertTrue(ok)
        resp = self.client.get(reverse('users:profile'))
        self.assertEqual(resp.status_code, 200)
