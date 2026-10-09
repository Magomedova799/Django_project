from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Создает и сохраняет обычного пользователя"""
        if not email:
            raise ValueError('Email обязателен для создания пользователя')
       
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
   
    def create_superuser(self, email, password=None, **extra_fields):
        """Создает и сохраняет суперпользователя"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
       
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True')
       
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=True
    )

    email = models.EmailField(unique=True)

    specialization = models.CharField(
        max_length=100,
        blank=True
    )

    portfolio_url = models.URLField(
        blank=True
    )

    bio = models.TextField(blank=True)

    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.email

'''для автоматического создания токенов'''
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

class Subscription(models.Model):
    '''Система подписок на авторов'''
    follower = models.ForeignKey(
        'CustomUser', 
        on_delete=models.CASCADE, 
        related_name='following_subscriptions',
        verbose_name='Кто подписывается'
    )
    author = models.ForeignKey(
        'CustomUser', 
        on_delete=models.CASCADE, 
        related_name='follower_subscriptions',
        verbose_name='На кого подписываются'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        unique_together = ('follower', 'author')

    def __str__(self):
        return f'{self.follower.email} -> {self.author.email}'
