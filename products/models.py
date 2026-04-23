from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class Category(models.Model):
    name = models.CharField('Название', max_length=100)
    slug = models.SlugField('Slug', unique=True)
    image = models.ImageField('Изображение', upload_to='categories/', null=True, blank=True)
    description = models.TextField('Описание', blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                                related_name='children', verbose_name='Родительская категория')
    is_active = models.BooleanField('Активна', default=True)
    order = models.PositiveIntegerField('Порядок', default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products', verbose_name='Категория')
    name = models.CharField('Название', max_length=200)
    slug = models.SlugField('Slug', unique=True)
    description = models.TextField('Описание', blank=True)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    old_price = models.DecimalField('Старая цена', max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField('Изображение', upload_to='products/', null=True, blank=True)
    stock = models.PositiveIntegerField('Остаток на складе', default=0)
    unit = models.CharField('Единица измерения', max_length=20, default='шт',
                             choices=[('шт', 'Штука'), ('кг', 'Килограмм'), ('г', 'Грамм'),
                                      ('л', 'Литр'), ('мл', 'Миллилитр'), ('упак', 'Упаковка')])
    is_active = models.BooleanField('Активен', default=True)
    is_featured = models.BooleanField('Рекомендуемый', default=False)
    is_new = models.BooleanField('Новинка', default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']


    def __str__(self):
        return self.name

    @property
    def discount_percent(self):
        if self.old_price and self.old_price > self.price:
            return int((1 - self.price / self.old_price) * 100)
        return 0

    @property
    def in_stock(self):
        return self.stock > 0

    @property
    def avg_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 0

    @property
    def reviews_count(self):
        return self.reviews.count()


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name='Товар')
    image = models.ImageField('Изображение', upload_to='products/gallery/')
    alt = models.CharField('Alt текст', max_length=200, blank=True)
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Изображение товара'
        verbose_name_plural = 'Изображения товаров'
        ordering = ['order']

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name='Товар')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', verbose_name='Пользователь')
    rating = models.PositiveSmallIntegerField('Оценка', validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField('Комментарий', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        unique_together = ('product', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} — {self.product} ({self.rating}★)'


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist', verbose_name='Пользователь')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by', verbose_name='Товар')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Список желаний'
        verbose_name_plural = 'Списки желаний'
        unique_together = ('user', 'product')















