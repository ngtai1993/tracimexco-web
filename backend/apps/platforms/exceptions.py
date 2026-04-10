class PlatformNotFound(Exception):
    """Không tìm thấy nền tảng."""
    pass


class WebhookEndpointNotFound(Exception):
    """Không tìm thấy webhook endpoint."""
    pass


class InvalidWebhookSignature(Exception):
    """Chữ ký webhook không hợp lệ."""
    pass


class WebhookDeliveryError(Exception):
    """Gửi webhook thất bại."""
    pass
