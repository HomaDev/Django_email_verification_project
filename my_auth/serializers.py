from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from django.contrib import auth

from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=8, write_only=True)
    confirm_password = serializers.CharField(max_length=68, min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'confirm_password']

    def validate(self, attrs):
        email = attrs.get('email', '')
        username = attrs.get('username', '')
        password = attrs.get('password', '')
        confirm_password = attrs.get('confirm_password', '')
        if not password == confirm_password:
            raise serializers.ValidationError('Password and confirm_password is not the same')
        if not username.isalnum():
            raise serializers.ValidationError('The username should only contain alphanumeric characters')
        del(attrs['confirm_password'])
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
