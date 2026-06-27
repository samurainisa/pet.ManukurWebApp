from django.contrib import admin

from services.models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'base_duration_min', 'base_price', 'is_active', 'sort_order')
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('sort_order', 'name')
