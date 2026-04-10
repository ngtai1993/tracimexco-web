from django.db import models

from common.models import BaseModel


class WebhookEndpoint(BaseModel):
    """
    Endpoint nhận callback (incoming) từ nền tảng bên ngoài.
    secret_key: dùng để verify chữ ký HMAC của incoming request.
    """

    platform = models.ForeignKey(
        "platforms.Platform",
        on_delete=models.CASCADE,
        related_name="webhook_endpoints",
    )
    # URL mà nền tảng sẽ gửi callback về — thường là /api/v1/platforms/incoming/<slug>/
    endpoint_url = models.URLField(
        help_text="URL nhận callback từ nền tảng (incoming)."
    )
    # JSON array: ["publish_success", "publish_error", "engagement"]
    event_types = models.JSONField(default=list)
    secret_key = models.CharField(
        max_length=500,
        help_text="Secret key để verify HMAC signature của incoming webhook.",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "platforms_webhook_endpoints"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Endpoint for {self.platform.name}"
