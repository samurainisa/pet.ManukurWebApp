from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from payments.models import Payment
from payments.serializers import PaymentSerializer
from scheduling.models import Appointment
from users.permissions import IsMasterRole


class AppointmentPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsMasterRole]

    def get(self, request, appointment_id: int):
        appointment = get_object_or_404(Appointment, pk=appointment_id)
        payment = Payment.objects.filter(appointment=appointment).first()
        if not payment:
            return Response(
                {
                    'appointment': appointment.id,
                    'amount': str(appointment.planned_price),
                    'payment_method': Payment.PaymentMethod.CASH,
                    'payment_status': Payment.PaymentStatus.UNPAID,
                    'paid_at': None,
                    'comment': '',
                }
            )
        return Response(PaymentSerializer(payment).data)

    def put(self, request, appointment_id: int):
        appointment = get_object_or_404(Appointment, pk=appointment_id)
        payment, _ = Payment.objects.get_or_create(
            appointment=appointment,
            defaults={'amount': appointment.planned_price},
        )

        serializer = PaymentSerializer(payment, data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(appointment=appointment)

        if instance.payment_status == Payment.PaymentStatus.PAID and not instance.paid_at:
            instance.paid_at = timezone.now()
            instance.save(update_fields=['paid_at', 'updated_at'])

        return Response(PaymentSerializer(instance).data, status=status.HTTP_200_OK)
