from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from users.models import User
from recipes.models import Ingredient, IngredientAmount, Recipe, Tag, TagRecipe
from .mixins import CommonCountMixin, CommonRecipeMixin, CommonSubscribedMixin


class RegistrationSerializer(UserCreateSerializer, CommonSubscribedMixin):
    """Создание сериализатора модели пользователя."""
    class Meta:
        """Мета параметры сериализатора модели пользователя."""
        model = User
        fields = ('id', 'username', 'email', 'first_name',
                  'last_name', 'is_subscribed', 'password')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def to_representation(self, obj):
        """Метод представления результатов сериализатора."""
        result = super(RegistrationSerializer, self).to_representation(obj)
        result.pop('password', None)
        return result


class IngredientSerializer(serializers.ModelSerializer):
    """Создание сериализатора модели продуктов."""

    class Meta:
        """Мета параметры сериализатора модели продуктов."""
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientAmountSerializer(serializers.ModelSerializer):
    """Создание сериализатора модели продуктов в рецепте для чтения."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )

    class Meta:
        """Мета параметры сериализатора модели продуктов в рецепте."""
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientAmountRecipeSerializer(serializers.ModelSerializer):
    """Создание сериализатора продуктов с количеством для записи."""
    id = serializers.IntegerField(source='ingredient.id')

    class Meta:
        """Мета параметры сериализатора продуктов с количеством."""
        model = IngredientAmount
        fields = ('id', 'amount')


class TagSerializer(serializers.ModelSerializer):
    """Создание сериализатора модели тегов."""

    class Meta:
        """Мета параметры сериализатора модели тегов."""
        model = Tag
        fields = '__all__'


class FavoriteSerializer(serializers.Serializer):
    """Создание сериализатора избранных рецептов."""
    id = serializers.IntegerField()
    name = serializers.CharField()
    cooking_time = serializers.IntegerField()
    image = Base64ImageField(max_length=None, use_url=False,)


class ShoppingCartSerializer(serializers.Serializer):
    """Создание сериализатора корзины."""
    id = serializers.IntegerField()
    name = serializers.CharField()
    cooking_time = serializers.IntegerField()
    image = Base64ImageField(max_length=None, use_url=False,)


class RecipeSerializer(serializers.ModelSerializer,
                       CommonRecipeMixin):
    """Сериализатор модели рецептов."""
    author = RegistrationSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = IngredientAmountSerializer(
        source='ingredientamount',
        many=True)
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        """Мета параметры сериализатора модели рецептов."""
        model = Recipe
        fields = ('id', 'author', 'name', 'image', 'text',
                  'ingredients', 'tags', 'cooking_time',
                  'is_in_shopping_cart', 'is_favorited')


class RecipeSerializerPost(serializers.ModelSerializer,
                           CommonRecipeMixin):
    """Сериализатор модели рецептов."""
    author = RegistrationSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True)
    image = Base64ImageField(max_length=None, use_url=False,)
    ingredients = IngredientAmountRecipeSerializer(
        source='ingredientamount', many=True)

    class Meta:
        """Мета параметры сериализатора модели рецептов."""
        model = Recipe
        fields = ('id', 'author', 'name', 'image', 'text',
                  'ingredients', 'tags', 'cooking_time',
                  'is_in_shopping_cart', 'is_favorited')

    def validate_ingredients(self, ingredients):
        """Метод валидации продуктов в рецепте."""
        ingredients_list = []
        for ingredient in ingredients:
            id_to_check = ingredient.get('id')
            ingredient_to_check = get_object_or_404(Ingredient, id=id_to_check)
            if int(ingredient['amount']) <= 0:
                raise serializers.ValidationError(
                    'Количество ингредиента должно быть больше 0')
            if ingredient_to_check in ingredients_list:
                raise serializers.ValidationError(
                    'Данные ингредиенты повторяются в рецепте!')
            ingredients_list.append(ingredient_to_check)
        return ingredients

    def validate_tags(self, value):
        """Метод проверки на повтояемость существующих тегов в БД."""
        tag_list = []
        for tag in value:
            tag_to_check = Tag.objects.filter(id=tag['id'])
            if not tag_to_check.exists():
                raise serializers.ValidationError('Нет такого тэга!')
            if tag_to_check in tag_list:
                raise serializers.ValidationError('Уже есть такие тэги!')
            tag_list.append(tag_to_check)
        return value

    def add_tags_and_ingredients(self, tags_data, ingredients, recipe):
        """Метод добавления тегов и ингридиентов."""
        for tag_data in tags_data:
            recipe.tags.add(tag_data)
        ingredient_list = []
        for ingredient in ingredients:
            new_ingredient = IngredientAmount(
                recipe=recipe,
                id_to_check=ingredient.get('id'),
                amount=ingredient['amount']
                )
            ingredient_list.append(new_ingredient)
        IngredientAmount.objects.bulk_create(ingredient_list)
        return recipe

    def create(self, validated_data):
        """Метод создания рецептов."""
        tags_data = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredientamount')
        recipe = Recipe.objects.create(**validated_data)
        self.add_tags_and_ingredients(tags_data, ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        """Метод редактирования ингредиентов."""
        tags_data = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredientamount')
        TagRecipe.objects.filter(recipe=instance).delete()
        IngredientAmount.objects.filter(recipe=instance).delete()
        instance = self.add_tags_and_ingredients(
            tags_data, ingredients, instance)
        super().update(instance, validated_data)
        return instance


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для краткого отображения сведений о рецепте."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cooking_time', 'image')


class SubscriptionSerializer(serializers.ModelSerializer,
                             CommonSubscribedMixin, CommonCountMixin):
    """Сериализатор для списка подписок."""
    recipes = serializers.SerializerMethodField()

    class Meta:
        """Мета параметры сериализатора списка подписок."""
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        """Метод получения данных рецептов автора."""
        request = self.context.get('request')
        queryset = Recipe.objects.filter(author__id=obj.id).order_by('id')
        if request.GET.get('recipes_limit'):
            recipes_limit = int(request.GET.get('recipes_limit'))
            queryset = Recipe.objects.filter(author__id=obj.id).order_by('id')[
                :recipes_limit]
        return ShortRecipeSerializer(queryset, many=True).data
