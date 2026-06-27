import re
from datetime import date, datetime, timedelta
from decimal import Decimal

from django.utils import timezone
from rest_framework import serializers

from clients.models import Client
from scheduling.models import Appointment, TimeOffBlock, WorkScheduleRule
from scheduling.slot_service import has_overlap, has_time_off_overlap, is_inside_working_hours
from services.models import Service

PHONE_PATTERN = re.compile(r'^\+?[0-9()\-\s]{7,20}$')


class WorkScheduleRuleSerializer(serializers.ModelSerializer):
    start_time = serializers.TimeField(
        error_messages={
            'required': 'Укажите время начала рабочего дня.',
            'invalid': 'Некорректный формат времени начала.',
        }
    )
    end_time = serializers.TimeField(
        error_messages={
            'required': 'Укажите время окончания рабочего дня.',
            'invalid': 'Некорректный формат времени окончания.',
        }
    )

    class Meta:
        model = WorkScheduleRule
        fields = ['id', 'weekday', 'start_time', 'end_time', 'is_working_day']

    def validate(self, attrs):
        if attrs.get('is_working_day', True):
            start_time = attrs.get('start_time', self.instance.start_time if self.instance else None)
            end_time = attrs.get('end_time', self.instance.end_time if self.instance else None)
            if start_time and end_time and start_time >= end_time:
                raise serializers.ValidationError('Время начала должно быть раньше времени окончания.')
        return attrs


class TimeOffBlockSerializer(serializers.ModelSerializer):
    start_datetime = serializers.DateTimeField(
        error_messages={
            'required': 'Укажите начало блокировки.',
            'invalid': 'Некорректная дата и время начала блокировки.',
        }
    )
    end_datetime = serializers.DateTimeField(
        error_messages={
            'required': 'Укажите окончание блокировки.',
            'invalid': 'Некорректная дата и время окончания блокировки.',
        }
    )
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=255,
        error_messages={'max_length': 'Причина не должна превышать 255 символов.'},
    )

    class Meta:
        model = TimeOffBlock
        fields = ['id', 'start_datetime', 'end_datetime', 'reason', 'created_at']
        read_only_fields = ['created_at']

    def validate(self, attrs):
        start = attrs.get('start_datetime', self.instance.start_datetime if self.instance else None)
        end = attrs.get('end_datetime', self.instance.end_datetime if self.instance else None)

        if start and end and start >= end:
            raise serializers.ValidationError('Начало блокировки должно быть раньше окончания.')
        if start and end and has_overlap(start, end):
            raise serializers.ValidationError('Нельзя блокировать время, где уже есть активная запись.')

        return attrs


class AppointmentSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(),
        error_messages={
            'required': 'Выберите клиента.',
            'null': 'Выберите клиента.',
            'does_not_exist': 'Выбранный клиент не найден.',
            'incorrect_type': 'Выберите клиента из списка.',
        },
    )
    service = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(),
        error_messages={
            'required': 'Выберите услугу.',
            'null': 'Выберите услугу.',
            'does_not_exist': 'Выбранная услуга не найдена.',
            'incorrect_type': 'Выберите услугу из списка.',
        },
    )
    start_datetime = serializers.DateTimeField(
        error_messages={
            'required': 'Укажите дату и время записи.',
            'invalid': 'Некорректная дата и время записи.',
        }
    )
    planned_duration_min = serializers.IntegerField(
        required=False,
        min_value=5,
        max_value=600,
        error_messages={
            'invalid': 'Длительность должна быть числом.',
            'min_value': 'Минимальная длительность записи — 5 минут.',
            'max_value': 'Длительность записи не должна превышать 600 минут.',
        },
    )
    planned_price = serializers.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0'),
        error_messages={
            'invalid': 'Стоимость должна быть числом.',
            'min_value': 'Стоимость не может быть отрицательной.',
        },
    )

    client_name = serializers.CharField(source='client.full_name', read_only=True)
    client_phone = serializers.CharField(source='client.phone', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    payment_status = serializers.CharField(source='payment.payment_status', read_only=True, allow_null=True)
    photos = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = [
            'id',
            'client',
            'client_name',
            'client_phone',
            'service',
            'service_name',
            'status',
            'source',
            'appointment_date',
            'start_datetime',
            'end_datetime',
            'planned_duration_min',
            'planned_price',
            'comment_client',
            'comment_master',
            'created_by',
            'needs_removal',
            'needs_strengthening',
            'design_notes',
            'payment_status',
            'photos',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_by', 'source', 'appointment_date', 'created_at', 'updated_at', 'payment_status']
        extra_kwargs = {
            'end_datetime': {'required': False},
            'planned_price': {'required': False},
            'planned_duration_min': {'required': False},
        }

    def validate(self, attrs):
        instance = self.instance

        service = attrs.get('service', instance.service if instance else None)
        if service and not service.is_active and (not instance or service != instance.service):
            raise serializers.ValidationError({'service': ['Выбранная услуга отключена и недоступна для новых записей.']})

        planned_duration = attrs.get(
            'planned_duration_min',
            instance.planned_duration_min if instance else (service.base_duration_min if service else None),
        )

        if planned_duration is None:
            raise serializers.ValidationError({'planned_duration_min': ['Не удалось определить длительность записи.']})

        start = attrs.get('start_datetime', instance.start_datetime if instance else None)
        end = attrs.get('end_datetime', instance.end_datetime if instance else None)

        if not instance and not start:
            raise serializers.ValidationError({'start_datetime': ['Укажите дату и время записи.']})

        if start and not end:
            end = start + timedelta(minutes=planned_duration)
            attrs['end_datetime'] = end

        if start and end and end <= start:
            raise serializers.ValidationError({'end_datetime': ['Время окончания должно быть позже времени начала.']})

        if instance and instance.status == Appointment.AppointmentStatus.COMPLETED:
            protected_fields = {'client', 'service', 'start_datetime', 'end_datetime'}
            if protected_fields.intersection(attrs.keys()):
                raise serializers.ValidationError('Завершенный визит нельзя редактировать по времени, клиенту или услуге.')

        if start and end:
            if not is_inside_working_hours(start, end):
                raise serializers.ValidationError({'start_datetime': ['Выбранное время выходит за пределы рабочего графика.']})
            if has_time_off_overlap(start, end):
                raise serializers.ValidationError({'start_datetime': ['Выбранное время пересекается с блокировкой графика.']})
            if has_overlap(start, end, exclude_appointment_id=instance.pk if instance else None):
                raise serializers.ValidationError({'start_datetime': ['Выбранный слот уже занят другой записью.']})

        if service:
            attrs.setdefault('planned_price', service.base_price)
        attrs.setdefault('planned_duration_min', planned_duration)
        for key in ('comment_client', 'comment_master', 'design_notes'):
            if key in attrs:
                attrs[key] = (attrs.get(key) or '').strip() or None

        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            validated_data['created_by'] = request.user

        validated_data.setdefault('source', Appointment.AppointmentSource.MASTER_MANUAL)
        validated_data.setdefault('status', Appointment.AppointmentStatus.CREATED)

        if not validated_data.get('end_datetime') and validated_data.get('start_datetime'):
            duration = validated_data.get('planned_duration_min')
            validated_data['end_datetime'] = validated_data['start_datetime'] + timedelta(minutes=duration)

        return super().create(validated_data)

    def get_photos(self, obj):
        return [
            {
                'id': photo.id,
                'image': photo.image.url if photo.image else None,
                'sort_order': photo.sort_order,
                'created_at': photo.created_at,
            }
            for photo in obj.photos.all()
        ]


class AppointmentStatusActionSerializer(serializers.Serializer):
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000,
        error_messages={'max_length': 'Причина не должна превышать 1000 символов.'},
    )


class RescheduleSerializer(serializers.Serializer):
    start_datetime = serializers.DateTimeField(
        error_messages={
            'required': 'Укажите новую дату и время записи.',
            'invalid': 'Некорректная дата и время для переноса.',
        }
    )
    planned_duration_min = serializers.IntegerField(
        required=False,
        min_value=5,
        max_value=600,
        error_messages={
            'invalid': 'Длительность должна быть числом.',
            'min_value': 'Минимальная длительность записи — 5 минут.',
            'max_value': 'Длительность записи не должна превышать 600 минут.',
        },
    )

    def validate(self, attrs):
        appointment: Appointment = self.context['appointment']
        start = attrs['start_datetime']
        duration = attrs.get('planned_duration_min', appointment.planned_duration_min)
        end = start + timedelta(minutes=duration)

        if not is_inside_working_hours(start, end):
            raise serializers.ValidationError({'start_datetime': ['Новый слот вне рабочего графика.']})
        if has_time_off_overlap(start, end):
            raise serializers.ValidationError({'start_datetime': ['Новый слот попадает в блокировку времени.']})
        if has_overlap(start, end, exclude_appointment_id=appointment.pk):
            raise serializers.ValidationError({'start_datetime': ['Новый слот уже занят.']})

        attrs['end_datetime'] = end
        attrs['planned_duration_min'] = duration
        return attrs


class AvailableSlotsQuerySerializer(serializers.Serializer):
    service_id = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.filter(is_active=True),
        source='service',
        error_messages={
            'required': 'Выберите услугу.',
            'null': 'Выберите услугу.',
            'does_not_exist': 'Выбранная услуга не найдена или отключена.',
            'incorrect_type': 'Выберите услугу из списка.',
        },
    )
    date = serializers.DateField(
        error_messages={
            'required': 'Укажите дату.',
            'invalid': 'Некорректный формат даты.',
        }
    )

    def validate_date(self, value: date) -> date:
        if value < timezone.localdate():
            raise serializers.ValidationError('Дата не может быть в прошлом.')
        return value


