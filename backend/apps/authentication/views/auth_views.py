from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status

from apps.authentication.serializers import (
    RegisterSerializer,
    LoginSerializer,
    LogoutSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
from apps.authentication import services as auth_services
from apps.users import services as user_services
from apps.users.serializers import UserOutputSerializer
from apps.authentication.exceptions import InvalidCredentialsError, InvalidTokenError
from apps.users.exceptions import InvalidPasswordError


class RegisterView(APIView):
    """Đăng ký tài khoản mới."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        from apps.users.models import User
        if User.objects.filter(email=data["email"]).exists():
            return Response(
                {
                    "data": None,
                    "message": "Dữ liệu không hợp lệ",
                    "errors": {"email": ["Email này đã được sử dụng."]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = user_services.create_user(
            email=data["email"],
            password=data["password"],
            full_name=data.get("full_name", ""),
        )
        from tasks.email_tasks import send_welcome_email
        send_welcome_email.delay(user.email, user.full_name or user.email)

        out = UserOutputSerializer(user)
        return Response(
            {"data": out.data, "message": "Tài khoản tạo thành công", "errors": None},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """Đăng nhập — trả về JWT tokens."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            result = auth_services.login(data["email"], data["password"])
        except InvalidCredentialsError as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user_data = UserOutputSerializer(result["user"]).data
        return Response(
            {
                "data": {
                    "access": result["access"],
                    "refresh": result["refresh"],
                    "user": user_data,
                },
                "message": "Đăng nhập thành công",
                "errors": None,
            }
        )


class LogoutView(APIView):
    """Đăng xuất — blacklist refresh token."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            auth_services.logout(serializer.validated_data["refresh"])
        except InvalidTokenError as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"data": None, "message": "Đăng xuất thành công", "errors": None})


class TokenRefreshView(APIView):
    """Lấy access token mới từ refresh token."""

    permission_classes = [AllowAny]

    def post(self, request):
        refresh = request.data.get("refresh", "")
        try:
            result = auth_services.refresh_access_token(refresh)
        except InvalidTokenError as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return Response({"data": result, "message": "Token đã được làm mới", "errors": None})


class ChangePasswordView(APIView):
    """Đổi mật khẩu khi đã đăng nhập."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            user_services.change_password(
                user=request.user,
                old_password=data["old_password"],
                new_password=data["new_password"],
            )
        except InvalidPasswordError as e:
            return Response(
                {
                    "data": None,
                    "message": "Dữ liệu không hợp lệ",
                    "errors": {"old_password": [str(e)]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"data": None, "message": "Mật khẩu đã được cập nhật", "errors": None})


class PasswordResetRequestView(APIView):
    """Yêu cầu gửi email reset mật khẩu."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        auth_services.request_password_reset(serializer.validated_data["email"])
        return Response(
            {
                "data": None,
                "message": "Nếu email tồn tại, chúng tôi đã gửi hướng dẫn reset mật khẩu.",
                "errors": None,
            }
        )


class PasswordResetConfirmView(APIView):
    """Xác nhận token và đặt mật khẩu mới."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            auth_services.confirm_password_reset(data["token"], data["new_password"])
        except InvalidTokenError as e:
            return Response(
                {
                    "data": None,
                    "message": "Dữ liệu không hợp lệ",
                    "errors": {"token": [str(e)]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"data": None, "message": "Mật khẩu đã được đặt lại thành công", "errors": None}
        )
