from datetime import time

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from clients.models import Client
from services.models import Service

User = get_user_model()


class WorkScheduleRule(models.Model):
    WEEKDAY_CHOICES = [
        (0, 'Понедельник'),
        (1, 'Вторник'),
        (2, 'Среда'),
        (3, 'Четверг'),
        (4, 'Пятница'),
        (5, 'Суббота'),
        (6, 'Воскресенье'),
    ]

    weekday = models.PositiveSmallIntegerField(choices=WEEKDAY_CHOICES, unique=True)
    start_time = models.TimeField(default=time(9, 0))
    end_time = models.TimeField(default=time(18, 0))
    is_working_day = models.BooleanField(default=True)

    class Meta:
        ordering = ['weekday']

    def clean(self):
        if self.is_working_day and self.start_time >= self.end_time:
            raise ValidationError('Время начала должно быть раньше времени окончания.')

    def __str__(self) -> str:
        return f'weekday={self.weekday} ({self.start_time}-{self.end_time})'


class TimeOffBlock(models.Model):
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    reason = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_datetime']

    def clean(self):
        if self.start_datetime >= self.end_datetime:
            raise ValidationError('Начало блокировки должно быть раньше окончания.')

    def __str__(self) -> str:
        return f'{self.start_datetime} - {self.end_datetime}'


class Appointment(models.Model):
    class AppointmentStatus(models.TextChoices):
        CREATED = 'created', 'Создана'
        CONFIRMED = 'confirmed', 'Подтверждена'
        COMPLETED = 'completed', 'Выполнена'
        CANCELLED = 'cancelled', 'Отменена'
        RESCHEDULED = 'rescheduled', 'Перенесена'
        NO_SHOW = 'no_show', 'Неявка'

    class AppointmentSource(models.TextChoices):
        MASTER_MANUAL = 'master_manual', 'Создана мастером'
        PUBLIC_BOOKING = 'public_booking', 'Публичная запись'

    ACTIVE_SLOT_STATUSES = (
        AppointmentStatus.CREATED,
        AppointmentStatus.CONFIRMED,
        AppointmentStatus.COMPLETED,
        AppointmentStatus.RESCHEDULED,
    )

    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='appointments')
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name='appointments')
    status = models.CharField(max_length=20, choices=AppointmentStatus.choices, default=AppointmentStatus.CREATED)
    source = models.CharField(max_length=20, choices=AppointmentSource.choices, default=AppointmentSource.MASTER_MANUAL)

    appointment_date = models.DateField(db_index=True)
    start_datetime = models.DateTimeField(db_index=True)
    end_datetime = models.DateTimeField(db_index=True)
    planned_duration_min = models.PositiveIntegerField()
    planned_price = models.DecimalField(max_digits=10, decimal_places=2)

    comment_client = models.TextField(blank=True, null=True)
    comment_master = models.TextField(blank=True, null=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='created_appointments',
        blank=True,
        null=True,
    )

    needs_removal = models.BooleanField(default=False)
    needs_strengthening = models.BooleanField(default=False)
    design_notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_datetime']
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_datetime__gt=models.F('start_datetime')),
                name='appointment_end_after_start',
            )
        ]

    def save(self, *args, **kwargs):
        if self.start_datetime:
            self.appointment_date = timezone.localdate(self.start_datetime)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'Appointment #{self.pk} - {self.client.full_name}'
