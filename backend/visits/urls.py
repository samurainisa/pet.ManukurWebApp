from django.urls import path

from visits.views import AppointmentPhotoDeleteView, AppointmentPhotoUploadView, AppointmentResultView

urlpatterns = [
    path('appointments/<int:appointment_id>/result/', AppointmentResultView.as_view(), name='appointments-result'),
    path('appointments/<int:appointment_id>/photos/', AppointmentPhotoUploadView.as_view(), name='appointments-photos-upload'),
    path(
        'appointments/<int:appointment_id>/photos/<int:photo_id>/',
        AppointmentPhotoDeleteView.as_view(),
        name='appointments-photos-delete',
    ),
]
