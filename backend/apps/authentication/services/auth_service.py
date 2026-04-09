import secrets
import logging
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from apps.users.models import User
from apps.users.selectors import get_user_by_email
from apps.users.exceptions import UserNotFoundError
from apps.authentication.models import PasswordResetToken
from apps.authentication.exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
)

logger = logging.getLogger(__name__)


def login(email: str, password: str) -> dict:
    """Xác thực user và trả về JWT tokens."""
    user = authenticate(username=email, password=password)
    if user is None:
        raise InvalidCredentialsError("Email hoặc mật khẩu không đúng.")
    if not user.is_active:
        raise InvalidCredentialsError("Tài khoản đã bị vô hiệu hóa.")

    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": user,
    }


def logout(refresh_token: str) -> None:
    """Blacklist refresh token để đăng xuất."""
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except TokenError as exc:
        raise InvalidTokenError("Token không hợp lệ hoặc đã hết hạn.") from exc


def refresh_access_token(refresh_token: str) -> dict:
    """Lấy access token mới từ refresh token."""
    try:
        token = RefreshToken(refresh_token)
        return {"access": str(token.access_token)}
    except TokenError as exc:
        raise InvalidTokenError("Token không hợp lệ hoặc đã hết hạn.") from exc


def request_password_reset(email: str) -> None:
    """Tạo token reset và gửi email (nếu email tồn tại)."""
    try:
        user = get_user_by_email(email)
    except UserNotFoundError:
        # Không lộ thông tin user tồn tại hay không
        logger.info("Password reset requested for non-existent email: %s", email)
        return

    # Xóa token cũ chưa dùng của user này
    PasswordResetToken.objects.filter(user=user, is_used=False).delete()

    token_value = secrets.token_urlsafe(32)
    PasswordResetToken.objects.create(user=user, token=token_value)

    # Import tại đây để tránh circular import
    from tasks.email_tasks import send_password_reset_email
    reset_link = f"{settings.FRONTEND_URL if hasattr(settings, 'FRONTEND_URL') else 'http://localhost:3000'}/reset-password?token={token_value}"
    send_password_reset_email.delay(user.email, reset_link)


def confirm_password_reset(token: str, new_password: str) -> None:
    """Xác nhận token và đặt mật khẩu mới."""
    expiry_hours = getattr(settings, "PASSWORD_RESET_TOKEN_EXPIRY_HOURS", 24)
    expiry_time = timezone.now() - timedelta(hours=expiry_hours)

    try:
        reset_token = PasswordResetToken.objects.select_related("user").get(
            token=token,
            is_used=False,
            created_at__gte=expiry_time,
        )
    except PasswordResetToken.DoesNotExist:
        raise InvalidTokenError("Token không hợp lệ hoặc đã hết hạn.")

    user = reset_token.user
    user.set_password(new_password)
    user.save(update_fields=["password"])

    reset_token.is_used = True
    reset_token.save(update_fields=["is_used"])
