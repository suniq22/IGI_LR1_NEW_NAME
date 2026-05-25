"""FBV-based views for cargo domain: drivers, vehicles, services, orders, stats."""
import logging
import statistics
from collections import Counter
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from main.services import render_chart_png_base64

from .forms import (
    ClientOrderForm, DriverForm, OrderForm, OrganizationForm, ServiceForm,
    VehicleForm,
)
from .models import (
    BodyType, CargoType, Client, Driver, Order, Organization, Service,
    Vehicle, VehicleType,
)

logger = logging.getLogger('cargo')


def _is_superuser(user):
    return user.is_authenticated and user.is_superuser


def _is_driver(user):
    return user.is_authenticated and (
        user.is_superuser or hasattr(user, 'driver_profile')
        or (hasattr(user, 'profile') and user.profile.role == 'driver')
    )


def _is_client(user):
    return user.is_authenticated and (
        user.is_superuser or hasattr(user, 'client_profile')
        or (hasattr(user, 'profile') and user.profile.role == 'client')
    )


# --- Public catalogs --------------------------------------------------------

def vehicles_list(request):
    q = request.GET.get('q', '').strip()
    sort = request.GET.get('sort', 'brand')
    qs = Vehicle.objects.select_related('vehicle_type', 'body_type', 'driver').all()
    if q:
        qs = qs.filter(
            Q(brand__icontains=q) | Q(model__icontains=q)
            | Q(plate_number__icontains=q) | Q(vehicle_type__name__icontains=q)
        )
    if sort in ('brand', '-brand', 'capacity_tons', '-capacity_tons', 'year', '-year'):
        qs = qs.order_by(sort)
    return render(request, 'cargo/vehicles_list.html', {
        'vehicles': qs, 'q': q, 'sort': sort,
    })


def vehicles_detail(request, pk):
    v = get_object_or_404(Vehicle, pk=pk)
    return render(request, 'cargo/vehicle_detail.html', {'v': v})


def drivers_list(request):
    q = request.GET.get('q', '').strip()
    sort = request.GET.get('sort', 'last_name')
    qs = Driver.objects.all()
    if q:
        qs = qs.filter(
            Q(first_name__icontains=q) | Q(last_name__icontains=q)
            | Q(license_number__icontains=q)
        )
    if sort in ('first_name', '-first_name', 'last_name', '-last_name',
                'hired_at', '-hired_at'):
        qs = qs.order_by(sort)
    return render(request, 'cargo/drivers_list.html', {
        'drivers': qs, 'q': q, 'sort': sort,
    })


