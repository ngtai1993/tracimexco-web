from django.db import models
from django.utils.text import slugify

from common.models import BaseModel
from apps.platforms.constants import PlatformType, HealthStatus


class Platform(BaseModel):
    """
    Cấu hình nền tảng mạng xã hội.
    webhook_url: endpoint của nền tảng nhận bài viết (outgoing).
    webhook_secret: khóa ký HMAC cho outgoing request.
    """

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    platform_type = models.CharField(
        max_length=20,
        choices=PlatformType.CHOICES,
        db_index=True,
    )
    webhook_url = models.URLField(
        help_text="URL của nền tảng để nhận bài viết khi đến lịch đăng."
    )
    webhook_secret = models.CharField(
        max_length=500,
        blank=True,
        default="",
        help_text="Secret key dùng để ký HMAC outgoing webhook.",
    )
    health_status = models.CharField(
        max_length=20,
        choices=HealthStatus.CHOICES,
        default=HealthStatus.UNKNOWN,
    )
    is_active = models.BooleanField(default=True, db_index=True)
    last_health_check_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "platforms_platforms"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.platform_type})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
