from rest_framework import serializers

from visits.models import VisitPhoto, VisitResult


class VisitResultSerializer(serializers.ModelSerializer):
    actual_duration_min = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
        max_value=600,
        error_messages={
            'invalid': 'Фактическая длительность должна быть числом.',
            'min_value': 'Фактическая длительность должна быть больше 0.',
            'max_value': 'Фактическая длительность не должна превышать 600 минут.',
        },
    )

    class Meta:
        model = VisitResult
        fields = [
            'id',
            'appointment',
            'actual_service_summary',
            'materials_used',
            'result_notes',
            'actual_duration_min',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'appointment', 'created_at', 'updated_at']


class VisitPhotoSerializer(serializers.ModelSerializer):
    MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024
    ALLOWED_CONTENT_TYPES = {'image/jpeg', 'image/png', 'image/webp'}

    class Meta:
        model = VisitPhoto
        fields = ['id', 'appointment', 'image', 'sort_order', 'created_at']
        read_only_fields = ['id', 'appointment', 'created_at']

    def validate_sort_order(self, value: int) -> int:
        if value < 0:
            raise serializers.ValidationError('Порядок фото не может быть отрицательным.')
        return value

    def validate_image(self, value):
        if value.size > self.MAX_IMAGE_SIZE_BYTES:
            raise serializers.ValidationError('Размер фото не должен превышать 5 МБ.')

        content_type = getattr(value, 'content_type', '')
        if content_type and content_type not in self.ALLOWED_CONTENT_TYPES:
            raise serializers.ValidationError('Разрешены только JPG, PNG и WEBP файлы.')

        return value
