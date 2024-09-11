# Generated by Django 5.0.6 on 2024-09-06 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0003_coupon_usage_limit_coupon_used_count_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='shipping_address',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cart',
            name='shipping_city',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='cart',
            name='shipping_zip',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
