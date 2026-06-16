"""Forms for cargo domain: orders, drivers, vehicles, services."""
from django import forms
from django.contrib.auth import get_user_model

from .models import (
    BodyType, CargoType, Client, Driver, Order, Organization, Service,
    Vehicle, VehicleType,
)

User = get_user_model()


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'client', 'cargo_type', 'cargo_name', 'services', 'distance_km',
            'weight_tons', 'driver', 'vehicle', 'promo_code',
            'scheduled_at', 'status',
        ]
        widgets = {
            'scheduled_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'services': forms.CheckboxSelectMultiple(),
        }

    def clean_distance_km(self):
        v = self.cleaned_data['distance_km']
        if v <= 0:
            raise forms.ValidationError('Расстояние должно быть больше 0')
        return v

    def clean_weight_tons(self):
        v = self.cleaned_data['weight_tons']
        if v <= 0:
            raise forms.ValidationError('Вес должен быть больше 0')
        return v


class ClientOrderForm(forms.ModelForm):
    """Forma for client to create their own order (without admin fields)."""
    class Meta:
        model = Order
        fields = [
            'cargo_type', 'cargo_name', 'services',
            'distance_km', 'weight_tons', 'promo_code', 'scheduled_at',
        ]
        widgets = {
            'scheduled_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'services': forms.CheckboxSelectMultiple(),
        }

    def clean_distance_km(self):
        v = self.cleaned_data['distance_km']
        if v <= 0:
            raise forms.ValidationError('Расстояние должно быть больше 0')
        return v

    def clean_weight_tons(self):
        v = self.cleaned_data['weight_tons']
        if v <= 0:
            raise forms.ValidationError('Вес должен быть больше 0')
        return v


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'price_per_km', 'suitable_cargo', 'is_additional']
        widgets = {'suitable_cargo': forms.CheckboxSelectMultiple()}


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['brand', 'model', 'plate_number', 'vehicle_type',
                  'body_type', 'capacity_tons', 'year', 'driver']


class DriverForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(driver_profile__isnull=True),
        label='Учётная запись пользователя',
        help_text='Выберите пользователя без профиля водителя',
    )

    class Meta:
        model = Driver
        fields = ['user', 'first_name', 'last_name', 'birth_date', 'phone',
                  'license_number', 'hired_at']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'hired_at': forms.DateInput(attrs={'type': 'date'}),
            'phone': forms.TextInput(attrs={
                'pattern': r'^\+375 \((25|29|33|44)\) \d{3}-\d{2}-\d{2}$',
                'placeholder': '+375 (29) XXX-XX-XX',
            }),
        }


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name', 'legal_address', 'inn', 'phone', 'email']
        widgets = {
            'phone': forms.TextInput(attrs={
                'pattern': r'^\+375 \((25|29|33|44)\) \d{3}-\d{2}-\d{2}$',
                'placeholder': '+375 (29) XXX-XX-XX',
            }),
        }
