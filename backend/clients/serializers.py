import re

from django.db.models import Sum
from rest_framework import serializers

from clients.models import Client
from scheduling.models import Appointment

PHONE_PATTERN = re.compile(r'^\+?[0-9()\-\s]{7,20}$')


class ClientSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(
        max_length=255,
        trim_whitespace=True,
        error_messages={
            'required': 'Укажите имя клиента.',
            'blank': 'Имя клиента не может быть пустым.',
            'max_length': 'Имя клиента не должно превышать 255 символов.',
        },
    )
    phone = serializers.CharField(
        max_length=32,
        trim_whitespace=True,
        error_messages={
            'required': 'Укажите телефон клиента.',
            'blank': 'Телефон клиента не может быть пустым.',
            'max_length': 'Телефон не должен превышать 32 символа.',
        },
    )
    email = serializers.EmailField(
        required=False,
        allow_null=True,
        allow_blank=True,
        error_messages={
            'invalid': 'Укажите корректный email.',
        },
    )
    total_paid = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = [
            'id',
            'full_name',
            'phone',
            'email',
            'notes',
            'total_paid',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ('created_at', 'updated_at', 'total_paid')

    def validate_phone(self, value: str) -> str:
        normalized = re.sub(r'\s+', ' ', value.strip())
        if not PHONE_PATTERN.match(normalized):
            raise serializers.ValidationError('Укажите корректный телефон.')

        digits_count = sum(char.isdigit() for char in normalized)
        if digits_count < 7:
            raise serializers.ValidationError('Телефон должен содержать минимум 7 цифр.')

        qs = Client.objects.filter(phone=normalized)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('Клиент с таким телефоном уже существует.')
        return normalized

    def validate_full_name(self, value: str) -> str:
        normalized = re.sub(r'\s+', ' ', value.strip())
        if len(normalized) < 2:
            raise serializers.ValidationError('Имя клиента должно содержать минимум 2 символа.')
        return normalized

    def get_total_paid(self, obj: Client):
        total = (
            obj.appointments.filter(payment__payment_status__in=['paid', 'partial'])
            .aggregate(total=Sum('payment__amount'))
            .get('total')
        )
        return total or 0


class ClientHistoryItemSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)
    payment_amount = serializers.DecimalField(
        source='payment.amount', max_digits=10, decimal_places=2, read_only=True, allow_null=True
    )
    payment_status = serializers.CharField(source='payment.payment_status', read_only=True, allow_null=True)

    class Meta:
        model = Appointment
        fields = [
            'id',
            'status',
            'start_datetime',
            'end_datetime',
            'planned_duration_min',
            'planned_price',
            'service_name',
            'payment_amount',
            'payment_status',
            'comment_master',
        ]
