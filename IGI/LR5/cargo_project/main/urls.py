"""URL patterns for the main app — uses regex via re_path."""
from django.urls import re_path

from . import views

app_name = 'main'

urlpatterns = [
    re_path(r'^$', views.home, name='home'),
    re_path(r'^about/$', views.about, name='about'),
    re_path(r'^privacy/$', views.privacy, name='privacy'),
    re_path(r'^contacts/$', views.contacts_list, name='contacts'),
    re_path(r'^faq/$', views.faq_list, name='faq'),
    re_path(r'^faq/create/$', views.faq_create, name='faq_create'),
    re_path(r'^faq/(?P<pk>\d+)/edit/$', views.faq_update, name='faq_update'),
    re_path(r'^faq/(?P<pk>\d+)/delete/$', views.faq_delete, name='faq_delete'),

    # News
    re_path(r'^news/$', views.news_list, name='news_list'),
    re_path(r'^news/create/$', views.news_create, name='news_create'),
    re_path(r'^news/(?P<pk>\d+)/$', views.news_detail, name='news_detail'),
    re_path(r'^news/(?P<pk>\d+)/edit/$', views.news_update, name='news_update'),
    re_path(r'^news/(?P<pk>\d+)/delete/$', views.news_delete, name='news_delete'),

    # Reviews
    re_path(r'^reviews/$', views.reviews_list, name='reviews_list'),
    re_path(r'^reviews/create/$', views.review_create, name='review_create'),
    re_path(r'^reviews/(?P<pk>\d+)/edit/$', views.review_update, name='review_update'),
    re_path(r'^reviews/(?P<pk>\d+)/delete/$', views.review_delete, name='review_delete'),

    # Vacancies
    re_path(r'^vacancies/$', views.vacancies_list, name='vacancies_list'),
    re_path(r'^vacancies/create/$', views.vacancy_create, name='vacancy_create'),
    re_path(r'^vacancies/(?P<pk>\d+)/edit/$', views.vacancy_update, name='vacancy_update'),
    re_path(r'^vacancies/(?P<pk>\d+)/delete/$', views.vacancy_delete, name='vacancy_delete'),

    # Promo codes
    re_path(r'^promocodes/$', views.promocodes_list, name='promocodes_list'),
    re_path(r'^promocodes/create/$', views.promocode_create, name='promocode_create'),
    re_path(r'^promocodes/(?P<pk>\d+)/edit/$', views.promocode_update, name='promocode_update'),
    re_path(r'^promocodes/(?P<pk>\d+)/delete/$', views.promocode_delete, name='promocode_delete'),
]
