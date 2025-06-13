from django.conf import settings
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import Recipe
from rest_framework import serializers
from users.models import Subscription

from ..utils import Base64ImageField

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя"""

    class Meta:
        model = User
        fields = ("id", "email", "username", "password",
                  "first_name", "last_name")


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """
    Сериализатор для укороченного рецепта
    """

    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")

    def get_image(self, obj):
        request = self.context.get("request")
        if not request:
            return None
        if not obj.image:
            return None
        return request.build_absolute_uri(obj.image.url)


class CustomUserSerializer(UserSerializer):
    """Сериализатор для получения информации о пользователе"""

    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False)

    class Meta:
        model = User
        fields = (
            "id",
            "avatar",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if not request:
            return False
        if not request.user.is_authenticated:
            return False
        return Subscription.objects.filter(
            user=request.user,
            author=obj
        ).exists()


class UserWithRecipesSerializer(CustomUserSerializer):
    """
    Сериализатор для получения пользователя с рецептами
    """

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        model = User
        fields = (
            "id",
            "avatar",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        limit = self.context.get("recipes_limit", settings.RECIPES_LIMIT)
        if limit:
            try:
                limit = int(limit)
                if limit > 0:
                    recipes = recipes[:limit]
            except (ValueError, TypeError):
                pass
        serializer = RecipeMinifiedSerializer(
            recipes, many=True, context={
                "request": self.context.get("request")
            }
        )
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SetPasswordSerializer(serializers.Serializer):
    """
    Сериализатор для изменения пароля
    """

    current_password = serializers.CharField()
    new_password = serializers.CharField()


class SetAvatarSerializer(serializers.ModelSerializer):
    """
    Сериализатор для смены аватара пользователя
    """

    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ("avatar",)


class SubscriptionSerializer(CustomUserSerializer):
    """Сериализатор для подписок"""

    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = (CustomUserSerializer.Meta.fields + (
            "recipes_count", "recipes"
        ))

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        from api.serializers.recipes import RecipeMinifiedSerializer

        request = self.context.get("request")
        recipes_limit = request.query_params.get(
            "recipes_limit"
        ) if request else None
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = recipes[: int(recipes_limit)]
        return RecipeMinifiedSerializer(
            recipes, many=True, context={"request": request}
        ).data
