from __future__ import annotations

from decimal import Decimal
from typing import Any

from .base import BasePaymentProvider


class StripePaymentProvider(BasePaymentProvider):
    """
    Placeholder for future Stripe integration.
    Set PAYMENT_PROVIDER=stripe once implemented.
    """

    def create_payment_intent(
        self,
        *,
        amount: Decimal,
        currency: str,
        metadata: dict[str, Any],
    ) -> dict[str, str]:
        raise NotImplementedError(
            'Stripe is not wired yet. Use PAYMENT_PROVIDER=mock for local development.'
        )

    def verify_payment(
        self,
        *,
        transaction_id: str,
        client_secret: str,
        simulate_outcome: str | None = None,
    ) -> str:
        raise NotImplementedError(
            'Stripe is not wired yet. Use PAYMENT_PROVIDER=mock for local development.'
        )

    def parse_webhook_payload(self, payload: dict[str, Any]) -> tuple[str, str]:
        raise NotImplementedError(
            'Stripe is not wired yet. Use PAYMENT_PROVIDER=mock for local development.'
        )
