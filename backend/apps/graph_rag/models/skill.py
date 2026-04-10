from django.db import models
from common.models import BaseModel
from apps.graph_rag.constants import SKILL_TYPE_CHOICES


class RAGSkill(BaseModel):
    """Một skill/tool mà RAG instance có thể sử dụng."""

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(
        help_text="Mô tả cho LLM biết khi nào dùng skill này"
    )

    skill_type = models.CharField(max_length=20, choices=SKILL_TYPE_CHOICES)

    config = models.JSONField(default=dict, help_text="Skill-specific config")
    input_schema = models.JSONField(default=dict, help_text="JSON Schema for input")
    output_schema = models.JSONField(default=dict, help_text="JSON Schema for output")

    implementation_path = models.CharField(
        max_length=500,
        blank=True,
        default="",
        help_text="Python path, e.g., 'apps.graph_rag.skills.web_search.WebSearchSkill'",
    )
    api_endpoint = models.URLField(blank=True, default="")
    api_method = models.CharField(max_length=10, default="POST")
    api_headers = models.JSONField(default=dict, blank=True)

    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, null=True, related_name="+"
    )

    class Meta:
        db_table = "rag_skills"
        ordering = ["name"]

    def __str__(self):
        return self.name


class RAGInstanceSkill(BaseModel):
    """Gán skill cho RAG instance với config override."""

    rag_instance = models.ForeignKey(
        "graph_rag.RAGInstance",
        on_delete=models.CASCADE,
        related_name="instance_skills",
    )
    skill = models.ForeignKey(RAGSkill, on_delete=models.CASCADE, related_name="instance_assignments")
    is_enabled = models.BooleanField(default=True)
    config_override = models.JSONField(
        default=dict, help_text="Override skill config per instance"
    )

    class Meta:
        db_table = "rag_instance_skills"
        unique_together = ["rag_instance", "skill"]

    def __str__(self):
        return f"{self.rag_instance.slug} ← {self.skill.slug}"
