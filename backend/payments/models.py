from django.core.validators import MinValueValidator
from django.db import models

from scheduling.models import Appointment


class Payment(models.Model):
    class PaymentMethod(models.TextChoices):
        CASH = 'cash', 'Наличные'
        TRANSFER = 'transfer', 'Перевод'
        CARD_MANUAL = 'card_manual', 'Карта (вручную)'

    class PaymentStatus(models.TextChoices):
        UNPAID = 'unpaid', 'Не оплачено'
        PAID = 'paid', 'Оплачено'
        PARTIAL = 'partial', 'Частично'

    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.CASH)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.UNPAID)
    paid_at = models.DateTimeField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'Payment for appointment #{self.appointment_id}'
