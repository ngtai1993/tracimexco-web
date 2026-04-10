from django.db import models
from django.utils.text import slugify

from common.models import BaseModel


class Tag(BaseModel):
    """Tag phẳng — dùng để gắn nhãn bài viết."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        db_table = "contents_tags"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
