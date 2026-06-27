from datetime import date, datetime, timedelta

from django.utils import timezone
from rest_framework import serializers

from scheduling.models import Appointment
from scheduling.serializers import AppointmentSerializer, AvailableSlotsQuerySerializer
from scheduling.slot_service import has_overlap, has_time_off_overlap, is_inside_working_hours
from services.models import Service
from users.models import UserProfile


class ClientBookingSerializer(serializers.Serializer):
    service_id = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.filter(is_active=True),
        source='service',
        error_messages={
            'required': 'Выберите услугу.',
            'does_not_exist': 'Выбранная услуга не найдена или отключена.',
        },
    )
    date = serializers.DateField(
        error_messages={
            'required': 'Укажите дату записи.',
            'invalid': 'Некорректный формат даты.',
        }
    )
    time = serializers.TimeField(
        error_messages={
            'required': 'Укажите время записи.',
            'invalid': 'Некорректный формат времени.',
        }
    )
    comment = serializers.CharField(required=False, allow_blank=True, max_length=2000)

    def validate(self, attrs):
        profile: UserProfile = self.context['profile']
        if not profile.client_id:
            raise serializers.ValidationError(
                'Профиль клиента не привязан к карточке клиента.'
            )

        service: Service = attrs['service']
        day: date = attrs['date']
        time_value = attrs['time']

        tz = timezone.get_current_timezone()
        start_datetime = timezone.make_aware(datetime.combine(day, time_value), tz)
        end_datetime = start_datetime + timedelta(minutes=service.base_duration_min)

        if day < timezone.localdate():
            raise serializers.ValidationError({'date': ['Дата записи не может быть в прошлом.']})
        if end_datetime <= timezone.now():
            raise serializers.ValidationError({'time': ['Выбранное время уже прошло.']})
        if not is_inside_working_hours(start_datetime, end_datetime):
            raise serializers.ValidationError({'time': ['Выбранный слот вне рабочего времени.']})
        if has_time_off_overlap(start_datetime, end_datetime):
            raise serializers.ValidationError({'time': ['Слот недоступен из-за блокировки времени.']})
        if has_overlap(start_datetime, end_datetime):
            raise serializers.ValidationError({'time': ['Выбранный слот уже занят.']})

        attrs['start_datetime'] = start_datetime
        attrs['end_datetime'] = end_datetime
        return attrs

    def create(self, validated_data):
        profile: UserProfile = self.context['profile']
        service = validated_data['service']

        return Appointment.objects.create(
            client=profile.client,
            service=service,
            status=Appointment.AppointmentStatus.CREATED,
            source=Appointment.AppointmentSource.PUBLIC_BOOKING,
            start_datetime=validated_data['start_datetime'],
            end_datetime=validated_data['end_datetime'],
            planned_duration_min=service.base_duration_min,
            planned_price=service.base_price,
            comment_client=(validated_data.get('comment', '') or '').strip() or None,
        )


class ClientNotificationItemSerializer(serializers.Serializer):
    appointment_id = serializers.IntegerField()
    type = serializers.ChoiceField(choices=['info', 'warning', 'success'])
    title = serializers.CharField()
    message = serializers.CharField()
    start_datetime = serializers.DateTimeField(allow_null=True)


class ClientAppointmentsSerializer(serializers.Serializer):
    items = AppointmentSerializer(many=True)


class ClientAvailableSlotsSerializer(AvailableSlotsQuerySerializer):
    pass
