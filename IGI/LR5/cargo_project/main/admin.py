from django.contrib import admin

from .models import CompanyInfo, Contact, FAQ, News, PromoCode, Review, Vacancy


@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ('title', 'updated_at')


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published_at', 'created_at')
    list_filter = ('published_at', 'author')
    search_fields = ('title', 'summary', 'content')
    date_hierarchy = 'published_at'


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('question', 'answer')


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'position', 'phone', 'email')
    search_fields = ('full_name', 'position', 'email')


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'salary', 'is_active', 'posted_at')
    list_filter = ('is_active', 'posted_at')
    search_fields = ('title', 'description')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('text', 'author__username')


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'valid_from', 'valid_to', 'is_archived')
    list_filter = ('is_archived', 'valid_to')
    search_fields = ('code', 'description')