class PublicBookingSerializer(serializers.Serializer):
    service_id = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.filter(is_active=True),
        source='service',
        error_messages={
            'required': 'Выберите услугу.',
            'null': 'Выберите услугу.',
            'does_not_exist': 'Выбранная услуга не найдена или отключена.',
            'incorrect_type': 'Выберите услугу из списка.',
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
    full_name = serializers.CharField(
        max_length=255,
        trim_whitespace=True,
        error_messages={
            'required': 'Укажите имя.',
            'blank': 'Имя не может быть пустым.',
            'max_length': 'Имя не должно превышать 255 символов.',
        },
    )
    phone = serializers.CharField(
        max_length=32,
        trim_whitespace=True,
        error_messages={
            'required': 'Укажите телефон.',
            'blank': 'Телефон не может быть пустым.',
            'max_length': 'Телефон не должен превышать 32 символа.',
        },
    )
    comment = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=2000,
        error_messages={'max_length': 'Комментарий не должен превышать 2000 символов.'},
    )
    website = serializers.CharField(required=False, allow_blank=True, write_only=True)

    def validate_full_name(self, value: str) -> str:
        normalized = re.sub(r'\s+', ' ', value.strip())
        if len(normalized) < 2:
            raise serializers.ValidationError('Имя должно содержать минимум 2 символа.')
        return normalized

    def validate_phone(self, value: str) -> str:
        normalized = re.sub(r'\s+', ' ', value.strip())
        if not PHONE_PATTERN.match(normalized):
            raise serializers.ValidationError('Укажите корректный телефон.')

        digits_count = sum(char.isdigit() for char in normalized)
        if digits_count < 7:
            raise serializers.ValidationError('Телефон должен содержать минимум 7 цифр.')

        return normalized

    def validate(self, attrs):
        if attrs.get('website'):
            raise serializers.ValidationError('Проверка спама не пройдена.')

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
        service = validated_data['service']
        full_name = validated_data['full_name'].strip()
        phone = validated_data['phone'].strip()

        client = Client.objects.filter(phone=phone).first()
        if client:
            if client.full_name != full_name:
                client.full_name = full_name
                client.save(update_fields=['full_name', 'updated_at'])
        else:
            client = Client.objects.create(full_name=full_name, phone=phone)

        appointment = Appointment.objects.create(
            client=client,
            service=service,
            status=Appointment.AppointmentStatus.CREATED,
            source=Appointment.AppointmentSource.PUBLIC_BOOKING,
            start_datetime=validated_data['start_datetime'],
            end_datetime=validated_data['end_datetime'],
            planned_duration_min=service.base_duration_min,
            planned_price=service.base_price,
            comment_client=validated_data.get('comment', ''),
        )
        return appointment


class PublicBookingSuccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['id', 'status', 'start_datetime', 'end_datetime', 'appointment_date']
