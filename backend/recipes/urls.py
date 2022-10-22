from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
     FavoriteViewSet, IngredientViewSet,
     RecipeViewSet, ShoppingCartViewSet,
     TagViewSet,
)

router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')

urlpatterns = [
    path('recipes/<int:recipes_id>/shopping_cart/',
         ShoppingCartViewSet.as_view(
          {'post': 'create', 'delete': 'delete'}), name='shoppingcart'),
    path('recipes/<int:recipes_id>/favorite/',
         FavoriteViewSet.as_view({'post': 'create',
                                  'delete': 'delete'}), name='favorite'),
    path('recipes/download_shopping_cart/',
         RecipeViewSet.as_view(
          {'get': 'download_shoping_cart'}), name='download'),
    path('', include(router.urls)),
]
