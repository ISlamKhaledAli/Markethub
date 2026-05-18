from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Any

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from orders.fulfillment import FulfillmentError, fulfill_order_on_payment
from orders.models import Order
from payments.models import Payment
from payments.providers import get_payment_provider
from payments.providers.stripe import StripePaymentProvider


class PaymentServiceError(Exception):
    def __init__(self, message: str, code: str = 'payment_error'):
        self.message = message
        self.code = code
        super().__init__(message)


@transaction.atomic
def create_payment_intent(*, user, order_id: int) -> Payment:
    order = (
        Order.objects.select_for_update()
        .filter(id=order_id, buyer=user)
        .first()
    )
    if not order:
        raise PaymentServiceError('Order not found.', 'not_found')

    if Payment.objects.filter(order=order, status=Payment.STATUS_SUCCEEDED).exists():
        raise PaymentServiceError('This order is already paid.', 'already_paid')

    amount = order.total_amount.quantize(Decimal('0.01'))

    provider_setting = (getattr(settings, 'PAYMENT_PROVIDER', None) or 'mock').lower()
    provider_enum = (
        Payment.PROVIDER_STRIPE if provider_setting == 'stripe' else Payment.PROVIDER_MOCK
    )

    if amount <= 0:
        payment = Payment.objects.create(
            order=order,
            user=user,
            provider=provider_enum,
            status=Payment.STATUS_SUCCEEDED,
            amount=amount,
            currency='usd',
            transaction_id=f'zero_amount_{order.id}_{user.id}',
            client_secret='',
            paid_at=timezone.now(),
        )
        _complete_order_payment(order)
        return payment

    existing = (
        Payment.objects.select_for_update()
        .filter(
            order=order,
            status__in=[Payment.STATUS_PENDING, Payment.STATUS_PROCESSING],
        )
        .first()
    )
    if existing:
        if existing.amount != amount:
            existing.amount = amount
            existing.save(update_fields=['amount', 'updated_at'])
        if provider_enum == Payment.PROVIDER_STRIPE and existing.transaction_id:
            url = StripePaymentProvider.retrieve_open_session_url(existing.transaction_id)
            if url and not existing.checkout_url:
                existing.checkout_url = url
                existing.save(update_fields=['checkout_url', 'updated_at'])
        return existing

    provider = get_payment_provider()
    pending_txn = f'pending_{uuid.uuid4().hex[:20]}'
    payment = Payment.objects.create(
        order=order,
        user=user,
        provider=provider_enum,
        status=Payment.STATUS_PENDING,
        amount=amount,
        currency='usd',
        transaction_id=pending_txn,
        client_secret='',
        checkout_url='',
    )

    metadata: dict[str, Any] = {
        'order_id': str(order.id),
        'user_id': str(user.id),
        'payment_id': str(payment.pk),
    }
    intent = provider.create_payment_intent(amount=amount, currency='usd', metadata=metadata)

    payment.transaction_id = intent['transaction_id']
    payment.client_secret = intent.get('client_secret', '')
    payment.checkout_url = intent.get('checkout_url', '')
    payment.save(update_fields=['transaction_id', 'client_secret', 'checkout_url', 'updated_at'])
    return payment


@transaction.atomic
def verify_payment(
    *,
    user,
    payment_id: int,
    client_secret: str,
    simulate_outcome: str | None = None,
) -> Payment:
    payment = (
        Payment.objects.select_for_update()
        .select_related('order')
        .filter(id=payment_id, user=user)
        .first()
    )
    if not payment:
        raise PaymentServiceError('Payment not found.', 'not_found')

    if payment.status == Payment.STATUS_SUCCEEDED:
        raise PaymentServiceError('Payment already completed.', 'already_succeeded')

    if payment.provider == Payment.PROVIDER_MOCK:
        if payment.client_secret != client_secret:
            raise PaymentServiceError('Invalid client secret.', 'invalid_secret')
    elif payment.provider == Payment.PROVIDER_STRIPE:
        allowed = {payment.client_secret, payment.transaction_id, payment.checkout_url}
        if client_secret not in allowed and not client_secret.startswith('cs_'):
            raise PaymentServiceError('Invalid payment session.', 'invalid_secret')

    if Payment.objects.filter(
        order_id=payment.order_id,
        status=Payment.STATUS_SUCCEEDED,
    ).exclude(pk=payment.pk).exists():
        raise PaymentServiceError('Order already has a successful payment.', 'order_already_paid')

    provider = get_payment_provider()
    outcome = provider.verify_payment(
        transaction_id=payment.transaction_id or '',
        client_secret=payment.client_secret,
        simulate_outcome=simulate_outcome,
    )

    return _apply_status(payment, outcome)


