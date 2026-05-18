from django.conf import settings

from .base import BasePaymentProvider
from .mock import MockPaymentProvider
from .stripe import StripePaymentProvider


def get_payment_provider() -> BasePaymentProvider:
    name = (getattr(settings, 'PAYMENT_PROVIDER', None) or 'mock').lower()
    if name == 'mock':
        return MockPaymentProvider()
    if name == 'stripe':
        return StripePaymentProvider()
    raise ValueError(f'Unsupported PAYMENT_PROVIDER: {name!r}')
