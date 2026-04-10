from rest_framework import serializers
from apps.graph_rag.models import RAGUsageLog, RAGConfigHistory


class UsageLogOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = RAGUsageLog
        fields = [
            "id",
            "query",
            "retrieval_strategy",
            "tokens_in",
            "tokens_out",
            "latency_ms",
            "sources_count",
            "images_returned",
            "created_at",
        ]
        read_only_fields = fields


class ConfigHistoryOutputSerializer(serializers.ModelSerializer):
    changed_by_email = serializers.SerializerMethodField()

    class Meta:
        model = RAGConfigHistory
        fields = [
            "id",
            "config_type",
            "old_value",
            "new_value",
            "reason",
            "changed_by_email",
            "created_at",
        ]
        read_only_fields = fields

    def get_changed_by_email(self, obj) -> str | None:
        return obj.changed_by.email if obj.changed_by else None
