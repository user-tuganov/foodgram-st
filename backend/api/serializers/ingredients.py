from django.core.validators import MinValueValidator
from recipes.models import Ingredient, IngredientInRecipe
from rest_framework import serializers


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для ингредиентов
    """

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для связи ингредиента с рецептом
    """

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source="ingredient"
    )
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )
    amount = serializers.IntegerField(
        validators=[MinValueValidator(1)],
        error_messages={
            "min_value": "Количество ингредиента должно быть больше 0"
        },
    )

    class Meta:
        model = IngredientInRecipe
        fields = ("id", "name", "measurement_unit", "amount")
