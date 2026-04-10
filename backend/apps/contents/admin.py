from django.contrib import admin

from apps.contents.models import (
    Category,
    Tag,
    Post,
    PostMedia,
    PostVersion,
    PostTemplate,
    PostComment,
    AIContentGeneration,
    BannerLayout,
    LayoutTemplate,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "parent", "order", "created_at"]
    search_fields = ["name", "slug"]
    list_filter = ["is_deleted"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "created_at"]
    search_fields = ["name"]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["title", "status", "platform_type", "author", "is_ai_generated", "created_at"]
    list_filter = ["status", "platform_type", "is_ai_generated", "is_deleted"]
    search_fields = ["title", "content"]
    raw_id_fields = ["author", "category", "rag_instance"]


@admin.register(PostMedia)
class PostMediaAdmin(admin.ModelAdmin):
    list_display = ["post", "media_type", "order", "created_at"]
    list_filter = ["media_type"]


@admin.register(PostVersion)
class PostVersionAdmin(admin.ModelAdmin):
    list_display = ["post", "version_number", "changed_by", "created_at"]
    raw_id_fields = ["post", "changed_by"]


@admin.register(PostTemplate)
class PostTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "platform_type", "is_active", "created_at"]
    list_filter = ["platform_type", "is_active"]


@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):
    list_display = ["post", "author", "created_at"]
    raw_id_fields = ["post", "author"]


@admin.register(AIContentGeneration)
class AIContentGenerationAdmin(admin.ModelAdmin):
    list_display = ["generation_type", "status", "created_by", "created_at"]
    list_filter = ["generation_type", "status"]
    raw_id_fields = ["post", "rag_instance", "created_by"]


@admin.register(BannerLayout)
class BannerLayoutAdmin(admin.ModelAdmin):
    list_display = ["post", "variant_index", "is_approved", "created_at"]
    list_filter = ["is_approved"]
    raw_id_fields = ["post", "rag_instance", "approved_by"]


@admin.register(LayoutTemplate)
class LayoutTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "platform_type", "is_active", "created_at"]
    list_filter = ["platform_type", "is_active"]
