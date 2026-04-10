from django.conf import settings
from django.db import models

from common.models import BaseModel
from apps.contents.constants import GenerationType, GenerationStatus


class AIContentGeneration(BaseModel):
    """Theo dõi quá trình sinh nội dung tự động bằng RAG."""

    post = models.ForeignKey(
        "contents.Post",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="generations",
    )
    rag_instance = models.ForeignKey(
        "graph_rag.RAGInstance",
        on_delete=models.CASCADE,
        related_name="content_generations",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="content_generations",
    )
    generation_type = models.CharField(
        max_length=20,
        choices=GenerationType.CHOICES,
    )
    prompt = models.TextField()
    # Extra context: platform_type, language, max_length, variants count, etc.
    context_data = models.JSONField(default=dict, blank=True)
    result_content = models.TextField(blank=True, default="")
    # List of variant strings for A/B generation
    result_variants = models.JSONField(default=list, blank=True)
    status = models.CharField(
        max_length=20,
        choices=GenerationStatus.CHOICES,
        default=GenerationStatus.PENDING,
        db_index=True,
    )
    error_message = models.TextField(blank=True, default="")

    class Meta:
        db_table = "contents_ai_generations"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.generation_type} [{self.status}] by {self.created_by}"
