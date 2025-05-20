from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from .models import User


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'role')


class CustomUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'role') 