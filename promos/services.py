from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from orders.models import Cart

from promos.models import PromoCode


@dataclass
class PromoValidationResult:
    valid: bool
    code: str
    discount_amount: Decimal
    message: str
    subtotal: Decimal
    total_after_discount: Decimal


def line_total_for_item(item) -> Decimal:
    price = item.product.discount_price if item.product.discount_price else item.product.price
    return price * item.quantity


def cart_subtotal(cart: Cart) -> Decimal:
    return sum((line_total_for_item(i) for i in cart.items.all()), start=Decimal('0'))


def compute_discount_amount(promo: PromoCode, subtotal: Decimal) -> Decimal:
    if promo.discount_type == PromoCode.DISCOUNT_PERCENTAGE:
        if promo.value <= 0:
            return Decimal('0')
        pct = min(promo.value, Decimal('100'))
        raw = (subtotal * pct / Decimal('100')).quantize(Decimal('0.01'))
        return min(raw, subtotal)
    # fixed
    if promo.value <= 0:
        return Decimal('0')
    return min(promo.value.quantize(Decimal('0.01')), subtotal)


def validate_promo_for_subtotal(promo: PromoCode | None, subtotal: Decimal) -> PromoValidationResult:
    if promo is None:
        return PromoValidationResult(
            valid=False,
            code='',
            discount_amount=Decimal('0'),
            message='Invalid promo code.',
            subtotal=subtotal,
            total_after_discount=subtotal,
        )
    now = timezone.now()
    if not promo.is_active:
        return PromoValidationResult(
            valid=False,
            code=promo.code,
            discount_amount=Decimal('0'),
            message='This promo code is not active.',
            subtotal=subtotal,
            total_after_discount=subtotal,
        )
    if promo.starts_at and now < promo.starts_at:
        return PromoValidationResult(
            valid=False,
            code=promo.code,
            discount_amount=Decimal('0'),
            message='This promo code is not valid yet.',
            subtotal=subtotal,
            total_after_discount=subtotal,
        )
    if promo.expires_at and now > promo.expires_at:
        return PromoValidationResult(
            valid=False,
            code=promo.code,
            discount_amount=Decimal('0'),
            message='This promo code has expired.',
            subtotal=subtotal,
            total_after_discount=subtotal,
        )
    if promo.max_uses is not None and promo.used_count >= promo.max_uses:
        return PromoValidationResult(
            valid=False,
            code=promo.code,
            discount_amount=Decimal('0'),
            message='This promo code has reached its usage limit.',
            subtotal=subtotal,
            total_after_discount=subtotal,
        )
    if subtotal < promo.minimum_order_amount:
        return PromoValidationResult(
            valid=False,
            code=promo.code,
            discount_amount=Decimal('0'),
            message=(
                f'Minimum order amount of {promo.minimum_order_amount} not met '
                f'(current subtotal: {subtotal}).'
            ),
            subtotal=subtotal,
            total_after_discount=subtotal,
        )

    discount = compute_discount_amount(promo, subtotal)
    return PromoValidationResult(
        valid=True,
        code=promo.code,
        discount_amount=discount,
        message='Promo code is valid.',
        subtotal=subtotal,
        total_after_discount=(subtotal - discount).quantize(Decimal('0.01')),
    )


def allocate_order_totals(seller_raw_totals: dict, subtotal: Decimal, discount: Decimal) -> dict:
    """
    Split (subtotal - discount) across sellers proportionally to their raw totals.
    """
    if subtotal <= 0:
        raise ValueError('Subtotal must be positive.')
    if discount < 0:
        raise ValueError('Discount cannot be negative.')
    if discount > subtotal:
        discount = subtotal

    distributable = (subtotal - discount).quantize(Decimal('0.01'))
    sellers = list(seller_raw_totals.keys())
    if not sellers:
        return {}

    allocated = Decimal('0')
    result: dict = {}
    for idx, seller in enumerate(sellers):
        raw = seller_raw_totals[seller]
        if idx == len(sellers) - 1:
            share = (distributable - allocated).quantize(Decimal('0.01'))
        else:
            if subtotal == 0:
                share = Decimal('0')
            else:
                share = (distributable * (raw / subtotal)).quantize(Decimal('0.01'))
            allocated += share
        result[seller] = max(share, Decimal('0'))
    return result


def increment_promo_usage(promo: PromoCode) -> None:
    with transaction.atomic():
        locked = PromoCode.objects.select_for_update().get(pk=promo.pk)
        if locked.max_uses is not None and locked.used_count >= locked.max_uses:
            raise ValueError('Promo usage limit exceeded.')
        locked.used_count += 1
        locked.save()
