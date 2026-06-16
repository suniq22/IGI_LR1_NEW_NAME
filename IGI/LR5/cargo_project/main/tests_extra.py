"""Extra tests to cover remaining view paths."""
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from users.models import UserProfile

from .models import News, PromoCode, Review, Vacancy
from .services import (
    fetch_currency_rates, fetch_random_quote, render_chart_png_base64,
)


def _make_user(username='u', superuser=False):
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


class NewsFullCrudTests(TestCase):
    def setUp(self):
        self.admin = _make_user('a', superuser=True)
        self.client.login(username='a', password='Pass!12345')
        self.n = News.objects.create(title='Old', summary='s', content='c')

    def test_detail(self):
        self.assertEqual(self.client.get(reverse('main:news_detail', args=[self.n.pk])).status_code, 200)

    def test_update_get_and_post(self):
        self.assertEqual(self.client.get(reverse('main:news_update', args=[self.n.pk])).status_code, 200)
        resp = self.client.post(reverse('main:news_update', args=[self.n.pk]), {
            'title': 'New', 'summary': 's2', 'content': 'c2',
            'published_at': '2025-01-01 10:00:00',
        })
        self.assertEqual(resp.status_code, 302)
        self.n.refresh_from_db()
        self.assertEqual(self.n.title, 'New')

    def test_delete(self):
        self.assertEqual(self.client.get(reverse('main:news_delete', args=[self.n.pk])).status_code, 200)
        resp = self.client.post(reverse('main:news_delete', args=[self.n.pk]))
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(News.objects.filter(pk=self.n.pk).exists())

    def test_sort(self):
        News.objects.create(title='B', summary='s', content='c')
        resp = self.client.get(reverse('main:news_list'), {'sort': 'title'})
        self.assertEqual(resp.status_code, 200)


class VacancyFullCrudTests(TestCase):
    def setUp(self):
        self.admin = _make_user('vad', superuser=True)
        self.client.login(username='vad', password='Pass!12345')

    def test_full_crud(self):
        # CREATE
        resp = self.client.get(reverse('main:vacancy_create'))
        self.assertEqual(resp.status_code, 200)
        resp = self.client.post(reverse('main:vacancy_create'), {
            'title': 'V1', 'description': 'd', 'salary': '1000', 'is_active': 'on',
        })
        self.assertEqual(resp.status_code, 302)
        v = Vacancy.objects.get(title='V1')
        # UPDATE
        resp = self.client.get(reverse('main:vacancy_update', args=[v.pk]))
        self.assertEqual(resp.status_code, 200)
        self.client.post(reverse('main:vacancy_update', args=[v.pk]), {
            'title': 'V2', 'description': 'd', 'salary': '2000', 'is_active': 'on',
        })
        v.refresh_from_db()
        self.assertEqual(v.title, 'V2')
        # DELETE
        self.client.get(reverse('main:vacancy_delete', args=[v.pk]))
        self.client.post(reverse('main:vacancy_delete', args=[v.pk]))
        self.assertFalse(Vacancy.objects.filter(pk=v.pk).exists())

    def test_negative_salary(self):
        resp = self.client.post(reverse('main:vacancy_create'), {
            'title': 'V', 'description': 'd', 'salary': '-1', 'is_active': 'on',
        })
        self.assertEqual(resp.status_code, 200)

    def test_search_sort(self):
        Vacancy.objects.create(title='Apple', description='d', salary=Decimal('1'))
        Vacancy.objects.create(title='Banana', description='d', salary=Decimal('2'))
        self.assertContains(self.client.get(reverse('main:vacancies_list'), {'q': 'Apple'}), 'Apple')
        self.assertEqual(self.client.get(reverse('main:vacancies_list'), {'sort': 'salary'}).status_code, 200)


class PromoFullCrudTests(TestCase):
    def setUp(self):
        self.admin = _make_user('pad', superuser=True)
        self.client.login(username='pad', password='Pass!12345')

    def test_full_crud(self):
        resp = self.client.post(reverse('main:promocode_create'), {
            'code': 'P1', 'discount_percent': 10, 'description': 'd',
            'valid_from': date.today().isoformat(),
            'valid_to': (date.today() + timedelta(days=10)).isoformat(),
        })
        self.assertEqual(resp.status_code, 302)
        p = PromoCode.objects.get(code='P1')
        self.client.post(reverse('main:promocode_update', args=[p.pk]), {
            'code': 'P1', 'discount_percent': 15, 'description': 'd',
            'valid_from': date.today().isoformat(),
            'valid_to': (date.today() + timedelta(days=20)).isoformat(),
        })
        p.refresh_from_db()
        self.assertEqual(p.discount_percent, 15)
        self.client.post(reverse('main:promocode_delete', args=[p.pk]))
        self.assertFalse(PromoCode.objects.filter(pk=p.pk).exists())

    def test_validation_dates_swapped(self):
        resp = self.client.post(reverse('main:promocode_create'), {
            'code': 'BAD', 'discount_percent': 10, 'description': 'd',
            'valid_from': (date.today() + timedelta(days=10)).isoformat(),
            'valid_to': date.today().isoformat(),
        })
        self.assertEqual(resp.status_code, 200)

    def test_search(self):
        PromoCode.objects.create(
            code='HOT', discount_percent=10, description='горячий',
            valid_from=date.today(), valid_to=date.today() + timedelta(days=5),
        )
        resp = self.client.get(reverse('main:promocodes_list'), {'q': 'HOT'})
        self.assertContains(resp, 'HOT')


class ReviewExtraTests(TestCase):
    def setUp(self):
        self.u1 = _make_user('a1')
        self.u2 = _make_user('a2')

    def test_user_cannot_edit_others_review(self):
        r = Review.objects.create(author=self.u1, rating=5, text='Очень хорошо все было!')
        self.client.login(username='a2', password='Pass!12345')
        resp = self.client.get(reverse('main:review_update', args=[r.pk]))
        self.assertEqual(resp.status_code, 403)
        resp = self.client.get(reverse('main:review_delete', args=[r.pk]))
        self.assertEqual(resp.status_code, 403)

    def test_user_edits_own_review(self):
        r = Review.objects.create(author=self.u1, rating=3, text='ничего особенного')
        self.client.login(username='a1', password='Pass!12345')
        resp = self.client.post(reverse('main:review_update', args=[r.pk]), {
            'rating': 5, 'text': 'Поменял мнение — всё отлично!',
        })
        self.assertEqual(resp.status_code, 302)
        r.refresh_from_db()
        self.assertEqual(r.rating, 5)

    def test_user_deletes_own_review(self):
        r = Review.objects.create(author=self.u1, rating=3, text='не очень понравилось')
        self.client.login(username='a1', password='Pass!12345')
        resp = self.client.post(reverse('main:review_delete', args=[r.pk]))
        self.assertEqual(resp.status_code, 302)


class ServicesTests(TestCase):
    def test_fetch_quote_returns_dict(self):
        q = fetch_random_quote(timeout=0.001)
        self.assertIn('content', q)
        self.assertIn('author', q)

    def test_fetch_rates_returns_dict(self):
        r = fetch_currency_rates(timeout=0.001)
        self.assertIn('rates', r)
        self.assertIn('base', r)

    def test_chart_renders_base64(self):
        out = render_chart_png_base64(['A', 'B'], [10, 20], title='t', ylabel='y')
        self.assertTrue(len(out) > 100)
