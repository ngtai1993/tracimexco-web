from django.db import models
from common.models import BaseModel
from apps.graph_rag.constants import PURPOSE_CHOICES, DEFAULT_RETRIEVAL_CONFIG, DEFAULT_GENERATION_CONFIG


class RAGInstance(BaseModel):
    """Một 'con RAG' riêng biệt, phục vụ một mục đích cụ thể."""

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, default="")
    purpose = models.CharField(max_length=50, choices=PURPOSE_CHOICES, default="general")

    system_prompt = models.TextField(
        help_text="Template system prompt. Variables: {context}, {sources}, {language}"
    )

    # AI Provider & Model (từ app agents)
    provider = models.ForeignKey(
        "agents.AgentProvider",
        on_delete=models.PROTECT,
        related_name="rag_instances",
    )
    agent_config = models.ForeignKey(
        "agents.AgentConfig",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rag_instances",
    )

    # Configurable parameters (JSON, tất cả tuning qua API)
    retrieval_config = models.JSONField(default=dict)
    generation_config = models.JSONField(default=dict)

    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(
        default=False,
        help_text="Tất cả authenticated users đều dùng được",
    )

    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_rag_instances",
    )

    class Meta:
        db_table = "rag_instances"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def images_enabled(self) -> bool:
        """Kiểm tra nhanh xem instance có bật image support không."""
        return self.retrieval_config.get("images_enabled", False)

    def save(self, *args, **kwargs):
        if not self.retrieval_config:
            self.retrieval_config = DEFAULT_RETRIEVAL_CONFIG.copy()
        if not self.generation_config:
            self.generation_config = DEFAULT_GENERATION_CONFIG.copy()
        super().save(*args, **kwargs)


class RAGInstanceKnowledgeBase(BaseModel):
    """Gán Knowledge Base cho RAG Instance với priority."""

    rag_instance = models.ForeignKey(
        RAGInstance,
        on_delete=models.CASCADE,
        related_name="instance_knowledge_bases",
    )
    knowledge_base = models.ForeignKey(
        "graph_rag.KnowledgeBase",
        on_delete=models.CASCADE,
        related_name="instance_assignments",
    )
    priority = models.PositiveIntegerField(default=1, help_text="1 = cao nhất")

    class Meta:
        db_table = "rag_instance_knowledge_bases"
        unique_together = ["rag_instance", "knowledge_base"]
        ordering = ["priority"]

    def __str__(self):
        return f"{self.rag_instance.slug} ← {self.knowledge_base.slug} (p={self.priority})"
