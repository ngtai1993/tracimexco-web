from django.db import models
from django.utils.text import slugify

from common.models import BaseModel


class Category(BaseModel):
    """Danh mục bài viết — hỗ trợ cấu trúc cây (self FK)."""

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children",
    )
    description = models.TextField(blank=True, default="")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "contents_categories"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
