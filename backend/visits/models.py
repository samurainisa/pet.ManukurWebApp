from django.db import models

from scheduling.models import Appointment


class VisitResult(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='result')
    actual_service_summary = models.TextField(blank=True, null=True)
    materials_used = models.TextField(blank=True, null=True)
    result_notes = models.TextField(blank=True, null=True)
    actual_duration_min = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'Result for appointment #{self.appointment_id}'


class VisitPhoto(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='visit_photos/%Y/%m/%d/')
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', 'id']

    def __str__(self) -> str:
        return f'Photo #{self.pk} for appointment #{self.appointment_id}'
