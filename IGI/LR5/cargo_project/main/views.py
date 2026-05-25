"""Function-Based Views for general site pages and CRUD for News/Review/Promo/Vacancy."""
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import FAQForm, NewsForm, PromoCodeForm, ReviewForm, VacancyForm
from .models import (
    CompanyInfo, Contact, FAQ, News, PromoCode, Review, Vacancy,
)
from .services import fetch_currency_rates, fetch_random_quote

logger = logging.getLogger('main')


def _is_superuser(user):
    return user.is_authenticated and user.is_superuser


# --- Public pages -----------------------------------------------------------

def home(request):
    """Главная страница — последняя новость + цитата дня + курсы валют."""
    latest = News.objects.order_by('-published_at').first()
    quote = fetch_random_quote()
    rates = fetch_currency_rates()
    logger.info('Home page rendered (latest=%s)', latest.pk if latest else None)
    return render(request, 'main/home.html', {
        'latest_news': latest,
        'quote': quote,
        'rates': rates,
    })


def about(request):
    info = CompanyInfo.objects.first()
    return render(request, 'main/about.html', {'info': info})


def privacy(request):
    return render(request, 'main/privacy.html')


def contacts_list(request):
    contacts = Contact.objects.all()
    return render(request, 'main/contacts.html', {'contacts': contacts})


def faq_list(request):
    q = request.GET.get('q', '').strip()
    qs = FAQ.objects.all()
    if q:
        qs = qs.filter(question__icontains=q) | qs.filter(answer__icontains=q)
    sort = request.GET.get('sort', '-added_at')
    if sort in ('question', '-question', 'added_at', '-added_at'):
        qs = qs.order_by(sort)
    return render(request, 'main/faq.html', {'faqs': qs, 'q': q, 'sort': sort})


@user_passes_test(_is_superuser)
def faq_create(request):
    form = FAQForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Термин добавлен')
        return redirect('main:faq')
    return render(request, 'main/faq_form.html', {'form': form, 'mode': 'create'})


@user_passes_test(_is_superuser)
def faq_update(request, pk):
    item = get_object_or_404(FAQ, pk=pk)
    form = FAQForm(request.POST or None, instance=item)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Термин обновлён')
        return redirect('main:faq')
    return render(request, 'main/faq_form.html', {'form': form, 'mode': 'update', 'item': item})


@user_passes_test(_is_superuser)
def faq_delete(request, pk):
    item = get_object_or_404(FAQ, pk=pk)
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Термин удалён')
        return redirect('main:faq')
    return render(request, 'main/confirm_delete.html', {
        'object': item, 'cancel_url': reverse('main:faq'),
    })


# --- News CRUD --------------------------------------------------------------

def news_list(request):
    q = request.GET.get('q', '').strip()
    sort = request.GET.get('sort', '-published_at')
    qs = News.objects.all()
    if q:
        qs = qs.filter(title__icontains=q) | qs.filter(summary__icontains=q)
    if sort in ('title', '-title', 'published_at', '-published_at'):
        qs = qs.order_by(sort)
    return render(request, 'main/news_list.html', {
        'news_items': qs,
        'q': q,
        'sort': sort,
    })


def news_detail(request, pk):
    item = get_object_or_404(News, pk=pk)
    return render(request, 'main/news_detail.html', {'item': item})


@user_passes_test(_is_superuser)
def news_create(request):
    form = NewsForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        item = form.save(commit=False)
        item.author = request.user
        item.save()
        logger.info('News created by %s: %s', request.user, item.title)
        messages.success(request, 'Новость создана')
        return redirect('main:news_detail', pk=item.pk)
    return render(request, 'main/news_form.html', {'form': form, 'mode': 'create'})


@user_passes_test(_is_superuser)
def news_update(request, pk):
    item = get_object_or_404(News, pk=pk)
    form = NewsForm(request.POST or None, request.FILES or None, instance=item)
    if request.method == 'POST' and form.is_valid():
        form.save()
        logger.info('News updated by %s: id=%s', request.user, item.pk)
        messages.success(request, 'Новость обновлена')
        return redirect('main:news_detail', pk=item.pk)
    return render(request, 'main/news_form.html', {'form': form, 'mode': 'update', 'item': item})


@user_passes_test(_is_superuser)
def news_delete(request, pk):
    item = get_object_or_404(News, pk=pk)
    if request.method == 'POST':
        logger.warning('News deleted by %s: id=%s', request.user, item.pk)
        item.delete()
        messages.success(request, 'Новость удалена')
        return redirect('main:news_list')
    return render(request, 'main/confirm_delete.html', {
        'object': item, 'cancel_url': reverse('main:news_detail', args=[item.pk]),
    })


# --- Reviews CRUD (clients only for create) ---------------------------------

