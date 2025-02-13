from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.db.models import Sum, F
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField('название', max_length=50)
    address = models.CharField('адрес', max_length=100, blank=True)
    contact_phone = models.CharField('контактный телефон', max_length=50, blank=True)

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductCategory(models.Model):
    name = models.CharField('название', max_length=50)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = RestaurantMenuItem.objects.filter(availability=True).values_list('product', flat=True)
        return self.filter(pk__in=products)


class Product(models.Model):
    name = models.CharField('название', max_length=50)
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='цена',
    )
    image = models.ImageField('картинка')
    special_status = models.BooleanField('спец.предложение', default=False, db_index=True)
    description = models.TextField('описание', max_length=200, blank=True)

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name='ресторан',
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        related_name='menu_items',
        verbose_name='продукт',
        on_delete=models.CASCADE,
    )
    availability = models.BooleanField('в продаже', default=True)

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = ('restaurant', 'product')

    def __str__(self):
        return f'{self.restaurant.name} - {self.product.name}'


class OrderQuerySet(models.QuerySet):
    def with_total_cost(self):
        return self.prefetch_related('items').annotate(
            total_cost=Sum(F('items__quantity') * F('items__price'))
        )


class Order(models.Model):
    STATUS_CHOICES = [
        ('Необработанный', 'необработанный'),
        ('Готовится', 'готовится'),
        ('Доставка', 'доставка'),
        ('Выполнен', 'выполнен'),
    ]
    PAYMENT_CHOICES = [
        ('Наличкой', 'наличкой'),
        ('Переводом', 'переводом'),
        ('Картой', 'картой'),
    ]

    firstname = models.CharField(max_length=20, verbose_name='имя')
    lastname = models.CharField(max_length=30, verbose_name='фамилия')
    phonenumber = PhoneNumberField(verbose_name='телефон')
    address = models.CharField(max_length=100, verbose_name='адрес')
    payment = models.CharField(
        max_length=9,
        choices=PAYMENT_CHOICES,
        default='Уточнить',
        verbose_name='способ оплаты',
    )
    status = models.CharField(
        max_length=14,
        choices=STATUS_CHOICES,
        default='Необработанный',
        verbose_name='статус',
    )
    comment = models.TextField(
        verbose_name='комментарий к заказу',
        blank=True,
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.SET_NULL,
        related_name='orders',
        verbose_name='ресторан',
        null=True,
        blank=True,
    )
    registered_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='дата создания заказа',
    )
    called_at = models.DateTimeField(
        verbose_name='дата звонка',
        null=True,
        blank=True,
    )
    delivered_at = models.DateTimeField(
        verbose_name='дата доставки',
        null=True,
        blank=True,
    )

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'Заказ №{self.id}'


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='заказ',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='ordered_items',
        verbose_name='продукт',
    )
    quantity = models.PositiveIntegerField(verbose_name='количество', validators=[MinValueValidator(1)])
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='цена',
    )

    class Meta:
        verbose_name = 'элемент заказа'
        verbose_name_plural = 'элементы заказа'

    def __str__(self):
        return f'{self.product.name} ({self.quantity} шт.)'
