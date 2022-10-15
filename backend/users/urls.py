from django.urls import path
from rest_framework.routers import DefaultRouter

from api.views import SubscribeViewSet, CreateUserView

app_name = 'users'
router = DefaultRouter()

router.register('users', CreateUserView, basename='users')

urlpatterns = [
    path('users/subscriptions/',
         SubscribeViewSet.as_view({'get': 'list'}), name='subscriptions'),
    path('users/<int:users_id>/subscribe/',
         SubscribeViewSet.as_view({'post': 'create',
                                   'delete': 'delete'}), name='subscribe'),
]
