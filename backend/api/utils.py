import base64
import uuid

from django.core.files.base import ContentFile
from django_filters import rest_framework as filters
from recipes.models import Ingredient, Recipe
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination


class Base64ImageField(serializers.ImageField):
    """Поле для работы с изображениями в формате base64"""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            id = uuid.uuid4()
            data = ContentFile(base64.b64decode(imgstr), name=f"{id}.{ext}")
        return super().to_internal_value(data)


class CustomPagination(PageNumberPagination):
    """Кастомный класс пагинации"""

    page_size = 6
    page_size_query_param = "limit"


class CustomIngredientFilter(filters.FilterSet):
    """Кастомный фильтр для ингредиентов"""

    name = filters.CharFilter(method="filter_name")

    def filter_name(self, queryset, name, value):
        return queryset.filter(name__istartswith=value).order_by("name")

    class Meta:
        model = Ingredient
        fields = ("name",)


class CustomRecipeFilter(filters.FilterSet):
    """Кастомный фильтр для рецептов"""

    is_favorited = filters.BooleanFilter(method="filter_is_favorited")
    is_in_shopping_cart = filters.BooleanFilter(
        method="filter_is_in_shopping_cart"
    )

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorites__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(shoppingcarts__user=user)
        return queryset

    class Meta:
        model = Recipe
        fields = ("author", "is_favorited", "is_in_shopping_cart")
