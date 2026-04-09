from django.db import models
from common.models import BaseModel


class AgentConfig(BaseModel):
    """Cấu hình model AI (model name, temperature, max_tokens...) per provider."""

    provider = models.ForeignKey(
        "agents.AgentProvider",
        on_delete=models.CASCADE,
        related_name="configs",
    )
    name = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    config_json = models.JSONField(default=dict)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "agent_configs"
        ordering = ["provider", "name"]

    def __str__(self):
        return f"{self.provider.slug} — {self.name}"
