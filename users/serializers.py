import re
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password2 = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password2',
            'phone_number', 'nickname', 'gender', 'avatar'
        ]

    @staticmethod
    def validate_email(value):
        # 邮箱正则验证
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', value):
            raise serializers.ValidationError("Invalid email format.")
        return value

    @staticmethod
    def validate_phone_number(value):
        # 手机号唯一验证（模型已设置 unique，但这里可加格式验证）
        if value and not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError("Invalid phone number format.")
        return value

    @staticmethod
    def validate(data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    @staticmethod
    def create(validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, help_text="Username, email or phone number")
    password = serializers.CharField(write_only=True)

    @staticmethod
    def validate(data):
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            raise serializers.ValidationError("Both username and password are required.")

        # 尝试使用 username 字段查询用户（支持用户名、邮箱、手机号）
        try:
            if '@' in username:
                user = User.objects.get(email=username)
            elif username.isdigit() and len(username) == 11:
                user = User.objects.get(phone_number=username)
            else:
                user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError("No active account found with the given credentials.")

        # 验证密码
        if not user.check_password(password):
            raise serializers.ValidationError("Incorrect password.")

        data['user'] = user
        return data


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone_number', 'nickname',
            'gender', 'avatar', 'user_uuid', 'date_joined'
        ]