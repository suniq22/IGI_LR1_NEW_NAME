"""Forms for the main app: review submission, news CRUD, promo CRUD, etc."""
from django import forms

from .models import Contact, FAQ, News, PromoCode, Review, Vacancy


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['full_name', 'position', 'description', 'phone', 'email', 'photo']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class FAQForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ['question', 'answer', 'added_at']
        widgets = {
            'answer': forms.Textarea(attrs={'rows': 4}),
            'added_at': forms.DateInput(attrs={'type': 'date'}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'minlength': 10}),
            'rating': forms.Select(),
        }

    def clean_text(self):
        text = self.cleaned_data['text'].strip()
        if len(text) < 10:
            raise forms.ValidationError('Текст отзыва слишком короткий (минимум 10 символов)')
        return text


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'summary', 'content', 'image', 'published_at']
        widgets = {
            'published_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'content': forms.Textarea(attrs={'rows': 6}),
        }


class VacancyForm(forms.ModelForm):
    class Meta:
        model = Vacancy
        fields = ['title', 'description', 'salary', 'is_active']
        widgets = {'description': forms.Textarea(attrs={'rows': 4})}

    def clean_salary(self):
        salary = self.cleaned_data['salary']
        if salary < 0:
            raise forms.ValidationError('Зарплата должна быть неотрицательной')
        return salary


class PromoCodeForm(forms.ModelForm):
    class Meta:
        model = PromoCode
        fields = ['code', 'discount_percent', 'description', 'valid_from', 'valid_to', 'is_archived']
        widgets = {
            'valid_from': forms.DateInput(attrs={'type': 'date'}),
            'valid_to': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned = super().clean()
        vf = cleaned.get('valid_from')
        vt = cleaned.get('valid_to')
        if vf and vt and vf > vt:
            raise forms.ValidationError('Дата начала должна быть раньше даты окончания')
        return cleaned
