from rest_framework import serializers
from apps.graph_rag.models import RAGConversation, RAGMessage


class QuerySerializer(serializers.Serializer):
    query = serializers.CharField(max_length=4000)
    conversation_id = serializers.UUIDField(required=False, allow_null=True, default=None)


class MessageOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = RAGMessage
        fields = [
            "id",
            "role",
            "content",
            "sources",
            "images",
            "skills_used",
            "metadata",
            "feedback",
            "feedback_comment",
            "created_at",
        ]
        read_only_fields = fields


class ConversationOutputSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = RAGConversation
        fields = [
            "id",
            "title",
            "message_count",
            "last_message",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_last_message(self, obj) -> str | None:
        msg = obj.messages.filter(is_deleted=False).order_by("-created_at").first()
        if msg:
            return msg.content[:200]
        return None


class FeedbackSerializer(serializers.Serializer):
    feedback = serializers.ChoiceField(choices=["positive", "negative"])
    comment = serializers.CharField(required=False, default="", allow_blank=True)
