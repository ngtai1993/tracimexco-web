import uuid
from django.db import models


class BaseModel(models.Model):
    """Model cơ sở cho tất cả models trong dự án."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, db_index=True)

    class Meta:
        abstract = True

    def soft_delete(self):
        """Đánh dấu record là đã xóa mà không xóa khỏi DB."""
        self.is_deleted = True
        self.save(update_fields=["is_deleted", "updated_at"])

    def restore(self):
        """Khôi phục record đã bị soft delete."""
        self.is_deleted = False
        self.save(update_fields=["is_deleted", "updated_at"])
