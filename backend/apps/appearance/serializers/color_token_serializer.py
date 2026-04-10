import re
from rest_framework import serializers
from apps.appearance.models import ColorToken
from apps.appearance.constants import ColorMode, ColorGroup


class ColorTokenWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColorToken
        fields = ["name", "key", "mode", "value", "group", "description", "order", "is_active"]

    def validate_value(self, value: str) -> str:
        if not re.match(r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$", value):
            raise serializers.ValidationError(
                "Giá trị màu phải là hex hợp lệ (vd: #0e4475 hoặc #fff)."
            )
        return value

    def validate_mode(self, value: str) -> str:
        valid = [choice[0] for choice in ColorMode.CHOICES]
        if value not in valid:
            raise serializers.ValidationError(f"mode phải là một trong: {', '.join(valid)}.")
        return value

    def validate_group(self, value: str) -> str:
        valid = [choice[0] for choice in ColorGroup.CHOICES]
        if value not in valid:
            raise serializers.ValidationError(f"group phải là một trong: {', '.join(valid)}.")
        return value

    def validate(self, attrs):
        key = attrs.get("key", getattr(self.instance, "key", None))
        mode = attrs.get("mode", getattr(self.instance, "mode", None))
        qs = ColorToken.objects.filter(key=key, mode=mode, is_deleted=False)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                {"key": f"Token với key='{key}' và mode='{mode}' đã tồn tại."}
            )
        return attrs


class ColorTokenOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColorToken
        fields = [
            "id", "name", "key", "mode", "value", "group",
            "description", "order", "is_active", "created_at", "updated_at",
        ]
        read_only_fields = fields
