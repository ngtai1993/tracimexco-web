from rest_framework import serializers
from apps.agents.models import AgentAPIKey


class AgentAPIKeyWriteSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    raw_key = serializers.CharField(write_only=True, trim_whitespace=False)
    priority = serializers.IntegerField(default=1, min_value=1)
    expires_at = serializers.DateTimeField(required=False, allow_null=True, default=None)


class AgentAPIKeyUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, required=False)
    priority = serializers.IntegerField(min_value=1, required=False)
    is_active = serializers.BooleanField(required=False)
    expires_at = serializers.DateTimeField(required=False, allow_null=True)


class AgentAPIKeyOutputSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = AgentAPIKey
        fields = [
            "id",
            "name",
            "key_preview",
            "is_active",
            "priority",
            "last_used_at",
            "expires_at",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_created_by(self, obj) -> str | None:
        if obj.created_by:
            return obj.created_by.email
        return None
