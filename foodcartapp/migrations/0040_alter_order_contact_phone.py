# Generated by Django 3.2.15 on 2025-01-21 08:41

import django.core.validators
from django.db import migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0039_alter_order_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='contact_phone',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None, validators=[django.core.validators.MinValueValidator(12), django.core.validators.MaxValueValidator(12)], verbose_name='Номер телефона'),
        ),
    ]
