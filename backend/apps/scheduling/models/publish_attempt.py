from django.db import models

from common.models import BaseModel
from apps.scheduling.constants import AttemptStatus


class PublishAttempt(BaseModel):
    """Ghi nhận mỗi lần thử đăng bài (bao gồm cả retry)."""

    schedule = models.ForeignKey(
        "scheduling.PostSchedule",
        on_delete=models.CASCADE,
        related_name="attempts",
    )
    attempt_number = models.PositiveIntegerField(default=1)
    attempted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=AttemptStatus.CHOICES,
        db_index=True,
    )
    error_message = models.TextField(blank=True, default="")
    response_data = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "scheduling_publish_attempts"
        ordering = ["-attempted_at"]

    def __str__(self):
        return f"Attempt #{self.attempt_number} [{self.status}] for {self.schedule}"
