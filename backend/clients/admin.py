from django.contrib import admin

from clients.models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'phone', 'email', 'created_at')
    search_fields = ('full_name', 'phone', 'email')
    list_filter = ('created_at',)
