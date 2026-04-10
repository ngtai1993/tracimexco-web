from django.db import models

from common.models import BaseModel
from apps.scheduling.constants import ScheduleStatus, DEFAULT_TIMEZONE


class PostSchedule(BaseModel):
    """Lịch đăng bài — liên kết Post với Platform tại thời điểm cụ thể."""

    post = models.ForeignKey(
        "contents.Post",
        on_delete=models.CASCADE,
        related_name="schedules",
    )
    platform = models.ForeignKey(
        "platforms.Platform",
        on_delete=models.CASCADE,
        related_name="schedules",
    )
    scheduled_at = models.DateTimeField(db_index=True)
    timezone = models.CharField(max_length=50, default=DEFAULT_TIMEZONE)
    status = models.CharField(
        max_length=20,
        choices=ScheduleStatus.CHOICES,
        default=ScheduleStatus.PENDING,
        db_index=True,
    )

    class Meta:
        db_table = "scheduling_post_schedules"
        ordering = ["scheduled_at"]
        indexes = [
            models.Index(fields=["status", "scheduled_at"]),
        ]

    def __str__(self):
        return f"Schedule {self.post.title} → {self.platform.name} at {self.scheduled_at}"
