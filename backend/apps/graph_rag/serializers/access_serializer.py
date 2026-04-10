from rest_framework import serializers
from apps.graph_rag.models import RAGAccessPermission
from apps.graph_rag.constants import ACCESS_LEVEL_CHOICES


class GrantAccessSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    access_level = serializers.ChoiceField(choices=ACCESS_LEVEL_CHOICES, default="use")
    daily_query_limit = serializers.IntegerField(default=100, min_value=1)
    monthly_token_limit = serializers.IntegerField(default=1_000_000, min_value=1000)
    expires_at = serializers.DateTimeField(required=False, allow_null=True, default=None)


class AccessPermissionOutputSerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField()
    granted_by_email = serializers.SerializerMethodField()

    class Meta:
        model = RAGAccessPermission
        fields = [
            "id",
            "user_email",
            "access_level",
            "daily_query_limit",
            "monthly_token_limit",
            "expires_at",
            "granted_by_email",
            "created_at",
        ]
        read_only_fields = fields

    def get_user_email(self, obj) -> str:
        return obj.user.email if obj.user else ""

    def get_granted_by_email(self, obj) -> str | None:
        return obj.granted_by.email if obj.granted_by else None
