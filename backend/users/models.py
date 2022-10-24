from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError


class User(AbstractUser):
    """Создание модели пользователя."""
    email = models.EmailField(
        db_index=True,
        unique=True,
        max_length=254,
        verbose_name='email',
        help_text='Введите электронную почту')
    username = models.CharField(
        db_index=True,
        max_length=150,
        unique=True,
        verbose_name='username',
        help_text='Введите уникальное имя пользователя')
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя',
        help_text='Введите имя пользователя')
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия',
        help_text='Введите фамилию пользователя')
    is_subscribed = models.BooleanField(
        default=False,
        verbose_name='Подписка на пользователя',
        help_text='Подписка на пользователя')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']

    class Meta:
        """Параметры модели."""
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        """Метод строкового представления модели."""
        return self.username


class Subscription(models.Model):
    """Создание модели подписки."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь',
        help_text='Выберите пользователя, который подписывается'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
        help_text='Выберите автора, на которого подписываются'
    )

    class Meta:
        """Параметры модели."""
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=['user', 'following'],
                                    name='unique_subscribe')
        ]

    def __str__(self):
        """Метод строкового представления модели."""
        return f'Подписка: {self.user.username} на {self.following.username}'

    def clean(self):
        errors = {}
        if self.user == self.following:
            errors['following'] = ValidationError(
                ('Пользователь не может быть подписан на самого себя.')
            )
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
