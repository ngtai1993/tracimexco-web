from django.conf import settings
from django.db import models

from common.models import BaseModel


class PostVersion(BaseModel):
    """Snapshot nội dung bài viết — lưu mỗi lần chỉnh sửa."""

    post = models.ForeignKey(
        "contents.Post",
        on_delete=models.CASCADE,
        related_name="versions",
    )
    version_number = models.PositiveIntegerField()
    title = models.CharField(max_length=500)
    content = models.TextField()
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="post_versions",
    )

    class Meta:
        db_table = "contents_post_versions"
        ordering = ["-version_number"]
        unique_together = [("post", "version_number")]

    def __str__(self):
        return f"{self.post.title} v{self.version_number}"
