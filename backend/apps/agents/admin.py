from django.contrib import admin
from apps.agents.models import AgentProvider, AgentAPIKey, AgentConfig


@admin.register(AgentProvider)
class AgentProviderAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "is_active", "is_deleted", "created_at"]
    list_filter = ["is_active", "is_deleted"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(AgentAPIKey)
class AgentAPIKeyAdmin(admin.ModelAdmin):
    list_display = ["name", "provider", "key_preview", "is_active", "priority", "last_used_at", "expires_at"]
    list_filter = ["provider", "is_active", "is_deleted"]
    search_fields = ["name", "provider__slug"]
    readonly_fields = ["id", "encrypted_key", "key_preview", "last_used_at", "created_at", "updated_at"]
    exclude = ["encrypted_key"]

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        # Không hiển thị encrypted_key trong form
        return [f for f in fields if f != "encrypted_key"]


@admin.register(AgentConfig)
class AgentConfigAdmin(admin.ModelAdmin):
    list_display = ["name", "provider", "model_name", "is_default", "is_active"]
    list_filter = ["provider", "is_default", "is_active", "is_deleted"]
    search_fields = ["name", "model_name", "provider__slug"]
    readonly_fields = ["id", "created_at", "updated_at"]
