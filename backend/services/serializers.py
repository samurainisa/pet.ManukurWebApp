import re
from decimal import Decimal

from rest_framework import serializers

from services.models import Service


class ServiceSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=255,
        trim_whitespace=True,
        error_messages={
            'required': 'Укажите название услуги.',
            'blank': 'Название услуги не может быть пустым.',
            'max_length': 'Название услуги не должно превышать 255 символов.',
        },
    )
    base_duration_min = serializers.IntegerField(
        min_value=5,
        max_value=600,
        error_messages={
            'required': 'Укажите длительность услуги.',
            'invalid': 'Длительность должна быть числом.',
            'min_value': 'Минимальная длительность услуги — 5 минут.',
            'max_value': 'Длительность услуги не должна превышать 600 минут.',
        },
    )
    base_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0'),
        error_messages={
            'required': 'Укажите стоимость услуги.',
            'invalid': 'Стоимость должна быть числом.',
            'min_value': 'Стоимость не может быть отрицательной.',
        },
    )
    sort_order = serializers.IntegerField(
        min_value=0,
        max_value=10000,
        error_messages={
            'invalid': 'Порядок должен быть числом.',
            'min_value': 'Порядок не может быть отрицательным.',
            'max_value': 'Порядок не должен превышать 10000.',
        },
    )

    class Meta:
        model = Service
        fields = [
            'id',
            'name',
            'description',
            'base_duration_min',
            'base_price',
            'is_active',
            'sort_order',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ('created_at', 'updated_at')

    def validate_name(self, value: str) -> str:
        normalized = re.sub(r'\s+', ' ', value.strip())
        if len(normalized) < 2:
            raise serializers.ValidationError('Название услуги должно содержать минимум 2 символа.')
        return normalized
