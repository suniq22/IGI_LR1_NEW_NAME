"""Tests for the main app."""
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from users.models import UserProfile

from .models import (
    CompanyInfo, Contact, FAQ, News, PromoCode, Review, Vacancy,
)


def _make_user(username='tester', superuser=False):
    if superuser:
        u = User.objects.create_superuser(username, f'{username}@x.com', 'Pass!12345')
    else:
        u = User.objects.create_user(username, f'{username}@x.com', 'Pass!12345')
        UserProfile.objects.create(
            user=u, role='client',
            phone='+375 (29) 100-00-00',
            birth_date=date.today() - timedelta(days=25 * 365),
            timezone='Europe/Minsk',
        )
    return u


class HomeTests(TestCase):
    def test_home(self):
        resp = self.client.get(reverse('main:home'))
        self.assertEqual(resp.status_code, 200)

    def test_static_pages(self):
        for name in ['main:about', 'main:privacy', 'main:contacts', 'main:faq']:
            self.assertEqual(self.client.get(reverse(name)).status_code, 200)


class NewsCrudTests(TestCase):
    def setUp(self):
        self.admin = _make_user('admin1', superuser=True)
        self.user = _make_user('plain1')

    def test_anonymous_can_list(self):
        News.objects.create(
            title='N1', summary='s', content='c',
        )
        resp = self.client.get(reverse('main:news_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'N1')

    def test_only_admin_can_create(self):
        self.client.login(username='plain1', password='Pass!12345')
        resp = self.client.get(reverse('main:news_create'))
        self.assertEqual(resp.status_code, 302)

        self.client.login(username='admin1', password='Pass!12345')
        resp = self.client.post(reverse('main:news_create'), {
            'title': 'New title',
            'summary': 'sum',
            'content': 'body',
            'published_at': '2025-01-01 10:00:00',
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(News.objects.filter(title='New title').exists())

    def test_news_search(self):
        News.objects.create(title='Alpha', summary='s', content='c')
        News.objects.create(title='Beta', summary='s', content='c')
        resp = self.client.get(reverse('main:news_list'), {'q': 'Alpha'})
        self.assertContains(resp, 'Alpha')
        self.assertNotContains(resp, 'Beta')


class ReviewTests(TestCase):
    def setUp(self):
        self.user = _make_user('rev1')

    def test_anonymous_cannot_create_review(self):
        resp = self.client.get(reverse('main:review_create'))
        self.assertEqual(resp.status_code, 302)

    def test_logged_user_creates_review(self):
        self.client.login(username='rev1', password='Pass!12345')
        resp = self.client.post(reverse('main:review_create'), {
            'rating': 5, 'text': 'Спасибо, отличный сервис!',
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Review.objects.filter(author=self.user).exists())

    def test_review_too_short(self):
        self.client.login(username='rev1', password='Pass!12345')
        resp = self.client.post(reverse('main:review_create'), {
            'rating': 5, 'text': 'короткий',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Review.objects.exists())


class PromoTests(TestCase):
    def test_promo_is_active(self):
        p = PromoCode.objects.create(
            code='X', discount_percent=10, description='d',
            valid_from=date.today() - timedelta(days=1),
            valid_to=date.today() + timedelta(days=1),
        )
        self.assertTrue(p.is_active)

    def test_promo_archived_inactive(self):
        p = PromoCode.objects.create(
            code='Y', discount_percent=10, description='d',
            valid_from=date.today() - timedelta(days=1),
            valid_to=date.today() + timedelta(days=1),
            is_archived=True,
        )
        self.assertFalse(p.is_active)


class VacancyTests(TestCase):
    def test_list_page(self):
        Vacancy.objects.create(title='V', description='d', salary=Decimal('1000'))
        resp = self.client.get(reverse('main:vacancies_list'))
        self.assertContains(resp, 'V')


class ContactCompanyTests(TestCase):
    def test_contact_str(self):
        c = Contact.objects.create(
            full_name='Ф И О', position='Дир',
            description='-', phone='-', email='a@b.c',
        )
        self.assertIn('Ф И О', str(c))

    def test_companyinfo_str(self):
        info = CompanyInfo.objects.create(title='T', text='x')
        self.assertEqual(str(info), 'T')


class FAQTests(TestCase):
    def test_search_q(self):
        FAQ.objects.create(question='Что такое ADR', answer='ответ')
        FAQ.objects.create(question='Другой вопрос', answer='-')
        resp = self.client.get(reverse('main:faq'), {'q': 'ADR'})
        self.assertContains(resp, 'ADR')
        self.assertNotContains(resp, 'Другой вопрос')
