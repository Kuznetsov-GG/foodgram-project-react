from django.core.validators import (MinValueValidator,
                                    RegexValidator,
                                    MaxValueValidator)
from django.db import models

from users.models import User


class Ingredient(models.Model):
    """Создание модели продуктов."""
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Введите название ингредиента')
    measurement_unit = models.CharField(
        max_length=30,
        verbose_name='Единицы измерения',
        help_text='Введите единицы измерения')

    class Meta:
        """Параметры модели."""
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        """Метод строкового представления модели."""
        return self.name


class Tag(models.Model):
    """Модель тега"""
    name = models.CharField('Название', unique=True, max_length=50)
    color = models.CharField(
        'Цветовой HEX-код',
        unique=True,
        max_length=7,
        validators=[
            RegexValidator(
                regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Введенное значение не является цветом в формате HEX!'
            )
        ]
    )
    slug = models.SlugField('Уникальный слаг', unique=True, max_length=50)

    class Meta:
        """Параметры модели."""
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        """Метод строкового представления модели."""
        return self.name


class Recipe(models.Model):
    """Создание модели рецептов."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта',
        help_text='Введите название рецепта'
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/image/',
        help_text='Выберите изображение рецепта'
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        help_text='Введите описания рецепта',
        validators=[MaxValueValidator(256)])
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
        related_name='recipes',
        verbose_name='ингредиенты в рецепте',
        help_text='Выберите ингредиенты рецепта')
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe',
        verbose_name='Теги рецептов',
        help_text='Выберите тег рецепта')
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, message='Минимальное значение 1!'),
            MaxValueValidator(600, message='Максимальное значение 600!')
        ],
        verbose_name='Время приготовления',
        help_text='Введите время приготовления'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания')

    class Meta:
        """Параметры модели."""
        ordering = ('-pub_date', )
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        """Метод строкового представления модели."""
        return self.name


class ShoppingCart(models.Model):
    """Создание модели списка покупок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        help_text='Выберите пользователя'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shoppingcarts',
        verbose_name='Рецепты',
        help_text='Выберите рецепты для добавления в корзины'
    )

    class Meta:
        """Параметры модели."""
        verbose_name = 'Корзина'
        verbose_name_plural = 'Продуктовые корзины'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_shoppingcart')
        ]

    def __str__(self):
        """Метод строкового представления модели."""
        return f'{self.user} {self.recipe}'


class Subscription(models.Model):
    """Создание модели подписок."""
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
        return f'{self.user} {self.following}'


class IngredientAmount(models.Model):
    """Создание модели продуктов в рецепте."""
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredientamount',
        verbose_name='Ингредиенты в рецепте',
        help_text='Добавить ингредиенты для рецепта в корзину')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredientamount',
        verbose_name='Рецепт',
        help_text='Выберите рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        default=1,
        validators=[
            MinValueValidator(0.1),
            MaxValueValidator(10000)
            ],
        verbose_name='Количество ингредиента',
        help_text='Введите количество ингредиента'
    )

    class Meta:
        """Параметры модели."""
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(fields=['ingredient', 'recipe'],
                                    name='unique_ingredientamount')
        ]

    def __str__(self):
        """Метод строкового представления модели."""
        return f'{self.ingredient} {self.recipe}'


class TagRecipe(models.Model):
    """Создание модели тегов рецепта."""
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Теги',
        help_text='Выберите теги рецепта'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        help_text='Выберите рецепт')

    class Meta:
        """Параметры модели."""
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецепта'
        constraints = [
            models.UniqueConstraint(fields=['tag', 'recipe'],
                                    name='unique_tagrecipe')
        ]

    def __str__(self):
        """Метод строкового представления модели."""
        return f'{self.tag} {self.recipe}'


class Favorite(models.Model):
    """Создание модели избранных рецептов."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        help_text='Выберите пользователя'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
        help_text='Выберите рецепт'
    )

    class Meta:
        """Параметры модели."""
        verbose_name = 'Избранный'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_favorite')
        ]

    def __str__(self):
        """Метод строкового представления модели."""
        return f'{self.recipe} {self.user}'
