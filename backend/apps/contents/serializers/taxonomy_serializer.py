from rest_framework import serializers

from apps.contents.models import Category, Tag
from apps.contents.exceptions import CircularCategoryError


class CategoryWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["name", "slug", "parent", "description", "order"]
        extra_kwargs = {
            "slug": {"required": False, "allow_blank": True},
        }

    def validate(self, attrs):
        parent = attrs.get("parent", getattr(self.instance, "parent", None))
        instance = self.instance
        if instance and parent:
            # Prevent circular reference
            node = parent
            while node:
                if node.id == instance.id:
                    raise serializers.ValidationError(
                        {"parent": "Tạo vòng lặp cha-con không hợp lệ."}
                    )
                node = node.parent
        return attrs


class CategoryChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "order"]
        read_only_fields = fields


class CategoryOutputSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "parent", "description", "order", "children", "created_at"]
        read_only_fields = fields

    def get_children(self, obj):
        active_children = obj.children.filter(is_deleted=False).order_by("order", "name")
        return CategoryChildSerializer(active_children, many=True).data


class TagWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["name"]

    def validate_name(self, value: str) -> str:
        qs = Tag.objects.filter(name__iexact=value, is_deleted=False)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Tag với tên này đã tồn tại.")
        return value


class TagOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "slug", "created_at"]
        read_only_fields = fields
