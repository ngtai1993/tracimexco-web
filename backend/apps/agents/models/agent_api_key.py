from django.db import models
from django.conf import settings
from common.models import BaseModel


class AgentAPIKey(BaseModel):
    """API Key của provider, được mã hóa bằng Fernet trước khi lưu DB."""

    provider = models.ForeignKey(
        "agents.AgentProvider",
        on_delete=models.CASCADE,
        related_name="keys",
    )
    name = models.CharField(max_length=100)
    encrypted_key = models.TextField()
    key_preview = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    priority = models.PositiveIntegerField(default=1)
    last_used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_agent_keys",
    )

    class Meta:
        db_table = "agent_api_keys"
        ordering = ["provider", "priority"]

    def __str__(self):
        return f"{self.provider.slug} — {self.name}"
