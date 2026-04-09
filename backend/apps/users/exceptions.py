class UserNotFoundError(Exception):
    """User không tồn tại trong hệ thống."""
    pass


class InvalidPasswordError(Exception):
    """Mật khẩu cũ không đúng khi đổi mật khẩu."""
    pass
