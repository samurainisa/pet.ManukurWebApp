from django.contrib import admin

from visits.models import VisitPhoto, VisitResult


@admin.register(VisitResult)
class VisitResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'appointment', 'actual_duration_min', 'updated_at')


@admin.register(VisitPhoto)
class VisitPhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'appointment', 'sort_order', 'created_at')
