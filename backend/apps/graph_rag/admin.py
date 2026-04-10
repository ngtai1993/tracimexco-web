from django.contrib import admin
from apps.graph_rag.models import (
    RAGInstance,
    RAGInstanceKnowledgeBase,
    KnowledgeBase,
    Document,
    DocumentChunk,
    KnowledgeGraph,
    GraphEntity,
    GraphRelationship,
    GraphCommunity,
    RAGSkill,
    RAGInstanceSkill,
    RAGConversation,
    RAGMessage,
    RAGAccessPermission,
    RAGUsageLog,
    RAGConfigHistory,
)


class RAGInstanceKBInline(admin.TabularInline):
    model = RAGInstanceKnowledgeBase
    extra = 0


class RAGInstanceSkillInline(admin.TabularInline):
    model = RAGInstanceSkill
    extra = 0


@admin.register(RAGInstance)
class RAGInstanceAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "purpose", "is_active", "is_public", "created_at"]
    list_filter = ["purpose", "is_active", "is_public"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    inlines = [RAGInstanceKBInline, RAGInstanceSkillInline]


@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = [
        "name", "slug", "document_count", "image_count", "total_chunks", "is_active",
    ]
    list_filter = ["is_active", "chunk_strategy"]
    search_fields = ["name", "slug"]


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = [
        "title", "knowledge_base", "source_type", "is_image",
        "processing_status", "chunk_count", "created_at",
    ]
    list_filter = ["source_type", "is_image", "processing_status"]
    search_fields = ["title"]


@admin.register(KnowledgeGraph)
class KnowledgeGraphAdmin(admin.ModelAdmin):
    list_display = [
        "knowledge_base", "status", "entity_count", "relationship_count",
        "community_count", "last_built_at",
    ]
    list_filter = ["status"]


@admin.register(RAGSkill)
class RAGSkillAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "skill_type", "is_active"]
    list_filter = ["skill_type", "is_active"]


@admin.register(RAGConversation)
class RAGConversationAdmin(admin.ModelAdmin):
    list_display = ["title", "rag_instance", "user", "message_count", "created_at"]
    list_filter = ["rag_instance"]
    search_fields = ["title"]


@admin.register(RAGAccessPermission)
class RAGAccessPermissionAdmin(admin.ModelAdmin):
    list_display = [
        "rag_instance", "user", "access_level", "daily_query_limit",
        "monthly_token_limit", "expires_at",
    ]
    list_filter = ["access_level"]


@admin.register(RAGUsageLog)
class RAGUsageLogAdmin(admin.ModelAdmin):
    list_display = [
        "rag_instance", "user", "retrieval_strategy", "latency_ms",
        "images_returned", "created_at",
    ]
    list_filter = ["retrieval_strategy"]
    date_hierarchy = "created_at"


@admin.register(RAGConfigHistory)
class RAGConfigHistoryAdmin(admin.ModelAdmin):
    list_display = ["rag_instance", "config_type", "changed_by", "reason", "created_at"]
    list_filter = ["config_type"]


# Register remaining models with default admin
admin.site.register(DocumentChunk)
admin.site.register(GraphEntity)
admin.site.register(GraphRelationship)
admin.site.register(GraphCommunity)
admin.site.register(RAGMessage)
