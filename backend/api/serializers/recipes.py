from django.core.validators import MinValueValidator
from recipes.models import Favorite, IngredientInRecipe, Recipe, ShoppingCart
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
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if not request:
            return False
        if not request.user.is_authenticated:
            return False
        return ShoppingCart.objects.filter(
            user=request.user,
            recipe=obj
        ).exists()

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
        validators=[MinValueValidator(1)],
        error_messages={
            "min_value": "Время приготовления должно быть больше 0"
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
        used_ingredients = []
        for item in value:
            ingredient = item["ingredient"]
            if ingredient in used_ingredients:
                raise serializers.ValidationError(
                    "Ингредиенты не должны повторяться"
                )
            used_ingredients.append(ingredient)
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

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients_data:
            IngredientInRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient["ingredient"],
                amount=ingredient["amount"],
            )
        return recipe

    def update(self, instance, validated_data):
        if "ingredients" in validated_data:
            ingredients_data = validated_data.pop("ingredients")
            instance.ingredients.clear()
            for ingredient_data in ingredients_data:
                IngredientInRecipe.objects.create(
                    recipe=instance,
                    ingredient=ingredient_data["ingredient"],
                    amount=ingredient_data["amount"],
                )
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        serializer = RecipeListSerializer(
            instance, context={"request": self.context.get("request")}
        )
        return serializer.data
