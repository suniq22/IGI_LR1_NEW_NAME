"""Cargo / transportation domain models."""
from datetime import date

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from users.validators import validate_age_adult, validate_phone


class VehicleType(models.Model):
    """Тип транспортного средства (грузовик, фургон и т.д.)."""
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')

    class Meta:
        ordering = ['name']
        verbose_name = 'Тип транспортного средства'
        verbose_name_plural = 'Типы транспортных средств'

    def __str__(self):
        return self.name


class BodyType(models.Model):
    """Тип кузова."""
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')

    class Meta:
        ordering = ['name']
        verbose_name = 'Тип кузова'
        verbose_name_plural = 'Типы кузова'

    def __str__(self):
        return self.name


class CargoType(models.Model):
    """Тип / вид груза."""
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    is_dangerous = models.BooleanField(default=False, verbose_name='Опасный груз')

    class Meta:
        ordering = ['name']
        verbose_name = 'Вид груза'
        verbose_name_plural = 'Виды грузов'

    def __str__(self):
        return self.name


class Driver(models.Model):
    """Водитель — OneToOne к User, чтобы он мог логиниться."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='driver_profile',
        verbose_name='Учётка пользователя',
    )
    first_name = models.CharField(max_length=80, verbose_name='Имя')
    last_name = models.CharField(max_length=80, verbose_name='Фамилия')
    birth_date = models.DateField(
        validators=[validate_age_adult], verbose_name='Дата рождения'
    )
    phone = models.CharField(
        max_length=32, validators=[validate_phone], verbose_name='Телефон'
    )
    license_number = models.CharField(max_length=32, verbose_name='Номер ВУ')
    hired_at = models.DateField(default=timezone.now, verbose_name='Принят на работу')

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = 'Водитель'
        verbose_name_plural = 'Водители'

    def __str__(self):
        return f'{self.last_name} {self.first_name}'

    @property
    def age(self):
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )


class Vehicle(models.Model):
    """Транспортное средство."""
    brand = models.CharField(max_length=60, verbose_name='Марка')
    model = models.CharField(max_length=60, verbose_name='Модель')
    plate_number = models.CharField(
        max_length=20, unique=True, verbose_name='Гос. номер'
    )
    vehicle_type = models.ForeignKey(
        VehicleType,
        on_delete=models.PROTECT,
        related_name='vehicles',
        verbose_name='Тип ТС',
    )
    body_type = models.ForeignKey(
        BodyType,
        on_delete=models.PROTECT,
        related_name='vehicles',
        verbose_name='Тип кузова',
    )
    capacity_tons = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Грузоподъёмность, т',
    )
    year = models.PositiveIntegerField(
        validators=[MinValueValidator(1980), MaxValueValidator(2100)],
        verbose_name='Год выпуска',
    )
    driver = models.ForeignKey(
        Driver,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vehicles',
        verbose_name='Закреплённый водитель',
    )

    class Meta:
        ordering = ['brand', 'model']
        verbose_name = 'Транспортное средство'
        verbose_name_plural = 'Транспортные средства'

    def __str__(self):
        return f'{self.brand} {self.model} ({self.plate_number})'


class Organization(models.Model):
    """Организация-клиент."""
    name = models.CharField(max_length=200, unique=True, verbose_name='Название')
    legal_address = models.CharField(max_length=255, verbose_name='Юр. адрес')
    inn = models.CharField(max_length=20, unique=True, verbose_name='УНП')
    phone = models.CharField(
        max_length=32, validators=[validate_phone], verbose_name='Телефон'
    )
    email = models.EmailField(verbose_name='Email')

    class Meta:
        ordering = ['name']
        verbose_name = 'Организация'
        verbose_name_plural = 'Организации'

    def __str__(self):
        return self.name


class Client(models.Model):
    """Клиент (физлицо). Привязан к User один к одному."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='client_profile',
        verbose_name='Учётка пользователя',
    )
    first_name = models.CharField(max_length=80, verbose_name='Имя')
    last_name = models.CharField(max_length=80, verbose_name='Фамилия')
    birth_date = models.DateField(
        validators=[validate_age_adult], verbose_name='Дата рождения'
    )
    phone = models.CharField(
        max_length=32, validators=[validate_phone], verbose_name='Телефон'
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clients',
        verbose_name='Организация',
    )

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    def __str__(self):
        return f'{self.last_name} {self.first_name}'

    @property
    def age(self):
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )


class Service(models.Model):
    """Услуга, оказываемая компанией."""
    name = models.CharField(max_length=200, unique=True, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    price_per_km = models.DecimalField(
        max_digits=8, decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Цена за км, BYN',
    )
    suitable_cargo = models.ManyToManyField(
        CargoType,
        related_name='services',
        verbose_name='Подходящие виды груза',
    )
    is_additional = models.BooleanField(
        default=False, verbose_name='Дополнительная услуга'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'

    def __str__(self):
        return self.name


class Order(models.Model):
    """Заказ на перевозку."""
    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_DONE = 'done'
    STATUS_CANCELED = 'canceled'
    STATUS_CHOICES = [
        (STATUS_NEW, 'Новый'),
        (STATUS_IN_PROGRESS, 'В работе'),
        (STATUS_DONE, 'Выполнен'),
        (STATUS_CANCELED, 'Отменён'),
    ]

    client = models.ForeignKey(
        Client, on_delete=models.PROTECT, related_name='orders', verbose_name='Клиент'
    )
    driver = models.ForeignKey(
        Driver, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='orders', verbose_name='Водитель',
    )
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='orders', verbose_name='Транспортное средство',
    )
    cargo_type = models.ForeignKey(
        CargoType, on_delete=models.PROTECT, related_name='orders',
        verbose_name='Вид груза',
    )
    cargo_name = models.CharField(max_length=200, verbose_name='Наименование груза')
    services = models.ManyToManyField(
        Service, related_name='orders', verbose_name='Услуги'
    )
    distance_km = models.DecimalField(
        max_digits=8, decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Расстояние, км',
    )
    weight_tons = models.DecimalField(
        max_digits=6, decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Вес, т',
    )
    status = models.CharField(
        max_length=16, choices=STATUS_CHOICES, default=STATUS_NEW,
        verbose_name='Статус',
    )
    promo_code = models.ForeignKey(
        'main.PromoCode', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='orders', verbose_name='Промокод',
    )
    scheduled_at = models.DateTimeField(verbose_name='Запланировано на')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-scheduled_at']
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'Заказ #{self.pk} ({self.cargo_name})'

    @property
    def total_price(self):
        """Сумма по всем услугам * расстояние, с учётом промокода."""
        base = sum(
            (s.price_per_km for s in self.services.all()),
            start=0,
        )
        total = float(base) * float(self.distance_km)
        if self.promo_code and self.promo_code.is_active:
            total *= (100 - self.promo_code.discount_percent) / 100.0
        return round(total, 2)
