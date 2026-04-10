from rest_framework import serializers
from apps.graph_rag.models import KnowledgeBase, Document, DocumentChunk
from apps.graph_rag.models.knowledge_base import CHUNK_STRATEGY_CHOICES
from apps.graph_rag.constants import (
    SOURCE_TYPE_CHOICES,
    ALLOWED_DOCUMENT_TYPES,
    ALLOWED_IMAGE_TYPES,
)


class KnowledgeBaseWriteSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    slug = serializers.SlugField(max_length=100)
    description = serializers.CharField(required=False, default="", allow_blank=True)
    chunk_strategy = serializers.ChoiceField(
        choices=CHUNK_STRATEGY_CHOICES, default="recursive"
    )
    chunk_size = serializers.IntegerField(default=512, min_value=100, max_value=4096)
    chunk_overlap = serializers.IntegerField(default=50, min_value=0, max_value=500)
    embedding_model = serializers.CharField(
        max_length=100, default="text-embedding-3-small"
    )

    def validate_slug(self, value):
        if KnowledgeBase.objects.filter(slug=value, is_deleted=False).exists():
            raise serializers.ValidationError("Knowledge Base với slug này đã tồn tại.")
        return value


class KnowledgeBaseOutputSerializer(serializers.ModelSerializer):
    graph_status = serializers.SerializerMethodField()

    class Meta:
        model = KnowledgeBase
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "chunk_strategy",
            "chunk_size",
            "chunk_overlap",
            "embedding_model",
            "embedding_dimensions",
            "document_count",
            "image_count",
            "total_chunks",
            "is_active",
            "graph_status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_graph_status(self, obj) -> str | None:
        graph = getattr(obj, "knowledge_graph", None)
        if graph:
            return graph.status
        return None


class DocumentUploadSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=500)
    description = serializers.CharField(required=False, default="", allow_blank=True)
    file = serializers.FileField()


class DocumentTextSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=500)
    description = serializers.CharField(required=False, default="", allow_blank=True)
    content_text = serializers.CharField()


class DocumentURLSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=500)
    description = serializers.CharField(required=False, default="", allow_blank=True)
    source_url = serializers.URLField()


class DocumentOutputSerializer(serializers.ModelSerializer):
    kb_name = serializers.CharField(source="knowledge_base.name", read_only=True)

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "description",
            "source_type",
            "is_image",
            "image_caption",
            "image_tags",
            "processing_status",
            "processing_error",
            "chunk_count",
            "token_count",
            "kb_name",
            "metadata",
            "processed_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class DocumentChunkOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentChunk
        fields = [
            "id",
            "chunk_index",
            "content",
            "token_count",
            "is_image_chunk",
            "metadata",
            "created_at",
        ]
        read_only_fields = fields
