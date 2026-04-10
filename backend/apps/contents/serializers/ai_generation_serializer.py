from rest_framework import serializers

from apps.contents.models import AIContentGeneration
from apps.contents.constants import GenerationType, GenerationStatus, ImprovementType


class AIGenerationOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIContentGeneration
        fields = [
            "id", "generation_type", "status", "prompt",
            "result_content", "result_variants",
            "error_message", "created_at", "updated_at",
        ]
        read_only_fields = fields


class AIGenerateWriteSerializer(serializers.Serializer):
    rag_instance = serializers.UUIDField()
    prompt = serializers.CharField(min_length=5)
    platform_type = serializers.CharField(required=False, default="")
    variants = serializers.IntegerField(min_value=1, max_value=3, default=1)
    language = serializers.CharField(default="vi")
    post_id = serializers.UUIDField(required=False, allow_null=True, default=None)


class AISuggestHashtagsSerializer(serializers.Serializer):
    content = serializers.CharField(min_length=10)
    platform_type = serializers.CharField(required=False, default="")
    count = serializers.IntegerField(min_value=1, max_value=30, default=10)


class AISummarizeSerializer(serializers.Serializer):
    content = serializers.CharField(min_length=20)
    platform_type = serializers.CharField(required=False, default="")
    max_length = serializers.IntegerField(min_value=50, max_value=2000, default=280)


class AITranslateSerializer(serializers.Serializer):
    content = serializers.CharField(min_length=5)
    target_language = serializers.CharField(max_length=10)


class AIImproveSerializer(serializers.Serializer):
    content = serializers.CharField(min_length=10)
    improvement_type = serializers.ChoiceField(
        choices=[c[0] for c in ImprovementType.CHOICES]
    )


class AIGenerateCaptionSerializer(serializers.Serializer):
    media_id = serializers.UUIDField()
    rag_instance = serializers.UUIDField(required=False, allow_null=True, default=None)
