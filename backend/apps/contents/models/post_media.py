from django.db import models

from common.models import BaseModel
from apps.contents.constants import MediaType


class PostMedia(BaseModel):
    """File media (ảnh, video) gắn với bài viết."""

    post = models.ForeignKey(
        "contents.Post",
        on_delete=models.CASCADE,
        related_name="media",
    )
    media_type = models.CharField(
        max_length=10,
        choices=MediaType.CHOICES,
        default=MediaType.IMAGE,
    )
    file = models.FileField(upload_to="contents/media/%Y/%m/")
    caption = models.CharField(max_length=500, blank=True, default="")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "contents_post_media"
        ordering = ["order", "created_at"]

    def __str__(self):
        return f"{self.post.title} — {self.media_type} #{self.order}"
