from django.contrib import admin

from payments.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'order',
        'user',
        'provider',
        'status',
        'amount',
        'transaction_id',
        'paid_at',
        'created_at',
    )
    list_filter = ('provider', 'status')
    search_fields = ('transaction_id', 'user__email', 'order__id')
