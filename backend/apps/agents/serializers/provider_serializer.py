from rest_framework import serializers
from apps.agents.models import AgentProvider


class AgentProviderWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentProvider
        fields = ["name", "slug", "description", "website_url", "is_active"]

    def validate_slug(self, value):
        qs = AgentProvider.objects.filter(slug=value, is_deleted=False)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Provider với slug này đã tồn tại.")
        return value


class AgentProviderOutputSerializer(serializers.ModelSerializer):
    keys_count = serializers.SerializerMethodField()
    active_keys_count = serializers.SerializerMethodField()

    class Meta:
        model = AgentProvider
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "website_url",
            "is_active",
            "keys_count",
            "active_keys_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_keys_count(self, obj) -> int:
        return obj.keys.filter(is_deleted=False).count()

    def get_active_keys_count(self, obj) -> int:
        return obj.keys.filter(is_active=True, is_deleted=False).count()
