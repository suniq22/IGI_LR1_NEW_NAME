"""Tests for the cargo app."""
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import PromoCode
from users.models import UserProfile

from .models import (
    BodyType, CargoType, Client, Driver, Order, Organization, Service,
    Vehicle, VehicleType,
)


def _make_admin():
    return User.objects.create_superuser('admin', 'a@a.com', 'Pass!12345')


def _make_client_user(username='cuser'):
    u = User.objects.create_user(username, f'{username}@x.com', 'Pass!12345')
    UserProfile.objects.create(
        user=u, role='client', phone='+375 (29) 100-00-00',
        birth_date=date.today() - timedelta(days=25 * 365),
        timezone='Europe/Minsk',
    )
    return u


def _make_driver_user(username='duser'):
    u = User.objects.create_user(username, f'{username}@x.com', 'Pass!12345')
    UserProfile.objects.create(
        user=u, role='driver', phone='+375 (29) 100-00-00',
        birth_date=date.today() - timedelta(days=30 * 365),
        timezone='Europe/Minsk',
    )
    return u


class ModelTests(TestCase):
    def test_str(self):
        vt = VehicleType.objects.create(name='Грузовик')
        bt = BodyType.objects.create(name='Тент')
        ct = CargoType.objects.create(name='Еда')
        self.assertEqual(str(vt), 'Грузовик')
        self.assertEqual(str(bt), 'Тент')
        self.assertEqual(str(ct), 'Еда')

    def test_driver_age(self):
        u = _make_driver_user()
        d = Driver.objects.create(
            user=u, first_name='A', last_name='B',
            birth_date=date.today() - timedelta(days=20 * 365),
            phone='+375 (29) 100-00-00', license_number='AB1',
        )
        self.assertGreaterEqual(d.age, 19)

    def test_order_total_price(self):
        u = _make_client_user()
        c = Client.objects.create(
            user=u, first_name='A', last_name='B',
            birth_date=date.today() - timedelta(days=25 * 365),
            phone='+375 (29) 100-00-00',
        )
        ct = CargoType.objects.create(name='Что-то')
        s = Service.objects.create(name='Перевозка', description='d',
                                   price_per_km=Decimal('10.00'))
        o = Order.objects.create(
            client=c, cargo_type=ct, cargo_name='груз',
            distance_km=Decimal('100'), weight_tons=Decimal('1'),
            scheduled_at=timezone.now() + timedelta(days=1),
        )
        o.services.add(s)
        self.assertAlmostEqual(o.total_price, 1000.00, places=2)

    def test_order_total_with_promo(self):
        u = _make_client_user('c2')
        c = Client.objects.create(
            user=u, first_name='A', last_name='B',
            birth_date=date.today() - timedelta(days=25 * 365),
            phone='+375 (29) 100-00-00',
        )
        ct = CargoType.objects.create(name='Z')
        s = Service.objects.create(name='X', description='', price_per_km=Decimal('10'))
        p = PromoCode.objects.create(
            code='-50', discount_percent=50, description='-',
            valid_from=date.today() - timedelta(days=1),
            valid_to=date.today() + timedelta(days=1),
        )
        o = Order.objects.create(
            client=c, cargo_type=ct, cargo_name='X',
            distance_km=Decimal('10'), weight_tons=Decimal('1'),
            scheduled_at=timezone.now() + timedelta(days=1),
            promo_code=p,
        )
        o.services.add(s)
        self.assertAlmostEqual(o.total_price, 50.00, places=2)


class CatalogPagesTests(TestCase):
    def test_public_lists_load(self):
        for name in ['cargo:vehicles_list', 'cargo:drivers_list', 'cargo:services_list']:
            self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_orders_requires_login(self):
        resp = self.client.get(reverse('cargo:orders_list'))
        self.assertEqual(resp.status_code, 302)

    def test_stats_requires_login(self):
        resp = self.client.get(reverse('cargo:statistics'))
        self.assertEqual(resp.status_code, 302)


class StatsTests(TestCase):
    def test_stats_renders(self):
        admin = _make_admin()
        self.client.login(username='admin', password='Pass!12345')
        resp = self.client.get(reverse('cargo:statistics'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Статистика')


class CRUDClientOrderTests(TestCase):
    def setUp(self):
        self.admin = _make_admin()
        self.u = _make_client_user('client_x')
        self.client_obj = Client.objects.create(
            user=self.u, first_name='Ig', last_name='Ig',
            birth_date=date.today() - timedelta(days=25 * 365),
            phone='+375 (29) 100-00-00',
        )
        self.cargo_type = CargoType.objects.create(name='Тест')
        self.svc = Service.objects.create(
            name='Перевозка', description='', price_per_km=Decimal('5'),
        )

    def test_client_creates_order(self):
        self.client.login(username='client_x', password='Pass!12345')
        resp = self.client.post(reverse('cargo:order_create'), {
            'cargo_type': self.cargo_type.pk,
            'cargo_name': 'Груз 1',
            'services': [self.svc.pk],
            'distance_km': '10',
            'weight_tons': '1',
            'scheduled_at': (timezone.now() + timedelta(days=2)).strftime('%Y-%m-%dT%H:%M'),
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Order.objects.filter(cargo_name='Груз 1').exists())

    def test_invalid_distance(self):
        self.client.login(username='client_x', password='Pass!12345')
        resp = self.client.post(reverse('cargo:order_create'), {
            'cargo_type': self.cargo_type.pk,
            'cargo_name': 'Груз 2',
            'services': [self.svc.pk],
            'distance_km': '0',
            'weight_tons': '1',
            'scheduled_at': (timezone.now() + timedelta(days=2)).strftime('%Y-%m-%dT%H:%M'),
        })
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Order.objects.filter(cargo_name='Груз 2').exists())


class ServiceCrudTests(TestCase):
    def setUp(self):
        self.admin = _make_admin()

    def test_admin_creates_service(self):
        self.client.login(username='admin', password='Pass!12345')
        ct = CargoType.objects.create(name='X')
        resp = self.client.post(reverse('cargo:service_create'), {
            'name': 'Новая',
            'description': 'тест',
            'price_per_km': '7.50',
            'suitable_cargo': [ct.pk],
            'is_additional': False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Service.objects.filter(name='Новая').exists())

    def test_non_admin_blocked(self):
        u = _make_client_user('p1')
        self.client.login(username='p1', password='Pass!12345')
        resp = self.client.get(reverse('cargo:service_create'))
        self.assertEqual(resp.status_code, 302)