def services_list(request):
    q = request.GET.get('q', '').strip()
    sort = request.GET.get('sort', 'name')
    category = request.GET.get('category', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    qs = Service.objects.prefetch_related('suitable_cargo').all()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
    if category:
        qs = qs.filter(suitable_cargo__name__icontains=category)
    if max_price:
        try:
            qs = qs.filter(price_per_km__lte=Decimal(max_price))
        except Exception:  # noqa: BLE001
            pass
    if sort in ('name', '-name', 'price_per_km', '-price_per_km'):
        qs = qs.order_by(sort)
    return render(request, 'cargo/services_list.html', {
        'services': qs.distinct(), 'q': q, 'sort': sort,
        'category': category, 'max_price': max_price,
    })


# --- Service CRUD (admin only) ---------------------------------------------

@user_passes_test(_is_superuser)
def service_create(request):
    form = ServiceForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        logger.info('Service created: %s', form.instance.name)
        messages.success(request, 'Услуга создана')
        return redirect('cargo:services_list')
    return render(request, 'cargo/service_form.html', {'form': form, 'mode': 'create'})


@user_passes_test(_is_superuser)
def service_update(request, pk):
    s = get_object_or_404(Service, pk=pk)
    form = ServiceForm(request.POST or None, instance=s)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('cargo:services_list')
    return render(request, 'cargo/service_form.html', {'form': form, 'mode': 'update'})


@user_passes_test(_is_superuser)
def service_delete(request, pk):
    s = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        s.delete()
        return redirect('cargo:services_list')
    return render(request, 'main/confirm_delete.html', {
        'object': s, 'cancel_url': reverse('cargo:services_list'),
    })


# --- Vehicle CRUD (admin only) ----------------------------------------------

@user_passes_test(_is_superuser)
def vehicle_create(request):
    form = VehicleForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('cargo:vehicles_list')
    return render(request, 'cargo/vehicle_form.html', {'form': form, 'mode': 'create'})


@user_passes_test(_is_superuser)
def vehicle_update(request, pk):
    v = get_object_or_404(Vehicle, pk=pk)
    form = VehicleForm(request.POST or None, instance=v)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('cargo:vehicles_detail', pk=v.pk)
    return render(request, 'cargo/vehicle_form.html', {'form': form, 'mode': 'update'})


@user_passes_test(_is_superuser)
def vehicle_delete(request, pk):
    v = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        v.delete()
        return redirect('cargo:vehicles_list')
    return render(request, 'main/confirm_delete.html', {
        'object': v, 'cancel_url': reverse('cargo:vehicles_list'),
    })


# --- Driver CRUD (admin only) -----------------------------------------------

@user_passes_test(_is_superuser)
def driver_create(request):
    form = DriverForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        driver = form.save()
        logger.info('Driver created: %s by %s', driver, request.user)
        messages.success(request, f'Водитель {driver} создан')
        return redirect('cargo:drivers_list')
    return render(request, 'cargo/driver_form.html', {'form': form, 'mode': 'create'})


@user_passes_test(_is_superuser)
def driver_update(request, pk):
    d = get_object_or_404(Driver, pk=pk)
    form = DriverForm(request.POST or None, instance=d)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('cargo:drivers_list')
    return render(request, 'cargo/driver_form.html', {'form': form, 'mode': 'update'})


@user_passes_test(_is_superuser)
def driver_delete(request, pk):
    d = get_object_or_404(Driver, pk=pk)
    if request.method == 'POST':
        d.delete()
        return redirect('cargo:drivers_list')
    return render(request, 'main/confirm_delete.html', {
        'object': d, 'cancel_url': reverse('cargo:drivers_list'),
    })


# --- Orders ---------------------------------------------------------------

@login_required
def orders_list(request):
    """Admin sees all orders. Driver sees their own. Client sees their own."""
    user = request.user
    q = request.GET.get('q', '').strip()
    sort = request.GET.get('sort', '-scheduled_at')
    qs = Order.objects.select_related(
        'client', 'driver', 'vehicle', 'cargo_type', 'promo_code'
    ).all()
    if not user.is_superuser:
        if hasattr(user, 'driver_profile'):
            qs = qs.filter(driver=user.driver_profile)
        elif hasattr(user, 'client_profile'):
            qs = qs.filter(client=user.client_profile)
        else:
            qs = qs.none()
    if q:
        qs = qs.filter(
            Q(cargo_name__icontains=q) | Q(cargo_type__name__icontains=q)
            | Q(status__icontains=q)
        )
    if sort in ('scheduled_at', '-scheduled_at', 'status', '-status',
                'distance_km', '-distance_km'):
        qs = qs.order_by(sort)
    return render(request, 'cargo/orders_list.html', {
        'orders': qs, 'q': q, 'sort': sort,
    })


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    user = request.user
    allowed = (
        user.is_superuser
        or (hasattr(user, 'driver_profile') and order.driver_id == user.driver_profile.id)
        or (hasattr(user, 'client_profile') and order.client_id == user.client_profile.id)
    )
    if not allowed:
        return HttpResponseForbidden('Нет доступа к этому заказу')
    return render(request, 'cargo/order_detail.html', {'order': order})


@login_required
def order_create(request):
    """Clients book their own orders; admin creates any order."""
    user = request.user
    if user.is_superuser:
        form = OrderForm(request.POST or None)
        if request.method == 'POST' and form.is_valid():
            form.save_m2m_required = True
            order = form.save()
            logger.info('Order created by admin id=%s', order.pk)
            return redirect('cargo:order_detail', pk=order.pk)
        return render(request, 'cargo/order_form.html', {'form': form, 'mode': 'create'})

    if not hasattr(user, 'client_profile'):
        return HttpResponseForbidden('Заказ может оформить только клиент')

    form = ClientOrderForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        order = form.save(commit=False)
        order.client = user.client_profile
        order.save()
        form.save_m2m()
        logger.info('Order booked by client %s id=%s', user.username, order.pk)
        messages.success(request, 'Заказ оформлен!')
        return redirect('cargo:order_detail', pk=order.pk)
    return render(request, 'cargo/order_form.html', {'form': form, 'mode': 'create'})


@login_required
def order_update(request, pk):
    order = get_object_or_404(Order, pk=pk)
    user = request.user
    if not user.is_superuser and not (
        hasattr(user, 'client_profile') and order.client_id == user.client_profile.id
    ):
        return HttpResponseForbidden('Нельзя редактировать чужой заказ')
    FormCls = OrderForm if user.is_superuser else ClientOrderForm
    form = FormCls(request.POST or None, instance=order)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('cargo:order_detail', pk=order.pk)
    return render(request, 'cargo/order_form.html', {'form': form, 'mode': 'update'})


@login_required
def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    user = request.user
    if not user.is_superuser and not (
        hasattr(user, 'client_profile') and order.client_id == user.client_profile.id
    ):
        return HttpResponseForbidden('Нельзя удалить чужой заказ')
    if request.method == 'POST':
        order.delete()
        return redirect('cargo:orders_list')
    return render(request, 'main/confirm_delete.html', {
        'object': order, 'cancel_url': reverse('cargo:order_detail', args=[order.pk]),
    })


# --- Statistics & chart -----------------------------------------------------

@user_passes_test(_is_superuser)
def statistics_view(request):
    """Aggregate statistics: averages, popular cargo type, total revenue, chart."""
    orders = list(Order.objects.select_related('cargo_type').prefetch_related('services').all())
    totals = [o.total_price for o in orders]
    revenue = round(sum(totals), 2)

    avg = round(statistics.mean(totals), 2) if totals else 0
    median = round(statistics.median(totals), 2) if totals else 0
    try:
        mode = statistics.mode(totals) if totals else 0
    except statistics.StatisticsError:
        mode = totals[0] if totals else 0

    clients = list(Client.objects.all())
    ages = [c.age for c in clients]
    avg_age = round(statistics.mean(ages), 2) if ages else 0
    median_age = statistics.median(ages) if ages else 0

    counter = Counter(o.cargo_type.name for o in orders)
    popular_cargo = counter.most_common(1)[0][0] if counter else '—'

    revenue_by_cargo: dict = {}
    for o in orders:
        revenue_by_cargo[o.cargo_type.name] = (
            revenue_by_cargo.get(o.cargo_type.name, 0) + o.total_price
        )
    if revenue_by_cargo:
        best_cargo = max(revenue_by_cargo, key=revenue_by_cargo.get)
    else:
        best_cargo = '—'

    chart_b64 = ''
    if revenue_by_cargo:
        chart_b64 = render_chart_png_base64(
            list(revenue_by_cargo.keys()),
            [round(v, 2) for v in revenue_by_cargo.values()],
            title='Выручка по видам груза',
            ylabel='BYN',
        )

    clients_alpha = Client.objects.order_by('last_name', 'first_name')

    return render(request, 'cargo/statistics.html', {
        'revenue': revenue,
        'avg': avg, 'median': median, 'mode': mode,
        'avg_age': avg_age, 'median_age': median_age,
        'popular_cargo': popular_cargo,
        'best_cargo': best_cargo,
        'chart_b64': chart_b64,
        'clients_alpha': clients_alpha,
        'orders_count': len(orders),
    })
