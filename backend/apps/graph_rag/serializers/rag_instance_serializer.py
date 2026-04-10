from rest_framework import serializers
from apps.graph_rag.models import RAGInstance
from apps.graph_rag.constants import PURPOSE_CHOICES


class RAGInstanceWriteSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    slug = serializers.SlugField(max_length=100)
    description = serializers.CharField(required=False, default="", allow_blank=True)
    purpose = serializers.ChoiceField(choices=PURPOSE_CHOICES, default="general")
    system_prompt = serializers.CharField()
    provider_id = serializers.UUIDField()
    agent_config_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    retrieval_config = serializers.JSONField(required=False, default=dict)
    generation_config = serializers.JSONField(required=False, default=dict)
    is_public = serializers.BooleanField(default=False)

    def validate_slug(self, value):
        if RAGInstance.objects.filter(slug=value, is_deleted=False).exists():
            raise serializers.ValidationError("RAG instance với slug này đã tồn tại.")
        return value


class RAGInstanceUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    purpose = serializers.ChoiceField(choices=PURPOSE_CHOICES, required=False)
    system_prompt = serializers.CharField(required=False)
    provider_id = serializers.UUIDField(required=False)
    agent_config_id = serializers.UUIDField(required=False, allow_null=True)
    is_active = serializers.BooleanField(required=False)
    is_public = serializers.BooleanField(required=False)


class RAGConfigUpdateSerializer(serializers.Serializer):
    config_type = serializers.ChoiceField(
        choices=["retrieval", "generation", "system_prompt"]
    )
    config = serializers.JSONField()
    reason = serializers.CharField(required=False, default="", allow_blank=True)


class RAGInstanceCloneSerializer(serializers.Serializer):
    new_name = serializers.CharField(max_length=200)
    new_slug = serializers.SlugField(max_length=100)

    def validate_new_slug(self, value):
        if RAGInstance.objects.filter(slug=value, is_deleted=False).exists():
            raise serializers.ValidationError("Slug đã tồn tại.")
        return value


class RAGInstanceKBAssignSerializer(serializers.Serializer):
    knowledge_base_id = serializers.UUIDField()
    priority = serializers.IntegerField(default=1, min_value=1)


class RAGInstanceSkillAssignSerializer(serializers.Serializer):
    skill_id = serializers.UUIDField()
    config_override = serializers.JSONField(required=False, default=dict)


class RAGInstanceOutputSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source="provider.name", read_only=True)
    config_name = serializers.SerializerMethodField()
    kb_count = serializers.SerializerMethodField()
    images_enabled = serializers.BooleanField(read_only=True)
    created_by_email = serializers.SerializerMethodField()

    class Meta:
        model = RAGInstance
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "purpose",
            "system_prompt",
            "provider_name",
            "config_name",
            "retrieval_config",
            "generation_config",
            "is_active",
            "is_public",
            "images_enabled",
            "kb_count",
            "created_by_email",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_config_name(self, obj) -> str | None:
        return obj.agent_config.name if obj.agent_config else None

    def get_kb_count(self, obj) -> int:
        return obj.instance_knowledge_bases.filter(is_deleted=False).count()

    def get_created_by_email(self, obj) -> str | None:
        return obj.created_by.email if obj.created_by else None
