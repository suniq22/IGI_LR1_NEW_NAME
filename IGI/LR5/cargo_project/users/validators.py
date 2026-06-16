"""Shared validators for user-related data."""
import re
from datetime import date

from django.core.exceptions import ValidationError


PHONE_REGEX = re.compile(r'^\+375 \((25|29|33|44)\) \d{3}-\d{2}-\d{2}$')


def validate_phone(value):
    """Phone format: +375 (29) XXX-XX-XX."""
    if not PHONE_REGEX.match(value):
        raise ValidationError(
            'Телефон должен быть в формате +375 (29) XXX-XX-XX'
        )


def validate_age_adult(value):
    """Person must be 18 years or older."""
    if value is None:
        raise ValidationError('Дата рождения обязательна')
    today = date.today()
    age = today.year - value.year - (
        (today.month, today.day) < (value.month, value.day)
    )
    if age < 18:
        raise ValidationError('Возраст должен быть 18 лет или больше')
    if value > today:
        raise ValidationError('Дата рождения не может быть в будущем')
