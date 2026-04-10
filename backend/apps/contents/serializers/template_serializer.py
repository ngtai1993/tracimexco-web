from rest_framework import serializers

from apps.contents.models import BannerLayout, LayoutTemplate, PostTemplate


class BannerLayoutOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = BannerLayout
        fields = [
            "id", "variant_index", "layout_json",
            "is_approved", "approved_by",
            "created_at", "updated_at",
        ]
        read_only_fields = fields


class BannerLayoutWriteSerializer(serializers.Serializer):
    layout_json = serializers.DictField()


class BannerLayoutGenerateSerializer(serializers.Serializer):
    rag_instance = serializers.UUIDField(required=False, allow_null=True, default=None)
    variants = serializers.IntegerField(min_value=1, max_value=3, default=2)


class LayoutTemplateOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = LayoutTemplate
        fields = ["id", "name", "platform_type", "layout_json", "is_active", "created_at"]
        read_only_fields = fields


class LayoutTemplateWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = LayoutTemplate
        fields = ["name", "platform_type", "layout_json"]


class PostTemplateOutputSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True, default=None)

    class Meta:
        model = PostTemplate
        fields = [
            "id", "name", "platform_type", "content_template",
            "category", "category_name", "is_active", "created_at",
        ]
        read_only_fields = fields


class PostTemplateWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostTemplate
        fields = ["name", "platform_type", "content_template", "category"]
