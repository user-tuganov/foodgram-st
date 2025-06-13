from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    SAFE_METHODS, AllowAny, BasePermission, IsAuthenticated)
from rest_framework.response import Response

from ..serializers.ingredients import IngredientSerializer
from ..serializers.recipes import (RecipeCreateUpdateSerializer,
                                   RecipeListSerializer)
from ..serializers.users import RecipeMinifiedSerializer
from ..utils import (CustomIngredientFilter, CustomPagination,
                     CustomRecipeFilter)


class IsAuthorOrReadOnly(BasePermission):
    """
    Вспомогательный метод для получения прав на изменение рецепта
    (Только автору позволено изменять)
    """

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.author == request.user


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Вьюшка для просмотра интгредиентов
    """

    queryset = Ingredient.objects.all().order_by("name")
    serializer_class = IngredientSerializer
    filter_backends = (CustomIngredientFilter,)
    search_fields = ("^name",)
    pagination_class = None
    permission_classes = (AllowAny,)

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, id=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Вьюшка для работы с рецептами
    """

    queryset = Recipe.objects.all().select_related("author")
    serializer_class = RecipeListSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = CustomPagination
    filterset_class = CustomRecipeFilter

    def get_permissions(self):
        if self.action in ["list", "retrieve", "get_link"]:
            return [AllowAny()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ("create", "partial_update", "update"):
            return RecipeCreateUpdateSerializer
        return RecipeListSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def _check_user_auth(self, request):
        if not request:
            return False
        if not request.user.is_authenticated:
            return False
        return True

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if not self._check_user_auth(request):
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if not self._check_user_auth(request):
            return False
        return ShoppingCart.objects.filter(
            user=request.user,
            recipe=obj
        ).exists()

    def _handle_m2m_action(self, request, pk, model_class, error_message):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == "POST":
            if (model_class.objects.filter(
                    user=request.user,
                    recipe=recipe)
                    .exists()):
                return Response(
                    {"errors": error_message},
                    status=status.HTTP_400_BAD_REQUEST
                )
            model_class.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeMinifiedSerializer(
                recipe,
                context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        obj = model_class.objects.filter(
            user=request.user,
            recipe=recipe
        ).first()
        if not obj:
            return Response(
                {"errors": "Рецепт не найден в списке"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        return self._handle_m2m_action(
            request, pk, Favorite, "Рецепт уже добавлен в избранное"
        )

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        return self._handle_m2m_action(
            request, pk, ShoppingCart, "Рецепт уже добавлен в список покупок"
        )

    @action(
        detail=False,
        methods=["GET"],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        ingredients = (
            IngredientInRecipe.objects.filter(
                recipe__shopping_cart__user=request.user
            )
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(total_amount=Sum("amount"))
            .order_by("ingredient__name")
        )

        shopping_list = ["Список покупок:\n\n"]
        for item in ingredients:
            shopping_list.append(
                f'- {item["ingredient__name"]} '
                f'({item["ingredient__measurement_unit"]}) '
                f'- {item["total_amount"]}\n'
            )

        response = HttpResponse(
            "".join(shopping_list),
            content_type="text/plain; charset=utf-8"
        )
        response["Content-Disposition"] = \
            'attachment; filename="shopping_list.txt"'
        return response

    @action(detail=True, methods=["GET"], url_path="get-link")
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        url = request.build_absolute_uri(f"/api/recipes/{recipe.id}/")
        return Response({"short-link": url})
