from rest_framework import serializers
from apps.graph_rag.models import RAGSkill


class RAGSkillOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = RAGSkill
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "skill_type",
            "default_config",
            "is_active",
            "created_at",
        ]
        read_only_fields = fields
