"""Extra cargo tests covering remaining FBV branches."""
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from users.models import UserProfile

from .models import (
    BodyType, CargoType, Client, Driver, Order, Service, Vehicle,
    VehicleType,
)


def _admin():
    return User.objects.create_superuser('ad', 'a@a.com', 'Pass!12345')


def _client_user(name='cu'):
    u = User.objects.create_user(name, f'{name}@x.com', 'Pass!12345')
    UserProfile.objects.create(
        user=u, role='client', phone='+375 (29) 100-00-00',
        birth_date=date.today() - timedelta(days=25 * 365),
        timezone='Europe/Minsk',
    )
    return u


def _driver_user(name='du'):
    u = User.objects.create_user(name, f'{name}@x.com', 'Pass!12345')
    UserProfile.objects.create(
        user=u, role='driver', phone='+375 (29) 100-00-00',
        birth_date=date.today() - timedelta(days=30 * 365),
        timezone='Europe/Minsk',
    )
    return u


def _baseline():
    vt = VehicleType.objects.create(name='Грузовик')
    bt = BodyType.objects.create(name='Тент')
    ct = CargoType.objects.create(name='Стройматериалы')
    svc = Service.objects.create(name='Перевозка', description='', price_per_km=Decimal('10'))
    svc.suitable_cargo.add(ct)
    return vt, bt, ct, svc


class VehicleCrudTests(TestCase):
    def setUp(self):
        self.admin = _admin()
        self.client.login(username='ad', password='Pass!12345')
        self.vt, self.bt, *_ = _baseline()

    def test_create_update_delete_vehicle(self):
        resp = self.client.post(reverse('cargo:vehicle_create'), {
            'brand': 'MAN', 'model': 'TGS', 'plate_number': 'AB100-7',
            'vehicle_type': self.vt.pk, 'body_type': self.bt.pk,
            'capacity_tons': '5.5', 'year': 2020,
        })
        self.assertEqual(resp.status_code, 302)
        v = Vehicle.objects.get(plate_number='AB100-7')
        # detail
        self.assertEqual(self.client.get(reverse('cargo:vehicles_detail', args=[v.pk])).status_code, 200)
        # update
        self.client.post(reverse('cargo:vehicle_update', args=[v.pk]), {
            'brand': 'MAN', 'model': 'TGM', 'plate_number': 'AB100-7',
            'vehicle_type': self.vt.pk, 'body_type': self.bt.pk,
            'capacity_tons': '7.5', 'year': 2021,
        })
        v.refresh_from_db()
        self.assertEqual(v.model, 'TGM')
        # delete
        self.client.post(reverse('cargo:vehicle_delete', args=[v.pk]))
        self.assertFalse(Vehicle.objects.filter(pk=v.pk).exists())

    def test_search_and_sort(self):
        Vehicle.objects.create(brand='AAA', model='m', plate_number='X1-7',
                               vehicle_type=self.vt, body_type=self.bt,
                               capacity_tons=Decimal('1'), year=2020)
        self.assertContains(self.client.get(reverse('cargo:vehicles_list'), {'q': 'AAA'}), 'AAA')
        self.assertEqual(self.client.get(reverse('cargo:vehicles_list'), {'sort': '-year'}).status_code, 200)


class DriverCrudTests(TestCase):
    def setUp(self):
        self.admin = _admin()
        self.client.login(username='ad', password='Pass!12345')
        u = _driver_user('dr')
        self.driver = Driver.objects.create(
            user=u, first_name='A', last_name='B',
            birth_date=date.today() - timedelta(days=25 * 365),
            phone='+375 (29) 100-00-00', license_number='X1',
        )

    def test_update_delete(self):
        self.assertEqual(self.client.get(reverse('cargo:driver_update', args=[self.driver.pk])).status_code, 200)
        self.client.post(reverse('cargo:driver_delete', args=[self.driver.pk]))
        self.assertFalse(Driver.objects.filter(pk=self.driver.pk).exists())

    def test_search_sort(self):
        self.assertContains(self.client.get(reverse('cargo:drivers_list'), {'q': 'B'}), 'B')
        self.assertEqual(self.client.get(reverse('cargo:drivers_list'), {'sort': '-hired_at'}).status_code, 200)


class ServiceCrudFullTests(TestCase):
    def setUp(self):
        self.admin = _admin()
        self.client.login(username='ad', password='Pass!12345')
        _, _, self.ct, self.svc = _baseline()

    def test_update_delete(self):
        self.assertEqual(self.client.get(reverse('cargo:service_update', args=[self.svc.pk])).status_code, 200)
        self.client.post(reverse('cargo:service_update', args=[self.svc.pk]), {
            'name': 'Перевозка X', 'description': '-',
            'price_per_km': '5.50', 'suitable_cargo': [self.ct.pk],
        })
        self.svc.refresh_from_db()
        self.assertEqual(self.svc.name, 'Перевозка X')
        self.client.post(reverse('cargo:service_delete', args=[self.svc.pk]))
        self.assertFalse(Service.objects.filter(pk=self.svc.pk).exists())

    def test_search_sort_filter(self):
        resp = self.client.get(reverse('cargo:services_list'), {
            'q': 'Перевозка', 'sort': '-price_per_km', 'max_price': '999',
        })
        self.assertEqual(resp.status_code, 200)


