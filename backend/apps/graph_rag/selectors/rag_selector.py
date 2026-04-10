from django.db.models import Q, Count
from django.utils import timezone

from apps.graph_rag.models import (
    RAGInstance,
    RAGInstanceKnowledgeBase,
    KnowledgeBase,
    Document,
    DocumentChunk,
    KnowledgeGraph,
    RAGSkill,
    RAGInstanceSkill,
    RAGConversation,
    RAGMessage,
    RAGAccessPermission,
    RAGUsageLog,
    RAGConfigHistory,
)
from apps.graph_rag.exceptions import (
    RAGInstanceNotFound,
    KnowledgeBaseNotFound,
    DocumentNotFound,
    RAGConversationNotFound,
)


class RAGSelector:
    """Query-only methods cho graph_rag app."""

    # ── RAG Instance ────────────────────────────────
    @staticmethod
    def get_instance(instance_id) -> RAGInstance:
        try:
            return RAGInstance.objects.select_related(
                "provider", "agent_config", "created_by"
            ).get(id=instance_id, is_deleted=False)
        except RAGInstance.DoesNotExist:
            raise RAGInstanceNotFound("RAG instance không tồn tại")

    @staticmethod
    def get_instance_by_slug(slug: str) -> RAGInstance:
        try:
            return RAGInstance.objects.select_related(
                "provider", "agent_config", "created_by"
            ).get(slug=slug, is_deleted=False)
        except RAGInstance.DoesNotExist:
            raise RAGInstanceNotFound(f"RAG instance '{slug}' không tồn tại")

    @staticmethod
    def list_instances(*, user=None, include_inactive: bool = False):
        """List instances user có quyền truy cập."""
        qs = RAGInstance.objects.filter(is_deleted=False).select_related(
            "provider", "agent_config", "created_by"
        )
        if not include_inactive:
            qs = qs.filter(is_active=True)
        if user and not user.is_staff:
            # Public OR user has access
            qs = qs.filter(
                Q(is_public=True)
                | Q(
                    id__in=RAGAccessPermission.objects.filter(
                        user=user,
                        is_deleted=False,
                    )
                    .filter(
                        Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
                    )
                    .values_list("rag_instance_id", flat=True)
                )
                | Q(created_by=user)
            )
        return qs.order_by("-created_at")

    @staticmethod
    def list_instance_kbs(instance_id):
        return (
            RAGInstanceKnowledgeBase.objects.filter(
                rag_instance_id=instance_id, is_deleted=False
            )
            .select_related("knowledge_base")
            .order_by("priority")
        )

    @staticmethod
    def list_instance_skills(instance_id):
        return (
            RAGInstanceSkill.objects.filter(
                rag_instance_id=instance_id, is_deleted=False
            )
            .select_related("skill")
            .order_by("skill__name")
        )

    # ── Knowledge Base ──────────────────────────────
    @staticmethod
    def get_kb(kb_id) -> KnowledgeBase:
        try:
            return KnowledgeBase.objects.get(id=kb_id, is_deleted=False)
        except KnowledgeBase.DoesNotExist:
            raise KnowledgeBaseNotFound("Knowledge Base không tồn tại")

    @staticmethod
    def get_kb_by_slug(slug: str) -> KnowledgeBase:
        try:
            return KnowledgeBase.objects.get(slug=slug, is_deleted=False)
        except KnowledgeBase.DoesNotExist:
            raise KnowledgeBaseNotFound(f"Knowledge Base '{slug}' không tồn tại")

    @staticmethod
    def list_kbs(include_inactive: bool = False):
        qs = KnowledgeBase.objects.filter(is_deleted=False)
        if not include_inactive:
            qs = qs.filter(is_active=True)
        return qs.order_by("-created_at")

    @staticmethod
    def list_documents(kb_id, *, is_image: bool | None = None):
        qs = Document.objects.filter(
            knowledge_base_id=kb_id, is_deleted=False
        ).order_by("-created_at")
        if is_image is not None:
            qs = qs.filter(is_image=is_image)
        return qs

    @staticmethod
    def get_document(doc_id) -> Document:
        try:
            return Document.objects.select_related("knowledge_base").get(
                id=doc_id, is_deleted=False
            )
        except Document.DoesNotExist:
            raise DocumentNotFound("Document không tồn tại")

    @staticmethod
    def list_chunks(document_id, *, is_image_chunk: bool | None = None):
        qs = DocumentChunk.objects.filter(
            document_id=document_id, is_deleted=False
        ).order_by("chunk_index")
        if is_image_chunk is not None:
            qs = qs.filter(is_image_chunk=is_image_chunk)
        return qs

    # ── Knowledge Graph ─────────────────────────────
    @staticmethod
    def get_graph(kb_id):
        try:
            return KnowledgeGraph.objects.get(
                knowledge_base_id=kb_id, is_deleted=False
            )
        except KnowledgeGraph.DoesNotExist:
            return None

    # ── Skills ──────────────────────────────────────
    @staticmethod
    def list_skills():
        return RAGSkill.objects.filter(is_deleted=False, is_active=True).order_by("name")

    # ── Conversations ───────────────────────────────
    @staticmethod
    def list_conversations(*, instance_id, user_id):
        return RAGConversation.objects.filter(
            rag_instance_id=instance_id,
            user_id=user_id,
            is_deleted=False,
        ).order_by("-updated_at")

    @staticmethod
    def get_conversation(conversation_id, user_id) -> RAGConversation:
        try:
            return RAGConversation.objects.get(
                id=conversation_id, user_id=user_id, is_deleted=False
            )
        except RAGConversation.DoesNotExist:
            raise RAGConversationNotFound("Conversation không tồn tại")

    # ── Access ──────────────────────────────────────
    @staticmethod
    def list_access_permissions(instance_id):
        return RAGAccessPermission.objects.filter(
            rag_instance_id=instance_id, is_deleted=False
        ).select_related("user", "granted_by").order_by("-created_at")

    # ── Analytics ───────────────────────────────────
    @staticmethod
    def list_config_history(instance_id, limit: int = 20):
        return RAGConfigHistory.objects.filter(
            rag_instance_id=instance_id
        ).order_by("-created_at")[:limit]

    @staticmethod
    def list_usage_logs(instance_id, *, limit: int = 50):
        return RAGUsageLog.objects.filter(
            rag_instance_id=instance_id
        ).order_by("-created_at")[:limit]
