from django.contrib import admin

from payments.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'appointment', 'amount', 'payment_method', 'payment_status', 'paid_at')
    list_filter = ('payment_status', 'payment_method')
