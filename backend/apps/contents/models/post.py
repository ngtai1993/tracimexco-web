from django.conf import settings
from django.db import models

from common.models import BaseModel
from apps.contents.constants import PostStatus, PlatformType


class Post(BaseModel):
    """Bài viết dành cho mạng xã hội."""

    title = models.CharField(max_length=500)
    content = models.TextField()
    hashtags = models.JSONField(default=list, blank=True)
    platform_type = models.CharField(
        max_length=20,
        choices=PlatformType.CHOICES,
        db_index=True,
    )
    status = models.CharField(
        max_length=20,
        choices=PostStatus.CHOICES,
        default=PostStatus.DRAFT,
        db_index=True,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    category = models.ForeignKey(
        "contents.Category",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="posts",
    )
    tags = models.ManyToManyField(
        "contents.Tag",
        blank=True,
        related_name="posts",
    )
    rag_instance = models.ForeignKey(
        "graph_rag.RAGInstance",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="content_posts",
    )
    is_ai_generated = models.BooleanField(default=False, db_index=True)

    class Meta:
        db_table = "contents_posts"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
