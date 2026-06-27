from django.urls import path

from payments.views import AppointmentPaymentView

urlpatterns = [
    path('appointments/<int:appointment_id>/payment/', AppointmentPaymentView.as_view(), name='appointments-payment'),
]
