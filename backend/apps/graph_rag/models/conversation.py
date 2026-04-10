from django.db import models
from common.models import BaseModel
from apps.graph_rag.constants import MESSAGE_ROLE_CHOICES, FEEDBACK_CHOICES


class RAGConversation(BaseModel):
    """Một phiên chat với RAG instance."""

    rag_instance = models.ForeignKey(
        "graph_rag.RAGInstance",
        on_delete=models.CASCADE,
        related_name="conversations",
    )
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="rag_conversations"
    )
    title = models.CharField(max_length=500, blank=True, default="")
    is_active = models.BooleanField(default=True)
    message_count = models.PositiveIntegerField(default=0)
    metadata = models.JSONField(default=dict)

    class Meta:
        db_table = "rag_conversations"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.user} — {self.rag_instance.slug}: {self.title or 'Untitled'}"


class RAGMessage(BaseModel):
    """Một tin nhắn trong conversation."""

    conversation = models.ForeignKey(
        RAGConversation, on_delete=models.CASCADE, related_name="messages"
    )

    role = models.CharField(max_length=20, choices=MESSAGE_ROLE_CHOICES)
    content = models.TextField()

    # Sources & images used
    sources = models.JSONField(
        default=list,
        help_text="Chunks, entities, communities referenced",
    )
    images = models.JSONField(
        default=list,
        help_text="Images returned: [{id, url, caption, score}]",
    )

    # Skills used
    skills_used = models.JSONField(default=list)

    # Metadata
    metadata = models.JSONField(
        default=dict,
        help_text="tokens_in, tokens_out, latency_ms, retrieval_strategy, model, etc.",
    )

    # Feedback
    feedback = models.CharField(
        max_length=20, choices=FEEDBACK_CHOICES, null=True, blank=True
    )
    feedback_comment = models.TextField(blank=True, default="")

    class Meta:
        db_table = "rag_messages"
        ordering = ["created_at"]

    def __str__(self):
        return f"[{self.role}] {self.content[:80]}"
