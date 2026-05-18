from rest_framework import serializers

from payments.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source='order.id', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id',
            'order_id',
            'provider',
            'status',
            'amount',
            'currency',
            'transaction_id',
            'client_secret',
            'paid_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class CreateIntentSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(min_value=1)


class VerifyPaymentSerializer(serializers.Serializer):
    payment_id = serializers.IntegerField(min_value=1)
    client_secret = serializers.CharField(max_length=512)
    simulate_outcome = serializers.ChoiceField(
        choices=['succeeded', 'failed', 'processing', 'pending', 'random'],
        required=False,
        allow_null=True,
    )


class SimulateWebhookSerializer(serializers.Serializer):
    transaction_id = serializers.CharField(max_length=196)
    event = serializers.CharField(max_length=64)
