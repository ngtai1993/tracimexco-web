from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from apps.users.models import User


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer để tạo user mới (đăng ký)."""

    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "password_confirm", "full_name"]

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError({"password_confirm": "Mật khẩu xác nhận không khớp."})
        return attrs


class UserOutputSerializer(serializers.ModelSerializer):
    """Serializer trả về thông tin user — read only."""

    class Meta:
        model = User
        fields = ["id", "email", "username", "full_name", "avatar", "date_joined"]
        read_only_fields = fields


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer để user tự cập nhật profile."""

    class Meta:
        model = User
        fields = ["username", "full_name", "avatar"]


class AdminUserOutputSerializer(serializers.ModelSerializer):
    """Serializer trả về thông tin user cho admin."""

    class Meta:
        model = User
        fields = ["id", "email", "username", "full_name", "is_active", "is_staff", "date_joined"]
        read_only_fields = fields


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    """Serializer để admin cập nhật user."""

    class Meta:
        model = User
        fields = ["is_active", "is_staff"]
