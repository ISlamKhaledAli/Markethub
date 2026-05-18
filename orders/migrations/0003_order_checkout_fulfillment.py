from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('promos', '0001_initial'),
        ('orders', '0002_cart_applied_promo'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='checkout_group_id',
            field=models.UUIDField(blank=True, db_index=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='applied_promo',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='orders',
                to='promos.promocode',
            ),
        ),
        migrations.AddField(
            model_name='order',
            name='inventory_fulfilled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='promo_usage_recorded',
            field=models.BooleanField(default=False),
        ),
    ]
