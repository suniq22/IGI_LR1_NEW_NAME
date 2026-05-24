"""Registration and profile forms."""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import UserProfile
from .validators import validate_age_adult, validate_phone


class SignUpForm(UserCreationForm):
    """User registration form with extra profile fields."""
    email = forms.EmailField(required=True, label='Email')
    first_name = forms.CharField(max_length=30, required=True, label='Имя')
    last_name = forms.CharField(max_length=30, required=True, label='Фамилия')
    phone = forms.CharField(
        max_length=32,
        required=True,
        label='Телефон',
        help_text='Формат: +375 (29) XXX-XX-XX',
        widget=forms.TextInput(attrs={
            'placeholder': '+375 (29) XXX-XX-XX',
            'pattern': r'^\+375 \((25|29|33|44)\) \d{3}-\d{2}-\d{2}$',
        }),
    )
    birth_date = forms.DateField(
        required=True,
        label='Дата рождения',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        required=True,
        label='Роль',
    )
    timezone = forms.ChoiceField(
        choices=UserProfile.TIMEZONE_CHOICES,
        required=True,
        initial='Europe/Minsk',
        label='Часовой пояс',
    )

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email',
            'password1', 'password2',
        )

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        validate_phone(phone)
        return phone

    def clean_birth_date(self):
        bd = self.cleaned_data['birth_date']
        validate_age_adult(bd)
        return bd

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                role=self.cleaned_data['role'],
                phone=self.cleaned_data['phone'],
                birth_date=self.cleaned_data['birth_date'],
                timezone=self.cleaned_data['timezone'],
            )
        return user


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'birth_date', 'timezone']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'phone': forms.TextInput(attrs={
                'pattern': r'^\+375 \((25|29|33|44)\) \d{3}-\d{2}-\d{2}$',
                'placeholder': '+375 (29) XXX-XX-XX',
            }),
        }

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        validate_phone(phone)
        return phone

    def clean_birth_date(self):
        bd = self.cleaned_data['birth_date']
        validate_age_adult(bd)
        return bd
