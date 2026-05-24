from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'birth_date', 'timezone')
    list_filter = ('role', 'timezone')
    search_fields = ('user__username', 'user__email', 'phone')
