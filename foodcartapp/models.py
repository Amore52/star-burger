from django.utils import timezone
from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import Sum, F
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField('название', max_length=50)
    address = models.CharField('адрес', max_length=100, blank=True,)
    contact_phone = models.CharField('контактный телефон', max_length=50, blank=True,)

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name

class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)

class ProductCategory(models.Model):
    name = models.CharField('название', max_length=50)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name

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
    special_status = models.BooleanField('спец.предложение', default=False, db_index=True,)
    description = models.TextField('описание', max_length=200, blank=True,)
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
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField('в продаже', default=True, db_index=True)

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderManager(models.Manager):
    def get_queryset(self):
        return OrderQuerySet(self.model, using=self._db)

    def with_total_cost(self):
        return self.get_queryset().with_total_cost()


class Order(models.Model):
    STATUS_CHOISES = [
        ('Необработанный', 'необработанный'),
        ('Готовится', 'готовится'),
        ('Доставка', 'доставка'),
        ('Выполнен', 'выполнен')
    ]
    PAYMENT_CHOISES = [
        ('Наличкой', 'наличкой'),
        ('Переводом', 'переводом'),
        ('Картой', 'Картой')
    ]
    firstname = models.CharField(max_length=20, verbose_name='Имя')
    lastname = models.CharField(max_length=30, verbose_name='Фамилия')
    phonenumber = PhoneNumberField(verbose_name='Телефон')
    address = models.CharField(max_length=100, verbose_name='Адрес')
    payment = models.CharField(
        max_length=9,
        choices=PAYMENT_CHOISES,
        default='Уточнить',
        verbose_name='Способ оплаты')
    status = models.CharField(
        max_length=14,
        choices=STATUS_CHOISES,
        default='Необработанный',
        verbose_name='Статус')
    comment = models.TextField(
        verbose_name='Комментарий к заказу',
        default='',
        null=True,
        blank=True,)
    registrated_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата создания заказа')
    called_at = models.DateTimeField(
        verbose_name='Дата звонка',
        blank=True,
        null=True)
    delivered_at = models.DateTimeField(
        verbose_name='Дата доставки',
        blank=True,
        null=True)
    objects = OrderManager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'Заказ №{self.id}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ordered_items', verbose_name='Продукт')
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'

    def __str__(self):
        return f'{self.product.name} {self.quantity} шт.'

class OrderQuerySet(models.QuerySet):
    def with_total_cost(self):
        return self.prefetch_related('items').annotate(
            total_cost=Sum(F('items__quantity') * F('items__price'))
        )




