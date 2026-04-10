from django.conf import settings
from django.db import models

from common.models import BaseModel


class PostComment(BaseModel):
    """Comment nội bộ của team trên bài viết."""

    post = models.ForeignKey(
        "contents.Post",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="post_comments",
    )
    content = models.TextField()

    class Meta:
        db_table = "contents_post_comments"
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.author} on {self.post.title}"
