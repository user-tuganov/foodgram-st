from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Ingredient
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from ..serializers.ingredients import IngredientSerializer
from ..utils import CustomIngredientFilter


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Вьюшка для работы с ингредиентами
    """

    queryset = Ingredient.objects.all()
    queryset = queryset.order_by("name")
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CustomIngredientFilter
    search_fields = ["^name"]
    pagination_class = None
    permission_classes = [AllowAny]

    def get_object(self):
        ingredients = self.get_queryset()
        ingredient_id = self.kwargs["pk"]
        ingredient = get_object_or_404(ingredients, id=ingredient_id)
        self.check_object_permissions(self.request, ingredient)
        return ingredient
