from django.db import models

from common.models import BaseModel
from apps.platforms.constants import WebhookDirection


class WebhookLog(BaseModel):
    """Ghi nhận mọi HTTP request/response của webhook (outgoing và incoming)."""

    platform = models.ForeignKey(
        "platforms.Platform",
        on_delete=models.CASCADE,
        related_name="webhook_logs",
    )
    direction = models.CharField(
        max_length=10,
        choices=WebhookDirection.CHOICES,
        db_index=True,
    )
    event_type = models.CharField(max_length=100, blank=True, default="")
    payload = models.JSONField(default=dict)
    response_status = models.PositiveIntegerField(null=True, blank=True)
    response_body = models.TextField(blank=True, default="")
    # Reference to related schedule (optional)
    schedule_id = models.UUIDField(null=True, blank=True, db_index=True)
    error_message = models.TextField(blank=True, default="")

    class Meta:
        db_table = "platforms_webhook_logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["platform", "created_at"]),
            models.Index(fields=["direction", "created_at"]),
        ]

    def __str__(self):
        return f"{self.direction} [{self.response_status}] {self.platform.name}"
