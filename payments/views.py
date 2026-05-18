from django.conf import settings
from rest_framework import permissions, status, views

from payments.serializers import (
    CreateIntentSerializer,
    PaymentSerializer,
    SimulateWebhookSerializer,
    VerifyPaymentSerializer,
)
from payments.services import (
    PaymentServiceError,
    apply_webhook_event,
    create_payment_intent,
    list_payments_for_user,
    verify_payment,
)
from users.mixins import ApiResponseMixin


class PaymentCreateIntentView(ApiResponseMixin, views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        ser = CreateIntentSerializer(data=request.data)
        if not ser.is_valid():
            return self.error_response(message='Validation failed.', data=ser.errors)

        try:
            payment = create_payment_intent(user=request.user, order_id=ser.validated_data['order_id'])
        except PaymentServiceError as e:
            code = status.HTTP_404_NOT_FOUND if e.code == 'not_found' else status.HTTP_400_BAD_REQUEST
            return self.error_response(message=e.message, data={'code': e.code}, status_code=code)

        return self.success_response(
            data=PaymentSerializer(payment).data,
            message='Payment intent created.',
            status_code=status.HTTP_201_CREATED,
        )


class PaymentVerifyView(ApiResponseMixin, views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        ser = VerifyPaymentSerializer(data=request.data)
        if not ser.is_valid():
            return self.error_response(message='Validation failed.', data=ser.errors)

        try:
            payment = verify_payment(
                user=request.user,
                payment_id=ser.validated_data['payment_id'],
                client_secret=ser.validated_data['client_secret'],
                simulate_outcome=ser.validated_data.get('simulate_outcome'),
            )
        except PaymentServiceError as e:
            st = status.HTTP_400_BAD_REQUEST
            if e.code == 'not_found':
                st = status.HTTP_404_NOT_FOUND
            return self.error_response(
                message=e.message,
                data={'code': e.code},
                status_code=st,
            )

        return self.success_response(
            data=PaymentSerializer(payment).data,
            message='Payment status updated.',
        )


class PaymentHistoryView(ApiResponseMixin, views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = list_payments_for_user(request.user)
        return self.success_response(
            data={'results': PaymentSerializer(qs, many=True).data},
            message='OK',
        )


class PaymentSimulateWebhookView(ApiResponseMixin, views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        secret = request.headers.get('X-Payment-Webhook-Secret') or request.META.get(
            'HTTP_X_PAYMENT_WEBHOOK_SECRET'
        )
        expected = getattr(settings, 'PAYMENT_WEBHOOK_SECRET', '')
        if not expected or secret != expected:
            return self.error_response(
                message='Invalid webhook secret.',
                status_code=status.HTTP_403_FORBIDDEN,
            )

        ser = SimulateWebhookSerializer(data=request.data)
        if not ser.is_valid():
            return self.error_response(message='Validation failed.', data=ser.errors)

        try:
            payment = apply_webhook_event(
                transaction_id=ser.validated_data['transaction_id'],
                event=ser.validated_data['event'],
            )
        except PaymentServiceError as e:
            st = status.HTTP_404_NOT_FOUND if e.code == 'not_found' else status.HTTP_400_BAD_REQUEST
            return self.error_response(message=e.message, data={'code': e.code}, status_code=st)

        return self.success_response(
            data=PaymentSerializer(payment).data,
            message='Webhook processed.',
        )
