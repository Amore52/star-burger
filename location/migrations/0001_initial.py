# Generated by Django 3.2.15 on 2025-02-08 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=255, unique=True, verbose_name='Адрес')),
                ('latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True, verbose_name='Широта')),
                ('longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True, verbose_name='Долгота')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
            ],
            options={
                'verbose_name': 'Локация',
                'verbose_name_plural': 'Локации',
            },
        ),
    ]
