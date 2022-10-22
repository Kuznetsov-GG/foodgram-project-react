from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import CreateUserView, SubscribeViewSet


router = DefaultRouter()

router.register('users', CreateUserView, basename='users')

urlpatterns = [
    path('users/subscriptions/',
         SubscribeViewSet.as_view({'get': 'list'}), name='subscriptions'),
    path('users/<int:users_id>/subscribe/',
         SubscribeViewSet.as_view({'post': 'create',
                                   'delete': 'delete'}), name='subscribe'),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
