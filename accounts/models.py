from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    address = models.TextField(blank=True, verbose_name='Адрес доставки')
    avatar = models.ImageField(upload_to='avatars/', verbose_name='Аватар', null=True, blank=True)
    birth_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата рождения')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.get_full_name() or self.username



