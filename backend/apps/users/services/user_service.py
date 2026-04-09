from django.db import transaction
from apps.users.models import User
from apps.users.exceptions import UserNotFoundError, InvalidPasswordError


def create_user(email: str, password: str, full_name: str = "") -> User:
    """Tạo user mới."""
    with transaction.atomic():
        user = User.objects.create_user(
            email=email,
            password=password,
            full_name=full_name,
        )
    return user


def update_profile(user: User, full_name: str = None, username: str = None, avatar=None) -> User:
    """Cập nhật thông tin profile của user."""
    if full_name is not None:
        user.full_name = full_name
    if username is not None:
        user.username = username
    if avatar is not None:
        user.avatar = avatar
    user.save(update_fields=["full_name", "username", "avatar", "updated_at"])
    return user


def change_password(user: User, old_password: str, new_password: str) -> None:
    """Đổi mật khẩu cho user đã đăng nhập."""
    if not user.check_password(old_password):
        raise InvalidPasswordError("Mật khẩu cũ không đúng.")
    user.set_password(new_password)
    user.save(update_fields=["password", "updated_at"])


def deactivate_user(user_id: str) -> None:
    """Vô hiệu hóa tài khoản user."""
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise UserNotFoundError(f"Không tìm thấy user với id={user_id}")
    user.is_active = False
    user.save(update_fields=["is_active", "updated_at"])


def update_user_by_admin(user_id: str, **fields) -> User:
    """Admin cập nhật thông tin user."""
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise UserNotFoundError(f"Không tìm thấy user với id={user_id}")
    allowed = {"is_active", "is_staff"}
    for key, value in fields.items():
        if key in allowed:
            setattr(user, key, value)
    user.save()
    return user
