from django.db import models
from common.models import BaseModel
from apps.graph_rag.constants import ACCESS_LEVEL_CHOICES


class RAGAccessPermission(BaseModel):
    """Quyền sử dụng RAG instance cho 1 user."""

    rag_instance = models.ForeignKey(
        "graph_rag.RAGInstance",
        on_delete=models.CASCADE,
        related_name="access_permissions",
    )
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="rag_permissions"
    )

    access_level = models.CharField(
        max_length=20, choices=ACCESS_LEVEL_CHOICES, default="use"
    )

    daily_query_limit = models.PositiveIntegerField(default=100)
    monthly_token_limit = models.PositiveIntegerField(default=1_000_000)

    granted_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="granted_rag_permissions",
    )
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "rag_access_permissions"
        unique_together = ["rag_instance", "user"]

    def __str__(self):
        return f"{self.user} → {self.rag_instance.slug} ({self.access_level})"
