import logging
import time

from apps.graph_rag.models import (
    RAGInstance,
    RAGInstanceKnowledgeBase,
    RAGConversation,
    RAGMessage,
)
from apps.graph_rag.services.retrieval_service import RetrievalService
from apps.graph_rag.services.access_service import AccessService
from apps.graph_rag.exceptions import RAGAccessDenied, RAGInstanceNotFound

logger = logging.getLogger(__name__)


class PipelineService:
    """Điều phối toàn bộ RAG pipeline từ query → response."""

    @staticmethod
    def process_query(
        *,
        rag_instance_id: str,
        query: str,
        conversation_id: str | None = None,
        user_id: str,
    ) -> dict:
        """
        Full pipeline:
        1. Load RAG instance + config
        2. Check permissions & quota
        3. Retrieve (hybrid search + image search)
        4. Build context
        5. Generate response (LLM)
        6. Save message + log
        7. Return response with sources + images
        """
        start_time = time.time()

        # 1. Load instance
        try:
            instance = RAGInstance.objects.select_related(
                "provider", "agent_config"
            ).get(id=rag_instance_id, is_active=True, is_deleted=False)
        except RAGInstance.DoesNotExist:
            raise RAGInstanceNotFound("RAG instance không tồn tại hoặc không active")

        # 2. Check access
        if not instance.is_public:
            has_access = AccessService.check_access(
                instance_id=str(instance.id), user_id=user_id
            )
            if not has_access:
                raise RAGAccessDenied("Bạn không có quyền sử dụng RAG instance này")

        # Check quota
        AccessService.check_quota(instance_id=str(instance.id), user_id=user_id)

        # 3. Get KB IDs
        kb_ids = list(
            RAGInstanceKnowledgeBase.objects.filter(
                rag_instance=instance, is_deleted=False
            )
            .order_by("priority")
            .values_list("knowledge_base_id", flat=True)
        )

        if not kb_ids:
            return PipelineService._build_response(
                answer="RAG instance chưa có Knowledge Base nào được gán.",
                sources=[],
                images=[],
                metadata={"warning": "no_knowledge_bases"},
            )

        # 4. Retrieve
        retrieval_config = instance.retrieval_config
        retrieval_result = RetrievalService.hybrid_search(
            query=query,
            kb_ids=[str(kid) for kid in kb_ids],
            config=retrieval_config,
        )

        chunks = retrieval_result["chunks"]
        images = retrieval_result["images"]

        # 5. Build context
        context = PipelineService._build_context(chunks, images)

        # 6. Generate response (placeholder — cần LLM integration)
        answer = PipelineService._generate_answer(
            instance=instance,
            query=query,
            context=context,
            images=images,
        )

        latency_ms = int((time.time() - start_time) * 1000)

        # 7. Save conversation & message
        conversation = PipelineService._get_or_create_conversation(
            instance=instance,
            conversation_id=conversation_id,
            user_id=user_id,
            query=query,
        )

        # Save user message
        RAGMessage.objects.create(
            conversation=conversation,
            role="user",
            content=query,
        )

        # Save assistant message
        sources_json = [
            {
                "type": s.get("type", "chunk"),
                "id": s.get("id", ""),
                "content_preview": s.get("content", "")[:200],
                "document_title": s.get("document_title", ""),
                "score": s.get("score", 0),
            }
            for s in chunks
        ]
        images_json = [
            {
                "id": img.get("id", ""),
                "url": img.get("url", ""),
                "caption": img.get("caption", ""),
                "score": img.get("score", 0),
            }
            for img in images
        ]

        assistant_msg = RAGMessage.objects.create(
            conversation=conversation,
            role="assistant",
            content=answer,
            sources=sources_json,
            images=images_json,
            metadata={
                "tokens_in": 0,
                "tokens_out": 0,
                "latency_ms": latency_ms,
                "retrieval_strategy": retrieval_config.get("search_strategy", "hybrid"),
                "model": (
                    instance.agent_config.model_name if instance.agent_config else "unknown"
                ),
                "images_enabled": retrieval_config.get("images_enabled", False),
                "images_returned": len(images),
            },
        )

        # Update conversation
        conversation.message_count = conversation.messages.count()
        if not conversation.title:
            conversation.title = query[:100]
        conversation.save(update_fields=["message_count", "title", "updated_at"])

        # Log usage (async)
        try:
            from tasks.graph_rag_tasks import task_log_usage
            task_log_usage.delay({
                "rag_instance_id": str(instance.id),
                "user_id": user_id,
                "conversation_id": str(conversation.id),
                "query": query,
                "retrieval_strategy": retrieval_config.get("search_strategy", "hybrid"),
                "latency_ms": latency_ms,
                "sources_count": len(chunks),
                "images_returned": len(images),
            })
        except Exception:
            pass

        return {
            "conversation_id": str(conversation.id),
            "message": {
                "id": str(assistant_msg.id),
                "role": "assistant",
                "content": answer,
                "sources": sources_json,
                "images": images_json,
                "metadata": assistant_msg.metadata,
            },
        }

    @staticmethod
    def _build_context(chunks: list[dict], images: list[dict]) -> str:
        """Assemble context string from retrieved chunks and images."""
        parts = []

        if chunks:
            parts.append("=== Relevant Documents ===")
            for i, chunk in enumerate(chunks, 1):
                parts.append(
                    f"[{i}] (Source: {chunk.get('document_title', 'Unknown')})\n"
                    f"{chunk.get('content', '')}"
                )

        if images:
            parts.append("\n=== Relevant Images ===")
            for i, img in enumerate(images, 1):
                parts.append(
                    f"[Image {i}] {img.get('title', 'Image')}: {img.get('caption', '')}"
                )

        return "\n\n".join(parts)

    @staticmethod
    def _generate_answer(
        instance: RAGInstance,
        query: str,
        context: str,
        images: list[dict],
    ) -> str:
        """Generate answer via LLM. Placeholder."""
        # Real implementation:
        # 1. Build system prompt with {context}, {sources}
        # 2. Call LLM via AgentKeyService
        # 3. Return generated text
        #
        # from apps.agents.services.agent_key_service import AgentKeyService
        # api_key = AgentKeyService.get_active_key(instance.provider.slug)
        # config = instance.generation_config
        # system = instance.system_prompt.format(context=context, ...)
        # response = openai.chat.completions.create(...)

        answer = (
            f"[Placeholder — LLM chưa kết nối]\n\n"
            f"Query: {query}\n\n"
            f"Tìm thấy {len(context.split('['))-1} chunks liên quan."
        )

        if images:
            answer += f"\n\nTìm thấy {len(images)} hình ảnh liên quan:"
            for img in images:
                answer += f"\n- {img.get('title', 'Image')}: {img.get('caption', '')}"

        return answer

    @staticmethod
    def _get_or_create_conversation(
        *, instance, conversation_id, user_id, query
    ) -> RAGConversation:
        if conversation_id:
            try:
                return RAGConversation.objects.get(
                    id=conversation_id,
                    rag_instance=instance,
                    user_id=user_id,
                    is_deleted=False,
                )
            except RAGConversation.DoesNotExist:
                pass

        return RAGConversation.objects.create(
            rag_instance=instance,
            user_id=user_id,
            title=query[:100],
        )

    @staticmethod
    def _build_response(
        answer: str,
        sources: list,
        images: list,
        metadata: dict | None = None,
    ) -> dict:
        return {
            "conversation_id": None,
            "message": {
                "id": None,
                "role": "assistant",
                "content": answer,
                "sources": sources,
                "images": images,
                "metadata": metadata or {},
            },
        }
