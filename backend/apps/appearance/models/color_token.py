import re
from django.db import models
from common.models import BaseModel
from apps.appearance.constants import ColorMode, ColorGroup


class ColorToken(BaseModel):
    """Design token màu sắc — lưu giá trị hex cho từng mode (light/dark)."""

    name = models.CharField(max_length=100)
    key = models.SlugField(max_length=100)
    mode = models.CharField(max_length=10, choices=ColorMode.CHOICES, default=ColorMode.LIGHT)
    value = models.CharField(max_length=20)
    group = models.CharField(max_length=50, choices=ColorGroup.CHOICES, default=ColorGroup.BRAND)
    description = models.TextField(blank=True, default="")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "appearance_color_tokens"
        unique_together = [("key", "mode")]
        ordering = ["group", "order", "key"]

    def __str__(self):
        return f"{self.key} ({self.mode}): {self.value}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.value and not re.match(r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$", self.value):
            raise ValidationError({"value": "Giá trị màu phải là hex hợp lệ (vd: #0e4475 hoặc #fff)."})
