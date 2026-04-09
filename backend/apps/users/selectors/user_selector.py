from apps.users.models import User
from apps.users.exceptions import UserNotFoundError


def get_user_by_id(user_id: str) -> User:
    """Lấy user theo id, raise nếu không tìm thấy."""
    try:
        return User.objects.get(id=user_id, is_active=True)
    except User.DoesNotExist:
        raise UserNotFoundError(f"Không tìm thấy user với id={user_id}")


def get_user_by_email(email: str) -> User:
    """Lấy user theo email, raise nếu không tìm thấy."""
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        raise UserNotFoundError(f"Không tìm thấy user với email={email}")


def list_users(is_active: bool = None, search: str = None):
    """Trả QuerySet danh sách user với filter tùy chọn."""
    qs = User.objects.all()
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    if search:
        qs = qs.filter(email__icontains=search) | qs.filter(full_name__icontains=search)
    return qs
