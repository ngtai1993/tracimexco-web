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

    # Default models per provider
    _PROVIDER_DEFAULT_MODELS: dict = {
        "google-gemini": "gemini-2.0-flash",
        "openai": "gpt-4o-mini",
        "anthropic": "claude-3-5-haiku-20241022",
    }
    _PLACEHOLDER_MARKERS: tuple = ("sample", "placeholder", "dev-only", "only-xxx", "for-dev", "test")

    @staticmethod
    def _generate_answer(
        instance: RAGInstance,
        query: str,
        context: str,
        images: list[dict],
    ) -> str:
        """Generate answer using the RAG instance's configured provider/model.

        Resolution order:
        1. Use the provider set on the instance with its stored API key.
        2. If the key is missing or a placeholder, fall back to google-gemini.
        3. If Gemini key is also unavailable, return an error string.
        """
        from apps.agents.services.agent_key_service import AgentKeyService
        from apps.agents.exceptions import AgentAPIKeyNotFound

        provider_slug = instance.provider.slug
        api_key = None

        if provider_slug == "google-gemini":
            try:
                api_key = AgentKeyService.get_active_key("google-gemini")
            except AgentAPIKeyNotFound:
                pass
        else:
            # Try the configured provider first
            try:
                candidate = AgentKeyService.get_active_key(provider_slug)
                if any(m in candidate for m in PipelineService._PLACEHOLDER_MARKERS):
                    raise ValueError("placeholder key")
                api_key = candidate
            except Exception:
                # Key missing or placeholder — fall back to Gemini
                logger.info(
                    "Provider '%s' key not available or placeholder, falling back to google-gemini",
                    provider_slug,
                )
                try:
                    api_key = AgentKeyService.get_active_key("google-gemini")
                    provider_slug = "google-gemini"
                except AgentAPIKeyNotFound:
                    pass

        if not api_key:
            return (
                f"[Lỗi: không lấy được API key cho provider '{instance.provider.slug}']\n\n"
                f"Query: {query}"
            )

        gen_config = instance.generation_config or {}
        default_model = PipelineService._PROVIDER_DEFAULT_MODELS.get(provider_slug, "gemini-2.0-flash")
        # Prefer model from agent_config (when provider unchanged), then gen_config, then default
        if instance.agent_config and instance.provider.slug == provider_slug:
            model_name = instance.agent_config.model_name or gen_config.get("model_name") or default_model
        else:
            model_name = gen_config.get("model_name") or default_model
        # Guard: if we fell back to Gemini, ensure the model slug is a Gemini model
        if provider_slug == "google-gemini" and not model_name.startswith("gemini"):
            model_name = "gemini-2.0-flash"

        temperature = float(gen_config.get("temperature", 0.7))
        max_tokens = int(gen_config.get("max_tokens", 1024))

        # Build system prompt
        system_prompt_template = instance.system_prompt or (
            "Bạn là trợ lý AI. Sử dụng context bên dưới để trả lời câu hỏi.\n\n"
            "Context:\n{context}\n\n"
            "Nếu không tìm thấy thông tin liên quan, hãy nói rõ."
        )
        try:
            system_prompt = system_prompt_template.format(
                context=context or "(không có context)",
                sources="",
                language="Vietnamese",
            )
        except KeyError:
            system_prompt = system_prompt_template

        answer = PipelineService._call_provider(
            provider_slug=provider_slug,
            api_key=api_key,
            model_name=model_name,
            system_prompt=system_prompt,
            query=query,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        if images:
            answer += f"\n\n---\n*Tìm thấy {len(images)} hình ảnh liên quan.*"

        return answer

    @staticmethod
    def _call_provider(
        *,
        provider_slug: str,
        api_key: str,
        model_name: str,
        system_prompt: str,
        query: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Dispatch to the correct LLM SDK based on provider_slug."""

        if provider_slug == "google-gemini":
            try:
                import google.generativeai as genai

                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(
                    model_name=model_name,
                    generation_config=genai.GenerationConfig(
                        temperature=temperature,
                        max_output_tokens=max_tokens,
                    ),
                )
                full_prompt = f"{system_prompt}\n\nCâu hỏi: {query}"
                response = model.generate_content(full_prompt)
                return response.text
            except Exception as exc:
                logger.exception("Gemini API call failed: %s", exc)
                raise RuntimeError(f"Lỗi gọi Gemini API: {exc}") from exc

        elif provider_slug == "openai":
            try:
                import openai as openai_sdk

                client = openai_sdk.OpenAI(api_key=api_key)
                resp = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": query},
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return resp.choices[0].message.content
            except Exception as exc:
                logger.exception("OpenAI API call failed: %s", exc)
                raise RuntimeError(f"Lỗi gọi OpenAI API: {exc}") from exc

        elif provider_slug == "anthropic":
            try:
                import anthropic as anthropic_sdk

                client = anthropic_sdk.Anthropic(api_key=api_key)
                resp = client.messages.create(
                    model=model_name,
                    max_tokens=max_tokens,
                    system=system_prompt,
                    messages=[{"role": "user", "content": query}],
                )
                return resp.content[0].text
            except Exception as exc:
                logger.exception("Anthropic API call failed: %s", exc)
                raise RuntimeError(f"Lỗi gọi Anthropic API: {exc}") from exc

        else:
            raise RuntimeError(
                f"Provider '{provider_slug}' chưa được hỗ trợ. "
                f"Các provider hỗ trợ: google-gemini, openai, anthropic."
            )

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
