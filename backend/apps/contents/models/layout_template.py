from django.db import models

from common.models import BaseModel
from apps.contents.constants import PlatformType


class LayoutTemplate(BaseModel):
    """Template bố cục banner đã được duyệt — tái sử dụng nhiều lần."""

    name = models.CharField(max_length=200)
    platform_type = models.CharField(
        max_length=20,
        choices=PlatformType.CHOICES,
        blank=True,
        default="",
    )
    layout_json = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "contents_layout_templates"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
