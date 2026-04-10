from django.db import models
from common.models import BaseModel
from apps.graph_rag.constants import CONFIG_TYPE_CHOICES


class RAGUsageLog(BaseModel):
    """Log mỗi query cho tracking và analytics."""

    rag_instance = models.ForeignKey(
        "graph_rag.RAGInstance",
        on_delete=models.CASCADE,
        related_name="usage_logs",
    )
    user = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, null=True, related_name="+"
    )
    conversation = models.ForeignKey(
        "graph_rag.RAGConversation",
        on_delete=models.SET_NULL,
        null=True,
        related_name="+",
    )

    query = models.TextField()
    retrieval_strategy = models.CharField(max_length=20, default="hybrid")
    tokens_in = models.PositiveIntegerField(default=0)
    tokens_out = models.PositiveIntegerField(default=0)
    latency_ms = models.PositiveIntegerField(default=0)

    sources_count = models.PositiveIntegerField(default=0)
    images_returned = models.PositiveIntegerField(default=0)
    skills_used = models.JSONField(default=list)
    feedback = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        db_table = "rag_usage_logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["rag_instance", "created_at"]),
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self):
        return f"Query: {self.query[:60]}"


class RAGConfigHistory(BaseModel):
    """Log mỗi lần thay đổi config của RAG instance."""

    rag_instance = models.ForeignKey(
        "graph_rag.RAGInstance",
        on_delete=models.CASCADE,
        related_name="config_history",
    )

    config_type = models.CharField(max_length=20, choices=CONFIG_TYPE_CHOICES)
    old_value = models.JSONField()
    new_value = models.JSONField()
    changed_by = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, null=True, related_name="+"
    )
    reason = models.TextField(blank=True, default="")

    class Meta:
        db_table = "rag_config_history"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.rag_instance.slug} — {self.config_type} changed"
