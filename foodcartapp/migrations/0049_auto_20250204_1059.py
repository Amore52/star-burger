# Generated by Django 3.2.15 on 2025-02-04 07:59

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0048_alter_orderitem_order'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='orderitem',
            options={'verbose_name': 'Элемент заказа', 'verbose_name_plural': 'Элементы заказа'},
        ),
        migrations.RemoveField(
            model_name='order',
            name='adress',
        ),
        migrations.RemoveField(
            model_name='order',
            name='contact_phone',
        ),
        migrations.RemoveField(
            model_name='order',
            name='name',
        ),
        migrations.RemoveField(
            model_name='order',
            name='second_name',
        ),
        migrations.AddField(
            model_name='order',
            name='address',
            field=models.CharField(default='2', max_length=100, verbose_name='Адрес'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='firstname',
            field=models.CharField(default='12', max_length=20, verbose_name='Имя'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='lastname',
            field=models.CharField(default='123', max_length=30, verbose_name='Фамилия'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='phonenumber',
            field=phonenumber_field.modelfields.PhoneNumberField(default='+79524548867', max_length=128, region=None, verbose_name='Телефон'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='orderitem',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8, validators=[django.core.validators.MinValueValidator(0)], verbose_name='цена'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='foodcartapp.order'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ordered_items', to='foodcartapp.product', verbose_name='Продукт'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='quantity',
            field=models.PositiveIntegerField(verbose_name='Количество'),
        ),
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True, max_length=200, verbose_name='описание'),
        ),
    ]
