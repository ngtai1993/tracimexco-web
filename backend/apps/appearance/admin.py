from django.contrib import admin
from django.utils.html import format_html
from apps.appearance.models import ColorToken, MediaAsset


@admin.register(ColorToken)
class ColorTokenAdmin(admin.ModelAdmin):
    list_display = ["key", "mode", "color_preview", "value", "name", "group", "order", "is_active", "is_deleted"]
    list_filter = ["mode", "group", "is_active", "is_deleted"]
    search_fields = ["key", "name"]
    list_editable = ["order", "is_active"]
    readonly_fields = ["id", "color_preview", "created_at", "updated_at"]
    ordering = ["mode", "group", "order", "key"]

    @admin.display(description="Preview")
    def color_preview(self, obj):
        if obj.value:
            return format_html(
                '<div style="width:32px;height:20px;background:{};border-radius:3px;'
                'border:1px solid #ccc;display:inline-block"></div>',
                obj.value,
            )
        return "—"


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ["key", "name", "image_preview", "is_active", "is_deleted", "created_at"]
    list_filter = ["is_active", "is_deleted"]
    search_fields = ["key", "name"]
    readonly_fields = ["id", "image_preview", "created_at", "updated_at"]

    @admin.display(description="Preview")
    def image_preview(self, obj):
        if obj.file:
            return format_html(
                '<img src="{}" style="height:40px;border-radius:4px;" />',
                obj.file.url,
            )
        return "—"
