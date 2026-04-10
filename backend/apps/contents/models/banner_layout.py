from django.conf import settings
from django.db import models

from common.models import BaseModel


class BannerLayout(BaseModel):
    """
    Bố cục banner được RAG sinh ra — lưu dưới dạng JSON schema.

    layout_json structure example:
    {
        "title": "Tiêu đề banner",
        "tagline": "Slogan ngắn",
        "background": {"type": "color", "value": "#1A2B3C"},
        "title_position": "top-center",
        "font_family": "Montserrat",
        "accent_color": "#FF5733",
        "logo_placement": "top-left",
        "layout_style": "bold"
    }
    """

    post = models.ForeignKey(
        "contents.Post",
        on_delete=models.CASCADE,
        related_name="banner_layouts",
    )
    rag_instance = models.ForeignKey(
        "graph_rag.RAGInstance",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="banner_layouts",
    )
    variant_index = models.PositiveSmallIntegerField(default=1)
    layout_json = models.JSONField(default=dict)
    is_approved = models.BooleanField(default=False, db_index=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_banner_layouts",
    )

    class Meta:
        db_table = "contents_banner_layouts"
        ordering = ["variant_index"]
        unique_together = [("post", "variant_index")]

    def __str__(self):
        return f"Banner for '{self.post.title}' #{self.variant_index}"
