from django.conf import settings
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import Subscription, User

from ..serializers.users import (CustomUserSerializer, SetAvatarSerializer,
                                 SetPasswordSerializer,
                                 UserWithRecipesSerializer)
from ..utils import CustomPagination


class CustomUserViewSet(UserViewSet):
    """
    Вьюшка для работы с пользователями
    """

    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.action == "me":
            return [IsAuthenticated()]
        if self.action in ["retrieve", "list"]:
            return [AllowAny()]
        return super().get_permissions()

    @action(
        detail=False,
        methods=["POST"],
        permission_classes=[IsAuthenticated]
    )
    def set_password(self, request):
        serializer = SetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if user.check_password(serializer.data["current_password"]):
                user.set_password(serializer.data["new_password"])
                user.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"current_password": ["Неверный пароль"]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False, methods=["GET"],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(
            following__user=request.user
        ).order_by("id")
        page = self.paginate_queryset(queryset)
        if page is not None:
            recipes_limit = request.query_params.get(
                "recipes_limit", settings.RECIPES_LIMIT
            )
            serializer = UserWithRecipesSerializer(
                page,
                many=True,
                context={"request": request, "recipes_limit": recipes_limit},
            )
            return self.get_paginated_response(serializer.data)
        serializer = UserWithRecipesSerializer(
            queryset, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(
        detail=True, methods=["POST", "DELETE"],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        if request.method == "POST":
            if request.user == author:
                return Response(
                    {"errors": "Нельзя подписаться на самого себя"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if Subscription.objects.filter(
                    user=request.user,
                    author=author
            ).exists():
                return Response(
                    {"errors": "Вы уже подписаны на этого автора"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            subscription = Subscription.objects.create(
                user=request.user,
                author=author
            )
            recipes_limit = request.query_params.get(
                "recipes_limit", settings.RECIPES_LIMIT
            )
            serializer = UserWithRecipesSerializer(
                subscription.author,
                context={"request": request, "recipes_limit": recipes_limit},
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        subscription = Subscription.objects.filter(
            user=request.user, author=author
        ).first()
        if not subscription:
            return Response(
                {"errors": "Вы не подписаны на этого автора"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["PUT", "DELETE"],
        permission_classes=[IsAuthenticated],
        url_path="me/avatar",
    )
    def avatar(self, request):
        if request.method == "DELETE":
            request.user.avatar = None
            request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        if not request.data:
            return Response(
                {"avatar": ["Это поле обязательно."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = SetAvatarSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
