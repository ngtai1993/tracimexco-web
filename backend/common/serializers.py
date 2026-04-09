from rest_framework import serializers


class BaseOutputSerializer(serializers.ModelSerializer):
    """Base serializer dùng cho output — tất cả fields là read-only."""

    def get_fields(self):
        fields = super().get_fields()
        for field in fields.values():
            field.read_only = True
        return fields
