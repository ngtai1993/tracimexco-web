import logging

from apps.graph_rag.models import RAGConversation, RAGMessage
from apps.graph_rag.exceptions import RAGConversationNotFound

logger = logging.getLogger(__name__)


class ConversationService:
    """Chat history management."""

    @staticmethod
    def get_conversation_messages(conversation_id: str, user_id: str) -> list[dict]:
        """Lấy tất cả messages của conversation."""
        try:
            conv = RAGConversation.objects.get(
                id=conversation_id, user_id=user_id, is_deleted=False
            )
        except RAGConversation.DoesNotExist:
            raise RAGConversationNotFound("Conversation không tồn tại")

        messages = RAGMessage.objects.filter(
            conversation=conv, is_deleted=False
        ).order_by("created_at")

        return [
            {
                "id": str(m.id),
                "role": m.role,
                "content": m.content,
                "sources": m.sources,
                "images": m.images,
                "skills_used": m.skills_used,
                "metadata": m.metadata,
                "feedback": m.feedback,
                "created_at": m.created_at.isoformat(),
            }
            for m in messages
        ]

    @staticmethod
    def update_feedback(message_id: str, feedback: str, comment: str = "") -> None:
        """Cập nhật feedback cho message."""
        RAGMessage.objects.filter(id=message_id, is_deleted=False).update(
            feedback=feedback,
            feedback_comment=comment,
        )

    @staticmethod
    def soft_delete_conversation(conversation_id: str, user_id: str) -> None:
        try:
            conv = RAGConversation.objects.get(
                id=conversation_id, user_id=user_id, is_deleted=False
            )
        except RAGConversation.DoesNotExist:
            raise RAGConversationNotFound("Conversation không tồn tại")
        conv.soft_delete()
