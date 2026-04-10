from rest_framework import serializers

from apps.platforms.models import Platform, WebhookEndpoint, WebhookLog
from apps.platforms.constants import PlatformType, HealthStatus


class PlatformWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = ["name", "slug", "platform_type", "webhook_url", "webhook_secret"]

    def validate_platform_type(self, value):
        valid = [c[0] for c in PlatformType.CHOICES]
        if value not in valid:
            raise serializers.ValidationError(f"platform_type phải là: {', '.join(valid)}")
        return value


class PlatformOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = [
            "id", "name", "slug", "platform_type",
            "webhook_url", "health_status",
            "is_active", "last_health_check_at",
            "created_at", "updated_at",
        ]
        read_only_fields = fields


class WebhookEndpointWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookEndpoint
        fields = ["endpoint_url", "event_types", "secret_key"]


class WebhookEndpointOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookEndpoint
        fields = [
            "id", "endpoint_url", "event_types",
            "is_active", "created_at",
        ]
        read_only_fields = fields


class WebhookLogOutputSerializer(serializers.ModelSerializer):
    platform_name = serializers.CharField(source="platform.name", read_only=True)

    class Meta:
        model = WebhookLog
        fields = [
            "id", "platform_name", "direction", "event_type",
            "response_status", "response_body",
            "schedule_id", "error_message", "created_at",
        ]
        read_only_fields = fields
