from django.urls import path

from payments.views import (
    PaymentCreateIntentView,
    PaymentHistoryView,
    PaymentSimulateWebhookView,
    PaymentVerifyView,
    StripeWebhookView,
)

urlpatterns = [
    path('create-intent/', PaymentCreateIntentView.as_view(), name='payment-create-intent'),
    path('verify/', PaymentVerifyView.as_view(), name='payment-verify'),
    path('history/', PaymentHistoryView.as_view(), name='payment-history'),
    path('simulate-webhook/', PaymentSimulateWebhookView.as_view(), name='payment-simulate-webhook'),
    path('stripe-webhook/', StripeWebhookView.as_view(), name='payment-stripe-webhook'),
]