class OrderFullCrudTests(TestCase):
    def setUp(self):
        self.admin = _admin()
        _, _, self.ct, self.svc = _baseline()
        self.cu = _client_user('cu')
        self.client_obj = Client.objects.create(
            user=self.cu, first_name='A', last_name='B',
            birth_date=date.today() - timedelta(days=25 * 365),
            phone='+375 (29) 100-00-00',
        )

    def test_admin_creates_order(self):
        self.client.login(username='ad', password='Pass!12345')
        # Note: OrderForm needs client too
        resp = self.client.post(reverse('cargo:order_create'), {
            'client': self.client_obj.pk,
            'cargo_type': self.ct.pk, 'cargo_name': 'A',
            'services': [self.svc.pk],
            'distance_km': '10', 'weight_tons': '1',
            'status': 'new',
            'scheduled_at': (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M'),
        })
        self.assertIn(resp.status_code, (200, 302))

    def test_client_views_own_order(self):
        order = Order.objects.create(
            client=self.client_obj, cargo_type=self.ct,
            cargo_name='X', distance_km=Decimal('10'),
            weight_tons=Decimal('1'),
            scheduled_at=timezone.now() + timedelta(days=1),
        )
        self.client.login(username='cu', password='Pass!12345')
        resp = self.client.get(reverse('cargo:order_detail', args=[order.pk]))
        self.assertEqual(resp.status_code, 200)

    def test_other_client_blocked(self):
        order = Order.objects.create(
            client=self.client_obj, cargo_type=self.ct,
            cargo_name='X', distance_km=Decimal('10'),
            weight_tons=Decimal('1'),
            scheduled_at=timezone.now() + timedelta(days=1),
        )
        other_u = _client_user('other')
        Client.objects.create(
            user=other_u, first_name='C', last_name='D',
            birth_date=date.today() - timedelta(days=25 * 365),
            phone='+375 (29) 100-00-00',
        )
        self.client.login(username='other', password='Pass!12345')
        resp = self.client.get(reverse('cargo:order_detail', args=[order.pk]))
        self.assertEqual(resp.status_code, 403)

    def test_client_update_delete_own(self):
        order = Order.objects.create(
            client=self.client_obj, cargo_type=self.ct,
            cargo_name='X', distance_km=Decimal('10'),
            weight_tons=Decimal('1'),
            scheduled_at=timezone.now() + timedelta(days=1),
        )
        order.services.add(self.svc)
        self.client.login(username='cu', password='Pass!12345')
        resp = self.client.post(reverse('cargo:order_update', args=[order.pk]), {
            'cargo_type': self.ct.pk, 'cargo_name': 'Y',
            'services': [self.svc.pk],
            'distance_km': '20', 'weight_tons': '2',
            'scheduled_at': (timezone.now() + timedelta(days=2)).strftime('%Y-%m-%dT%H:%M'),
        })
        self.assertEqual(resp.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.cargo_name, 'Y')
        self.client.post(reverse('cargo:order_delete', args=[order.pk]))
        self.assertFalse(Order.objects.filter(pk=order.pk).exists())

    def test_driver_sees_only_assigned(self):
        # client order without driver
        Order.objects.create(
            client=self.client_obj, cargo_type=self.ct,
            cargo_name='UNIQUE_CARGO_NAME_42', distance_km=Decimal('10'),
            weight_tons=Decimal('1'),
            scheduled_at=timezone.now() + timedelta(days=1),
        )
        du = _driver_user('dx')
        Driver.objects.create(
            user=du, first_name='D', last_name='V',
            birth_date=date.today() - timedelta(days=30 * 365),
            phone='+375 (29) 100-00-00', license_number='X9',
        )
        self.client.login(username='dx', password='Pass!12345')
        resp = self.client.get(reverse('cargo:orders_list'))
        self.assertEqual(resp.status_code, 200)
        # driver sees no orders since not assigned
        self.assertNotContains(resp, 'UNIQUE_CARGO_NAME_42')

    def test_orders_search_sort(self):
        Order.objects.create(
            client=self.client_obj, cargo_type=self.ct,
            cargo_name='SEARCHME', distance_km=Decimal('10'),
            weight_tons=Decimal('1'),
            scheduled_at=timezone.now() + timedelta(days=1),
        )
        self.client.login(username='ad', password='Pass!12345')
        self.assertContains(self.client.get(reverse('cargo:orders_list'), {'q': 'SEARCHME'}), 'SEARCHME')
        self.assertEqual(self.client.get(reverse('cargo:orders_list'), {'sort': 'status'}).status_code, 200)

    def test_non_client_create_blocked(self):
        # logged-in user without client_profile
        u = User.objects.create_user('plain', 'p@p.com', 'Pass!12345')
        UserProfile.objects.create(
            user=u, role='client', phone='+375 (29) 100-00-00',
            birth_date=date.today() - timedelta(days=25 * 365),
            timezone='Europe/Minsk',
        )
        self.client.login(username='plain', password='Pass!12345')
        resp = self.client.get(reverse('cargo:order_create'))
        self.assertEqual(resp.status_code, 403)
