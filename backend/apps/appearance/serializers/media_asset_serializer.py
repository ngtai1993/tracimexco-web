from django.conf import settings
from rest_framework import serializers
from apps.appearance.models import MediaAsset


class MediaAssetWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaAsset
        fields = ["name", "key", "file", "alt_text", "description", "is_active"]

    def validate_key(self, value: str) -> str:
        qs = MediaAsset.objects.filter(key=value, is_deleted=False)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(f"Asset với key='{value}' đã tồn tại.")
        return value

    def validate_file(self, file):
        max_size = getattr(settings, "APPEARANCE_MAX_FILE_SIZE", 5 * 1024 * 1024)
        if file and file.size > max_size:
            mb = max_size // (1024 * 1024)
            raise serializers.ValidationError(f"Kích thước file tối đa là {mb}MB.")
        return file


class MediaAssetOutputSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = MediaAsset
        fields = [
            "id", "name", "key", "file_url", "alt_text",
            "description", "is_active", "created_at", "updated_at",
        ]
        read_only_fields = fields

    def get_file_url(self, obj) -> str | None:
        if not obj.file:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url
