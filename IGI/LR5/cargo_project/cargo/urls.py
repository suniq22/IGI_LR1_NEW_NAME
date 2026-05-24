"""URL patterns for the cargo app — uses regex via re_path."""
from django.urls import re_path

from . import views

app_name = 'cargo'

urlpatterns = [
    # Vehicles
    re_path(r'^vehicles/$', views.vehicles_list, name='vehicles_list'),
    re_path(r'^vehicles/create/$', views.vehicle_create, name='vehicle_create'),
    re_path(r'^vehicles/(?P<pk>\d+)/$', views.vehicles_detail, name='vehicles_detail'),
    re_path(r'^vehicles/(?P<pk>\d+)/edit/$', views.vehicle_update, name='vehicle_update'),
    re_path(r'^vehicles/(?P<pk>\d+)/delete/$', views.vehicle_delete, name='vehicle_delete'),

    # Drivers
    re_path(r'^drivers/$', views.drivers_list, name='drivers_list'),
    re_path(r'^drivers/(?P<pk>\d+)/edit/$', views.driver_update, name='driver_update'),
    re_path(r'^drivers/(?P<pk>\d+)/delete/$', views.driver_delete, name='driver_delete'),

    # Services
    re_path(r'^services/$', views.services_list, name='services_list'),
    re_path(r'^services/create/$', views.service_create, name='service_create'),
    re_path(r'^services/(?P<pk>\d+)/edit/$', views.service_update, name='service_update'),
    re_path(r'^services/(?P<pk>\d+)/delete/$', views.service_delete, name='service_delete'),

    # Orders
    re_path(r'^orders/$', views.orders_list, name='orders_list'),
    re_path(r'^orders/create/$', views.order_create, name='order_create'),
    re_path(r'^orders/(?P<pk>\d+)/$', views.order_detail, name='order_detail'),
    re_path(r'^orders/(?P<pk>\d+)/edit/$', views.order_update, name='order_update'),
    re_path(r'^orders/(?P<pk>\d+)/delete/$', views.order_delete, name='order_delete'),

    # Statistics
    re_path(r'^statistics/$', views.statistics_view, name='statistics'),
]
