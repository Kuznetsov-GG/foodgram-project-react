from http import HTTPStatus

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Subscription, Tag)
from users.models import User
from .filters import RecipeFilter, SearchIngredientFilter
from .mixins import BaseFavoriteCartViewSetMixin
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeSerializer, RecipeSerializerPost,
                          RegistrationSerializer, ShoppingCartSerializer,
                          SubscriptionSerializer, TagSerializer)


class CreateUserView(UserViewSet):
    serializer_class = RegistrationSerializer

    def get_queryset(self):
        return User.objects.all()


class SubscribeViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)

    def create(self, request, *args, **kwargs):
        user_id = self.kwargs.get('users_id')
        user = request.user
        author = get_object_or_404(User, id=user_id)
        if user == author:
            return Response(
                'Нельзя подписаться на себя',
                status=status.HTTP_400_BAD_REQUEST
            )
        if Subscription.objects.filter(user=user, author=author).exists():
            return Response(
                'Такая подписка уже существует',
                status=status.HTTP_400_BAD_REQUEST
            )
        follow = Subscription.objects.create(user=user, author=author)
        serializer = SubscriptionSerializer(
            follow.author, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        author_id = self.kwargs['users_id']
        user_id = request.user.id
        subscribe = get_object_or_404(
            Subscription, user__id=user_id, following__id=author_id)
        subscribe.delete()
        return Response(HTTPStatus.NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_class = RecipeFilter
    filter_backends = [DjangoFilterBackend, ]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):

        if self.request.method == 'GET':
            return RecipeSerializer
        return RecipeSerializerPost


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend, SearchIngredientFilter)
    pagination_class = None
    search_fields = ['^name', ]


class FavoriteViewSet(BaseFavoriteCartViewSetMixin):
    serializer_class = FavoriteSerializer
    queryset = Favorite.objects.all()
    model = Favorite


class ShoppingCartViewSet(BaseFavoriteCartViewSetMixin):
    serializer_class = ShoppingCartSerializer
    queryset = ShoppingCart.objects.all()
    model = ShoppingCart


class DownloadShoppingCart(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'],)
    def download(self, request):
        final_list = IngredientAmount.objects.filter(
            recipe__shoppingcarts__user=request.user).values(
            'ingredient__name', 'ingredient__measurement_unit').order_by(
                'ingredient__name').annotate(ingredient_total=Sum('amount'))
        pdfmetrics.registerFont(
            TTFont('FreeSans', 'data/FreeSans.ttf', 'UTF-8'))
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = ('attachment; '
                                           'filename="shopping_cart.pdf"')
        page = canvas.Canvas(response)
        page.setFont('FreeSans', size=20)
        page.drawString(250, 800, 'Список покупок')
        page.setFont('FreeSans', size=16)
        height = 750
        for number, item in enumerate(final_list, start=1):
            page.drawString(
                75,
                height,
                f'{number}.  {item["ingredient__name"]} - '
                f'{item["ingredient_total"]}'
                f' {item["ingredient__measurement_unit"]}'
            )
            height -= 30
        page.showPage()
        page.save()
        return response
