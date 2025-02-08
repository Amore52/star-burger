# Generated by Django 3.2.15 on 2025-02-05 14:23

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0060_alter_order_registrated_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='registrated_at',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата создания заказа'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Необработанный', 'необработанный'), ('Готовится', 'готовится'), ('Доставка', 'доставка'), ('Выполнен', 'выполнен')], default='необработанный', max_length=14, verbose_name='Статус'),
        ),
    ]
