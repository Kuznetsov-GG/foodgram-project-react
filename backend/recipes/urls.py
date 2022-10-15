from django.urls import path
from rest_framework.routers import DefaultRouter

from api.views import (DownloadShoppingCart,
                       FavoriteViewSet,
                       ShoppingCartViewSet,
                       RecipeViewSet)

app_name = 'recipes'

router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('recipes/<int:recipes_id>/shopping_cart/',
         ShoppingCartViewSet.as_view(
          {'post': 'create', 'delete': 'delete'}), name='shoppingcart'),
    path('recipes/<int:recipes_id>/favorite/',
         FavoriteViewSet.as_view({'post': 'create',
                                  'delete': 'delete'}), name='favorite'),
    path('recipes/download_shopping_cart/',
         DownloadShoppingCart.as_view({'get': 'download'}), name='download'),
]
