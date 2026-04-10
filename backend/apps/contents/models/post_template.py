from django.db import models

from common.models import BaseModel
from apps.contents.constants import PlatformType


class PostTemplate(BaseModel):
    """Template tái sử dụng cho bài viết."""

    name = models.CharField(max_length=200)
    platform_type = models.CharField(max_length=20, choices=PlatformType.CHOICES)
    content_template = models.TextField()
    category = models.ForeignKey(
        "contents.Category",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="templates",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "contents_post_templates"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
