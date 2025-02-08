from django.db import models

class Location(models.Model):
    address = models.CharField('Адрес', max_length=255, unique=True)
    latitude = models.DecimalField('Широта', max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField('Долгота', max_digits=9, decimal_places=6, null=True, blank=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Локация'
        verbose_name_plural = 'Локации'

    def __str__(self):
        return self.address
