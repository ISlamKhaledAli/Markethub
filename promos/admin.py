from django.contrib import admin

from promos.models import PromoCode


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'discount_type',
        'value',
        'is_active',
        'used_count',
        'max_uses',
        'minimum_order_amount',
        'starts_at',
        'expires_at',
    )
    search_fields = ('code',)
    list_filter = ('is_active', 'discount_type')
