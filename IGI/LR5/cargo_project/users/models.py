"""User profile model with extra fields (OneToOne to auth user)."""
import pytz
from django.conf import settings
from django.db import models

from .validators import validate_age_adult, validate_phone


class UserProfile(models.Model):
    """Profile linked one-to-one with the built-in User."""

    ROLE_CLIENT = 'client'
    ROLE_DRIVER = 'driver'
    ROLE_CHOICES = [
        (ROLE_CLIENT, 'Клиент'),
        (ROLE_DRIVER, 'Водитель'),
    ]

    TIMEZONE_CHOICES = [(tz, tz) for tz in pytz.common_timezones]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    role = models.CharField(
        max_length=16,
        choices=ROLE_CHOICES,
        default=ROLE_CLIENT,
        verbose_name='Роль',
    )
    phone = models.CharField(
        max_length=32,
        validators=[validate_phone],
        help_text='Формат: +375 (29) XXX-XX-XX',
        verbose_name='Телефон',
    )
    birth_date = models.DateField(
        validators=[validate_age_adult],
        verbose_name='Дата рождения',
    )
    timezone = models.CharField(
        max_length=64,
        choices=TIMEZONE_CHOICES,
        default='Europe/Minsk',
        verbose_name='Часовой пояс',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return f'{self.user.username} ({self.get_role_display()})'

    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )
