from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from recipes.models import IngredientInRecipe, Recipe
from rest_framework import serializers

from ..utils import Base64ImageField
from .ingredients import IngredientInRecipeSerializer
from .users import CustomUserSerializer


class RecipeListSerializer(serializers.ModelSerializer):
    """
    Сериализатор для рецептов
    """

    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source="ingredientinrecipe_set", many=True, read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "text",
            "cooking_time",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
        )

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if not request:
            return False
        if not request.user.is_authenticated:
            return False
        return obj.favorites.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if not request:
            return False
        if not request.user.is_authenticated:
            return False
        return obj.shoppingcarts.filter(user=request.user).exists()

    def get_image(self, obj):
        request = self.context.get("request")
        if not request:
            return None
        if not obj.image:
            return None
        return request.build_absolute_uri(obj.image.url)


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и изменения рецептов
    """

    ingredients = IngredientInRecipeSerializer(many=True)
    image = Base64ImageField(required=True)
    cooking_time = serializers.IntegerField(
        validators=[
            MinValueValidator(settings.MIN_COOKING_TIME),
            MaxValueValidator(settings.MAX_COOKING_TIME)
        ],
        error_messages={
            "min_value": "Время приготовления должно быть больше 0",
            "max_value": "Время приготовления не может быть больше 32_000"
        },
    )
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
            "author",
        )

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                "Необходимо указать хотя бы один ингредиент"
            )
        used_ingredients = set()
        for item in value:
            ingredient = item["ingredient"]
            if ingredient in used_ingredients:
                raise serializers.ValidationError(
                    "Ингредиенты не должны повторяться"
                )
            used_ingredients.add(ingredient)
        return value

    def validate(self, data):
        if "ingredients" not in data:
            raise serializers.ValidationError(
                {"ingredients": "Это поле обязательно"}
            )
        if not data.get("image"):
            raise serializers.ValidationError(
                {"image": "Это поле обязательно"}
            )
        return data

    def _create_ingredients(self, recipe, ingredients_data):
        """Создание ингредиентов для рецепта"""
        IngredientInRecipe.objects.bulk_create(
            IngredientInRecipe(
                recipe=recipe,
                ingredient=data["ingredient"],
                amount=data["amount"]
            ) for data in ingredients_data
        )

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data)
        self._create_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        if "ingredients" in validated_data:
            ingredients_data = validated_data.pop("ingredients")
            instance.ingredients.clear()
            self._create_ingredients(instance, ingredients_data)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        serializer = RecipeListSerializer(
            instance, context={"request": self.context.get("request")}
        )
        return serializer.data