def reviews_list(request):
    q = request.GET.get('q', '').strip()
    sort = request.GET.get('sort', '-created_at')
    qs = Review.objects.select_related('author').all()
    if q:
        qs = qs.filter(text__icontains=q) | qs.filter(author__username__icontains=q)
    if sort in ('rating', '-rating', 'created_at', '-created_at'):
        qs = qs.order_by(sort)
    return render(request, 'main/reviews_list.html', {
        'reviews': qs, 'q': q, 'sort': sort,
    })


@login_required
def review_create(request):
    form = ReviewForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        review = form.save(commit=False)
        review.author = request.user
        review.save()
        logger.info('Review created by %s rating=%s', request.user, review.rating)
        messages.success(request, 'Спасибо за отзыв!')
        return redirect('main:reviews_list')
    return render(request, 'main/review_form.html', {'form': form, 'mode': 'create'})


@login_required
def review_update(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if review.author != request.user and not request.user.is_superuser:
        logger.warning('Forbidden review update attempt by %s', request.user)
        return HttpResponseForbidden('Нельзя редактировать чужой отзыв')
    form = ReviewForm(request.POST or None, instance=review)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Отзыв обновлён')
        return redirect('main:reviews_list')
    return render(request, 'main/review_form.html', {'form': form, 'mode': 'update'})


@login_required
def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if review.author != request.user and not request.user.is_superuser:
        return HttpResponseForbidden('Нельзя удалить чужой отзыв')
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Отзыв удалён')
        return redirect('main:reviews_list')
    return render(request, 'main/confirm_delete.html', {
        'object': review, 'cancel_url': reverse('main:reviews_list'),
    })


# --- Vacancies CRUD ---------------------------------------------------------

def vacancies_list(request):
    q = request.GET.get('q', '').strip()
    sort = request.GET.get('sort', '-posted_at')
    qs = Vacancy.objects.all()
    if q:
        qs = qs.filter(title__icontains=q) | qs.filter(description__icontains=q)
    if sort in ('title', '-title', 'salary', '-salary', 'posted_at', '-posted_at'):
        qs = qs.order_by(sort)
    return render(request, 'main/vacancies_list.html', {
        'vacancies': qs, 'q': q, 'sort': sort,
    })


@user_passes_test(_is_superuser)
def vacancy_create(request):
    form = VacancyForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Вакансия создана')
        return redirect('main:vacancies_list')
    return render(request, 'main/vacancy_form.html', {'form': form, 'mode': 'create'})


@user_passes_test(_is_superuser)
def vacancy_update(request, pk):
    v = get_object_or_404(Vacancy, pk=pk)
    form = VacancyForm(request.POST or None, instance=v)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('main:vacancies_list')
    return render(request, 'main/vacancy_form.html', {'form': form, 'mode': 'update'})


@user_passes_test(_is_superuser)
def vacancy_delete(request, pk):
    v = get_object_or_404(Vacancy, pk=pk)
    if request.method == 'POST':
        v.delete()
        return redirect('main:vacancies_list')
    return render(request, 'main/confirm_delete.html', {
        'object': v, 'cancel_url': reverse('main:vacancies_list'),
    })


# --- PromoCode list & CRUD --------------------------------------------------

def promocodes_list(request):
    q = request.GET.get('q', '').strip()
    sort = request.GET.get('sort', '-valid_to')
    active = PromoCode.objects.filter(is_archived=False)
    archived = PromoCode.objects.filter(is_archived=True)
    if q:
        active = active.filter(code__icontains=q) | active.filter(description__icontains=q)
        archived = archived.filter(code__icontains=q) | archived.filter(description__icontains=q)
    if sort in ('code', '-code', 'valid_to', '-valid_to', 'discount_percent', '-discount_percent'):
        active = active.order_by(sort)
        archived = archived.order_by(sort)
    return render(request, 'main/promocodes_list.html', {
        'active': active, 'archived': archived, 'q': q, 'sort': sort,
    })


@user_passes_test(_is_superuser)
def promocode_create(request):
    form = PromoCodeForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('main:promocodes_list')
    return render(request, 'main/promocode_form.html', {'form': form, 'mode': 'create'})


@user_passes_test(_is_superuser)
def promocode_update(request, pk):
    p = get_object_or_404(PromoCode, pk=pk)
    form = PromoCodeForm(request.POST or None, instance=p)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('main:promocodes_list')
    return render(request, 'main/promocode_form.html', {'form': form, 'mode': 'update'})


@user_passes_test(_is_superuser)
def promocode_delete(request, pk):
    p = get_object_or_404(PromoCode, pk=pk)
    if request.method == 'POST':
        p.delete()
        return redirect('main:promocodes_list')
    return render(request, 'main/confirm_delete.html', {
        'object': p, 'cancel_url': reverse('main:promocodes_list'),
    })