def _complete_order_payment(order: Order) -> None:
    order.refresh_from_db()
    try:
        fulfill_order_on_payment(order)
    except FulfillmentError as exc:
        raise PaymentServiceError(str(exc), 'fulfillment_failed') from exc
    Order.objects.filter(pk=order.pk).update(status='accepted')


def _apply_status(payment: Payment, outcome: str) -> Payment:
    if outcome == Payment.STATUS_SUCCEEDED:
        payment.status = Payment.STATUS_SUCCEEDED
        payment.paid_at = timezone.now()
        payment.save(update_fields=['status', 'paid_at', 'updated_at'])
        _complete_order_payment(payment.order)
        return payment

    if outcome == Payment.STATUS_FAILED:
        payment.status = Payment.STATUS_FAILED
        payment.save(update_fields=['status', 'updated_at'])
        return payment

    if outcome == Payment.STATUS_PROCESSING:
        payment.status = Payment.STATUS_PROCESSING
        payment.save(update_fields=['status', 'updated_at'])
        return payment

    if outcome == Payment.STATUS_PENDING:
        payment.status = Payment.STATUS_PENDING
        payment.save(update_fields=['status', 'updated_at'])
        return payment

    payment.status = Payment.STATUS_FAILED
    payment.save(update_fields=['status', 'updated_at'])
    return payment


@transaction.atomic
def apply_webhook_event(*, transaction_id: str, event: str) -> Payment:
    if not transaction_id:
        raise PaymentServiceError('transaction_id is required.', 'invalid_payload')

    payment = (
        Payment.objects.select_for_update()
        .select_related('order')
        .filter(transaction_id=transaction_id)
        .first()
    )
    if not payment:
        raise PaymentServiceError('Payment not found for transaction.', 'not_found')

    event_l = event.lower()
    if event_l in ('succeeded', 'payment.succeeded', 'success'):
        if payment.status == Payment.STATUS_SUCCEEDED:
            return payment
        if Payment.objects.filter(
            order_id=payment.order_id,
            status=Payment.STATUS_SUCCEEDED,
        ).exclude(pk=payment.pk).exists():
            raise PaymentServiceError('Order already paid.', 'already_paid')
        return _apply_status(payment, Payment.STATUS_SUCCEEDED)

    if event_l in ('failed', 'payment.failed', 'failure'):
        if payment.status == Payment.STATUS_SUCCEEDED:
            raise PaymentServiceError('Cannot fail a completed payment.', 'invalid_transition')
        return _apply_status(payment, Payment.STATUS_FAILED)

    if event_l in ('refunded', 'payment.refunded'):
        payment.status = Payment.STATUS_REFUNDED
        payment.save(update_fields=['status', 'updated_at'])
        return payment

    raise PaymentServiceError('Unsupported webhook event.', 'unsupported_event')


@transaction.atomic
def apply_stripe_webhook_event(*, event_type: str, transaction_id: str) -> Payment:
    """Map Stripe webhook event types to internal payment status updates."""
    if event_type == 'checkout.session.completed':
        return apply_webhook_event(transaction_id=transaction_id, event='succeeded')
    if event_type in (
        'checkout.session.expired',
        'checkout.session.async_payment_failed',
        'payment_intent.payment_failed',
    ):
        return apply_webhook_event(transaction_id=transaction_id, event='failed')
    raise PaymentServiceError(f'Unhandled Stripe event: {event_type}', 'unsupported_event')


def list_payments_for_account(user):
    qs = Payment.objects.select_related('order', 'order__buyer', 'order__seller')
    if user.role == 'admin':
        return qs.order_by('-created_at')
    if user.role == 'seller' and hasattr(user, 'seller_profile'):
        return qs.filter(order__seller=user.seller_profile).order_by('-created_at')
    return qs.filter(user=user).order_by('-created_at')
