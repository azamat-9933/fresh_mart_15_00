from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart', verbose_name='Пользователь')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def __str__(self):
        return f'Корзина: {self.user}'

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE,
                             related_name='items',
                             verbose_name='Корзина')
    product = models.ForeignKey('products.Product',
                                on_delete=models.CASCADE,
                                verbose_name='Товар')
    quantity = models.PositiveIntegerField('Количество',
                                           default=1,
                                           validators=[MinValueValidator(1)])
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Элемент корзины'
        verbose_name_plural = 'Элементы корзины'
        unique_together = ('cart', 'product')

    @property
    def total_price(self):
        return self.product.price * self.quantity


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждён'),
        ('processing', 'Собирается'),
        ('shipped', 'В доставке'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменён'),
    ]
    PAYMENT_CHOICES = [
        ('cash', 'Наличные при получении'),
        ('card', 'Банковская карта'),
        ('online', 'Онлайн оплата'),
    ]
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='orders', verbose_name='Пользователь')
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_met = models.CharField('Способ оплаты', max_length=20, choices=PAYMENT_CHOICES, default='cash')
    is_paid = models.BooleanField('Оплачен', default=False)
    # Адрес доставки
    delivery_address = models.TextField('Адрес доставки')
    delivery_phone = models.CharField('Телефон', max_length=20)
    delivery_name = models.CharField('Имя получателя', max_length=100)
    comment = models.TextField('Комментарий', blank=True)
    delivery_latitude = models.TextField(verbose_name='Широта')
    delivery_longitude = models.TextField(verbose_name='Долгота')

    # Суммы
    total_price = models.DecimalField('Итого', max_digits=12, decimal_places=2)
    delivery_price = models.DecimalField('Стоимость доставки', max_digits=8, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Заказ #{self.pk} — {self.user}'

    @property
    def grand_total(self):
        return self.total_price + self.delivery_price


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Заказ')
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT, verbose_name='Товар')
    product_name = models.CharField('Название товара', max_length=200)  # snapshot
    product_price = models.DecimalField('Цена на момент заказа', max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField('Количество')

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'

    @property
    def total_price(self):
        return self.product_price * self.quantity

