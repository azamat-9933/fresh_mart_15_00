from django.db import models

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    phone = models.CharField(verbose_name="Телефон", max_length=20, blank=True)
    address = models.TextField(verbose_name='Адрес доставки', blank=True)
    avatar = models.ImageField(verbose_name='Аватар', upload_to='avatars/', null=True, blank=True)
    birth_date = models.DateTimeField(verbose_name='Дата рождения', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.get_full_name() or self.username