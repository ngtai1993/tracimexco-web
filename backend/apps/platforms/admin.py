from django.contrib import admin

from apps.platforms.models import Platform, WebhookEndpoint, WebhookLog


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "platform_type", "health_status", "is_active", "created_at"]
    list_filter = ["platform_type", "health_status", "is_active"]
    search_fields = ["name", "slug"]


@admin.register(WebhookEndpoint)
class WebhookEndpointAdmin(admin.ModelAdmin):
    list_display = ["platform", "endpoint_url", "is_active", "created_at"]
    list_filter = ["is_active"]
    raw_id_fields = ["platform"]


@admin.register(WebhookLog)
class WebhookLogAdmin(admin.ModelAdmin):
    list_display = ["platform", "direction", "event_type", "response_status", "created_at"]
    list_filter = ["direction", "event_type"]
    raw_id_fields = ["platform"]
    readonly_fields = ["platform", "direction", "event_type", "payload", "response_status", "response_body", "schedule_id", "created_at"]
