from rest_framework import serializers
from apps.agents.models import AgentConfig


class AgentConfigWriteSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    model_name = serializers.CharField(max_length=100)
    config_json = serializers.JSONField(default=dict)
    is_default = serializers.BooleanField(default=False)
    is_active = serializers.BooleanField(default=True)


class AgentConfigUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, required=False)
    model_name = serializers.CharField(max_length=100, required=False)
    config_json = serializers.JSONField(required=False)
    is_default = serializers.BooleanField(required=False)
    is_active = serializers.BooleanField(required=False)


class AgentConfigOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentConfig
        fields = [
            "id",
            "name",
            "model_name",
            "config_json",
            "is_default",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields
