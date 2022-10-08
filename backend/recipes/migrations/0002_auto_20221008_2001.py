# Generated by Django 2.2.20 on 2022-10-08 15:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('recipes', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='following',
            field=models.ForeignKey(help_text='Выберите автора, на которого подписываются', on_delete=django.db.models.deletion.CASCADE, related_name='following', to=settings.AUTH_USER_MODEL, verbose_name='Автор'),
        ),
        migrations.AddField(
            model_name='subscription',
            name='user',
            field=models.ForeignKey(help_text='Выберите пользователя, который подписывается', on_delete=django.db.models.deletion.CASCADE, related_name='follower', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AddField(
            model_name='shoppingcart',
            name='recipe',
            field=models.ForeignKey(help_text='Выберите рецепты для добавления в корзины', on_delete=django.db.models.deletion.CASCADE, related_name='shoppingcarts', to='recipes.Recipe', verbose_name='Рецепты'),
        ),
        migrations.AddField(
            model_name='shoppingcart',
            name='user',
            field=models.ForeignKey(help_text='Выберите пользователя', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='author',
            field=models.ForeignKey(help_text='Выберите автора рецепта', on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to=settings.AUTH_USER_MODEL, verbose_name='Автор'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(help_text='Выберите ингредиенты рецепта', related_name='recipes', through='recipes.IngredientAmount', to='recipes.Ingredient', verbose_name='ингредиенты в рецепте'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(help_text='Выберите тег рецепта', through='recipes.TagRecipe', to='recipes.Tag', verbose_name='Тег рецепта'),
        ),
        migrations.AddField(
            model_name='ingredientamount',
            name='ingredient',
            field=models.ForeignKey(help_text='Добавить ингредиенты для рецепта в корзину', on_delete=django.db.models.deletion.CASCADE, related_name='ingredientamount', to='recipes.Ingredient', verbose_name='Ингредиенты в рецепте'),
        ),
        migrations.AddField(
            model_name='ingredientamount',
            name='recipe',
            field=models.ForeignKey(help_text='Выберите рецепт', on_delete=django.db.models.deletion.CASCADE, related_name='ingredientamount', to='recipes.Recipe', verbose_name='Рецепт'),
        ),
        migrations.AddField(
            model_name='favorite',
            name='recipe',
            field=models.ForeignKey(help_text='Выберите рецепт', on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to='recipes.Recipe', verbose_name='Рецепт'),
        ),
        migrations.AddField(
            model_name='favorite',
            name='user',
            field=models.ForeignKey(help_text='Выберите пользователя', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AddConstraint(
            model_name='tagrecipe',
            constraint=models.UniqueConstraint(fields=('tag', 'recipe'), name='unique_tagrecipe'),
        ),
        migrations.AddConstraint(
            model_name='subscription',
            constraint=models.UniqueConstraint(fields=('user', 'following'), name='unique_subscribe'),
        ),
        migrations.AddConstraint(
            model_name='shoppingcart',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_shoppingcart'),
        ),
        migrations.AddConstraint(
            model_name='ingredientamount',
            constraint=models.UniqueConstraint(fields=('ingredient', 'recipe'), name='unique_ingredientamount'),
        ),
        migrations.AddConstraint(
            model_name='favorite',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_favorite'),
        ),
    ]
