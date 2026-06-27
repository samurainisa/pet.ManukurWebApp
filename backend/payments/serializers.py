from decimal import Decimal

from rest_framework import serializers

from payments.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0'),
        error_messages={
            'required': 'Укажите сумму оплаты.',
            'invalid': 'Сумма должна быть числом.',
            'min_value': 'Сумма не может быть отрицательной.',
        },
    )
    payment_method = serializers.ChoiceField(
        choices=Payment.PaymentMethod.choices,
        error_messages={
            'required': 'Укажите способ оплаты.',
            'invalid_choice': 'Выберите корректный способ оплаты.',
        },
    )
    payment_status = serializers.ChoiceField(
        choices=Payment.PaymentStatus.choices,
        error_messages={
            'required': 'Укажите статус оплаты.',
            'invalid_choice': 'Выберите корректный статус оплаты.',
        },
    )
    comment = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Payment
        fields = [
            'id',
            'appointment',
            'amount',
            'payment_method',
            'payment_status',
            'paid_at',
            'comment',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'appointment', 'created_at', 'updated_at']

    def validate(self, attrs):
        amount = attrs.get('amount', self.instance.amount if self.instance else Decimal('0'))
        status_value = attrs.get('payment_status', self.instance.payment_status if self.instance else None)

        if status_value in {Payment.PaymentStatus.PAID, Payment.PaymentStatus.PARTIAL} and amount <= 0:
            raise serializers.ValidationError({'amount': ['Для выбранного статуса сумма должна быть больше 0.']})

        return attrs
