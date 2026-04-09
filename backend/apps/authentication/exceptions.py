class InvalidCredentialsError(Exception):
    """Email hoặc mật khẩu sai."""
    pass


class InvalidTokenError(Exception):
    """Token không hợp lệ hoặc đã hết hạn."""
    pass
