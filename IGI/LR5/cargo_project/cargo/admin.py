from django.contrib import admin

from .models import (
    BodyType, CargoType, Client, Driver, Order, Organization, Service,
    Vehicle, VehicleType,
)


class OrderInline(admin.TabularInline):
    model = Order
    extra = 0
    fields = ('cargo_name', 'cargo_type', 'status', 'scheduled_at', 'distance_km')
    show_change_link = True


@admin.register(VehicleType)
class VehicleTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(BodyType)
class BodyTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(CargoType)
class CargoTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_dangerous')
    list_filter = ('is_dangerous',)
    search_fields = ('name',)


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'phone', 'license_number', 'hired_at')
    list_filter = ('hired_at',)
    search_fields = ('last_name', 'first_name', 'license_number', 'phone')
    inlines = [OrderInline]


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('brand', 'model', 'plate_number', 'vehicle_type',
                    'body_type', 'capacity_tons', 'year', 'driver')
    list_filter = ('vehicle_type', 'body_type', 'year')
    search_fields = ('brand', 'model', 'plate_number')


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'inn', 'phone', 'email')
    search_fields = ('name', 'inn', 'email')


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'phone', 'organization')
    list_filter = ('organization',)
    search_fields = ('last_name', 'first_name', 'phone')
    inlines = [OrderInline]


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_per_km', 'is_additional')
    list_filter = ('is_additional', 'suitable_cargo')
    search_fields = ('name',)
    filter_horizontal = ('suitable_cargo',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'cargo_name', 'cargo_type', 'client', 'driver',
                    'vehicle', 'status', 'scheduled_at', 'distance_km')
    list_filter = ('status', 'cargo_type', 'scheduled_at')
    search_fields = ('cargo_name', 'client__last_name', 'driver__last_name')
    filter_horizontal = ('services',)
    date_hierarchy = 'scheduled_at'
    autocomplete_fields = ('client', 'driver', 'vehicle', 'cargo_type', 'promo_code')
