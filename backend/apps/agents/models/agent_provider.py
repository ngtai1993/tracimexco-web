from django.db import models
from common.models import BaseModel


class AgentProvider(BaseModel):
    """Nhà cung cấp AI bên ngoài (OpenAI, Anthropic, Google Gemini, ...)."""

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, default="")
    website_url = models.URLField(blank=True, default="")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "agent_providers"
        ordering = ["name"]

    def __str__(self):
        return self.name
