# serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class TokenObtainSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class TokenRefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


class EditUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['profile_img','first_name','last_name','roles']
        depth=1
    
    # def update(self, instance, validated_data):
    #     print(validated_data,"---------------validated_data----------")
    #     profile_img = validated_data.get('profile_img', None)
    #     roles = validated_data.get('roles', None)

    #     # Update profile_img if provided
    #     if profile_img:
    #         instance.profile_img = profile_img

    #     # Update roles if provided
    #     if roles is not None:
    #         instance.roles.clear()
    #         for role in roles.split(','):
    #             role_inst, _ = Role.objects.get_or_create(name=role)
    #             instance.roles.add(role_inst)
    #     elif roles == '':
    #         instance.roles.clear()

    #     # Update other fields
    #     for field, value in validated_data.items():
    #         if field not in ['profile_img', 'roles']:
    #             setattr(instance, field, value)

    #     instance.save()
    #     return instance
    # def create(self, validated_data):
    #     user = User.objects.create_user(**validated_data)
    #     return user
    
    
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['name']