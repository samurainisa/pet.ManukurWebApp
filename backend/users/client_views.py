from datetime import timedelta

from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from scheduling.models import Appointment
from scheduling.serializers import AppointmentSerializer
from scheduling.slot_service import generate_available_slots
from users.client_serializers import (
    ClientAvailableSlotsSerializer,
    ClientBookingSerializer,
    ClientNotificationItemSerializer,
)
from users.permissions import IsClientRole


class ClientProfileMixin:
    permission_classes = [permissions.IsAuthenticated, IsClientRole]

    def get_profile(self, request):
        profile = getattr(request.user, 'profile', None)
        if not profile or not profile.client_id:
            return None
        return profile


class ClientAvailableSlotsView(ClientProfileMixin, APIView):
    def get(self, request):
        profile = self.get_profile(request)
        if not profile:
            return Response(
                {'detail': 'Профиль клиента не заполнен.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ClientAvailableSlotsSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        service = serializer.validated_data['service']
        day = serializer.validated_data['date']
        slots = generate_available_slots(day, service.base_duration_min)

        return Response(
            {
                'service_id': service.id,
                'date': day,
                'slots': [slot.isoformat() for slot in slots],
            }
        )


class ClientBookingsView(ClientProfileMixin, APIView):
    def get(self, request):
        profile = self.get_profile(request)
        if not profile:
            return Response(
                {'detail': 'Профиль клиента не заполнен.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = (
            Appointment.objects.filter(client_id=profile.client_id)
            .select_related('client', 'service', 'payment')
            .prefetch_related('photos')
            .order_by('-start_datetime')
        )
        return Response({'items': AppointmentSerializer(queryset, many=True).data})

    def post(self, request):
        profile = self.get_profile(request)
        if not profile:
            return Response(
                {'detail': 'Профиль клиента не заполнен.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ClientBookingSerializer(data=request.data, context={'profile': profile})
        serializer.is_valid(raise_exception=True)
        appointment = serializer.save()
        return Response(AppointmentSerializer(appointment).data, status=status.HTTP_201_CREATED)


class ClientNotificationsView(ClientProfileMixin, APIView):
    def get(self, request):
        profile = self.get_profile(request)
        if not profile:
            return Response(
                {'detail': 'Профиль клиента не заполнен.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        now = timezone.now()
        soon_border = now + timedelta(hours=48)
        window_start = timezone.localdate() - timedelta(days=30)

        appointments = (
            Appointment.objects.filter(client_id=profile.client_id, appointment_date__gte=window_start)
            .select_related('service')
            .order_by('-start_datetime')[:40]
        )

        notifications = []
        for appointment in appointments:
            title = ''
            message = ''
            level = 'info'

            if appointment.status in {
                Appointment.AppointmentStatus.CREATED,
                Appointment.AppointmentStatus.CONFIRMED,
                Appointment.AppointmentStatus.RESCHEDULED,
            } and now <= appointment.start_datetime <= soon_border:
                title = 'Ближайший визит'
                message = (
                    f'Напоминание: {appointment.service.name} '
                    f'{timezone.localtime(appointment.start_datetime):%d.%m %H:%M}.'
                )
                level = 'info'
            elif appointment.status == Appointment.AppointmentStatus.CANCELLED:
                title = 'Запись отменена'
                message = f'Запись на {appointment.service.name} была отменена.'
                level = 'warning'
            elif appointment.status == Appointment.AppointmentStatus.NO_SHOW:
                title = 'Неявка'
                message = f'Визит на {appointment.service.name} отмечен как неявка.'
                level = 'warning'
            elif appointment.status == Appointment.AppointmentStatus.COMPLETED:
                title = 'Визит выполнен'
                message = f'Спасибо за визит: {appointment.service.name}.'
                level = 'success'

            if title:
                notifications.append(
                    {
                        'appointment_id': appointment.id,
                        'type': level,
                        'title': title,
                        'message': message,
                        'start_datetime': appointment.start_datetime,
                    }
                )

        payload = ClientNotificationItemSerializer(notifications, many=True).data
        return Response({'items': payload})
