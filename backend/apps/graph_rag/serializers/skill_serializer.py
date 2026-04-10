from rest_framework import serializers
from apps.graph_rag.models import RAGSkill


class RAGSkillWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = RAGSkill
        fields = [
            "name",
            "slug",
            "description",
            "skill_type",
            "config",
            "input_schema",
            "output_schema",
            "implementation_path",
            "api_endpoint",
            "api_method",
            "api_headers",
            "is_active",
        ]

    def validate_slug(self, value):
        qs = RAGSkill.objects.filter(slug=value, is_deleted=False)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Slug này đã được sử dụng.")
        return value


class RAGSkillOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = RAGSkill
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "skill_type",
            "config",
            "input_schema",
            "output_schema",
            "implementation_path",
            "api_endpoint",
            "api_method",
            "is_active",
            "created_at",
        ]
        read_only_fields = fields
