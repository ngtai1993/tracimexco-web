from rest_framework import serializers

from apps.contents.models import Post, PostMedia, PostVersion, PostComment
from apps.contents.constants import PostStatus, PlatformType


class PostMediaOutputSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = PostMedia
        fields = ["id", "media_type", "file", "file_url", "caption", "order", "created_at"]
        read_only_fields = fields

    def get_file_url(self, obj):
        request = self.context.get("request")
        if request and obj.file:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url if obj.file else None


class PostVersionOutputSerializer(serializers.ModelSerializer):
    changed_by_name = serializers.CharField(source="changed_by.get_full_name", read_only=True)

    class Meta:
        model = PostVersion
        fields = ["id", "version_number", "title", "content", "changed_by_name", "created_at"]
        read_only_fields = fields


class PostCommentOutputSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.get_full_name", read_only=True)

    class Meta:
        model = PostComment
        fields = ["id", "author_name", "content", "created_at"]
        read_only_fields = fields


class PostListSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.get_full_name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True, default=None)
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id", "title", "status", "platform_type",
            "author_name", "category_name", "tags",
            "is_ai_generated", "created_at", "updated_at",
        ]
        read_only_fields = fields

    def get_tags(self, obj):
        return [{"id": str(t.id), "name": t.name} for t in obj.tags.all()]


class PostDetailSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.get_full_name", read_only=True)
    category = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    media = PostMediaOutputSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            "id", "title", "content", "hashtags", "platform_type", "status",
            "author_name", "category", "tags", "media",
            "is_ai_generated", "created_at", "updated_at",
        ]
        read_only_fields = fields

    def get_category(self, obj):
        if obj.category:
            return {"id": str(obj.category.id), "name": obj.category.name, "slug": obj.category.slug}
        return None

    def get_tags(self, obj):
        return [{"id": str(t.id), "name": t.name, "slug": t.slug} for t in obj.tags.all()]


class PostWriteSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(
        child=serializers.UUIDField(), required=False, default=list
    )

    class Meta:
        model = Post
        fields = [
            "title", "content", "hashtags", "platform_type",
            "category", "tags", "rag_instance", "is_ai_generated",
        ]

    def validate_platform_type(self, value: str) -> str:
        valid = [c[0] for c in PlatformType.CHOICES]
        if value not in valid:
            raise serializers.ValidationError(f"platform_type phải là: {', '.join(valid)}")
        return value


class PostMediaWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMedia
        fields = ["media_type", "file", "caption", "order"]


class PostCommentWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostComment
        fields = ["content"]
