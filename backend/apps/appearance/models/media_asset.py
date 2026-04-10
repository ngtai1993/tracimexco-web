from django.db import models
from common.models import BaseModel


class MediaAsset(BaseModel):
    """File media được đặt key cố định — logo, favicon, banner, v.v."""

    name = models.CharField(max_length=100)
    key = models.SlugField(max_length=100, unique=True)
    file = models.ImageField(upload_to="appearance/media/%Y/%m/", null=True, blank=True)
    alt_text = models.CharField(max_length=200, blank=True, default="")
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "appearance_media_assets"
        ordering = ["key"]

    def __str__(self):
        return f"{self.key}: {self.name}"
