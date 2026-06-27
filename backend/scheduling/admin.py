from django.contrib import admin

from scheduling.models import Appointment, TimeOffBlock, WorkScheduleRule


@admin.register(WorkScheduleRule)
class WorkScheduleRuleAdmin(admin.ModelAdmin):
    list_display = ('weekday', 'is_working_day', 'start_time', 'end_time')
    list_editable = ('is_working_day', 'start_time', 'end_time')
    ordering = ('weekday',)


@admin.register(TimeOffBlock)
class TimeOffBlockAdmin(admin.ModelAdmin):
    list_display = ('id', 'start_datetime', 'end_datetime', 'reason')
    search_fields = ('reason',)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'service', 'status', 'source', 'start_datetime', 'end_datetime')
    list_filter = ('status', 'source', 'appointment_date')
    search_fields = ('client__full_name', 'client__phone', 'service__name')
