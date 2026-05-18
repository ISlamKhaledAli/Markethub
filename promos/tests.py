from decimal import Decimal

from django.test import SimpleTestCase

from promos.models import PromoCode
from promos.services import allocate_order_totals, compute_discount_amount


class PromoServicesTests(SimpleTestCase):
    def test_allocate_order_totals_splits_discount(self):
        s1, s2 = object(), object()
        raw = {s1: Decimal('60.00'), s2: Decimal('40.00')}
        out = allocate_order_totals(raw, Decimal('100.00'), Decimal('10.00'))
        self.assertEqual(sum(out.values()), Decimal('90.00'))

    def test_percentage_discount_capped(self):
        p = PromoCode(
            code='X',
            discount_type=PromoCode.DISCOUNT_PERCENTAGE,
            value=Decimal('50'),
        )
        self.assertEqual(compute_discount_amount(p, Decimal('80')), Decimal('40.00'))
