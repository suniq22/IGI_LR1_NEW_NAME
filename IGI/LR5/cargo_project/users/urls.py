"""URL patterns for users app."""
from django.contrib.auth import views as auth_views
from django.urls import re_path

from . import views

app_name = 'users'

urlpatterns = [
    re_path(r'^login/$', auth_views.LoginView.as_view(
        template_name='registration/login.html'), name='login'),
    re_path(r'^logout/$', auth_views.LogoutView.as_view(
        next_page='/'), name='logout'),
    re_path(r'^signup/$', views.signup, name='signup'),
    re_path(r'^profile/$', views.profile, name='profile'),
    re_path(r'^profile/edit/$', views.profile_update, name='profile_update'),
]
