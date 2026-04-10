import logging

from django.db import transaction

from apps.contents.models import AIContentGeneration
from apps.contents.constants import GenerationStatus, GenerationType

logger = logging.getLogger(__name__)


class AIGenerationService:

    @staticmethod
    @transaction.atomic
    def create_generation(
        rag_instance,
        created_by,
        generation_type: str,
        prompt: str,
        context_data: dict = None,
    ) -> AIContentGeneration:
        """Tạo generation record và dispatch Celery task."""
        gen = AIContentGeneration.objects.create(
            rag_instance=rag_instance,
            created_by=created_by,
            generation_type=generation_type,
            prompt=prompt,
            context_data=context_data or {},
            status=GenerationStatus.PENDING,
        )
        # Dispatch async task — import here to avoid circular at module level
        from tasks.content_tasks import task_generate_content
        task_generate_content.delay(str(gen.id))
        return gen

    @staticmethod
    def process_generation(generation_id: str) -> None:
        """Được gọi bởi Celery task — thực thi RAG pipeline."""
        try:
            gen = AIContentGeneration.objects.get(id=generation_id, is_deleted=False)
        except AIContentGeneration.DoesNotExist:
            logger.warning("AIContentGeneration %s not found", generation_id)
            return

        gen.status = GenerationStatus.PROCESSING
        gen.save(update_fields=["status", "updated_at"])

        try:
            content = AIGenerationService._call_rag(gen)
            variants_count = gen.context_data.get("variants", 1)
            if variants_count > 1 and gen.generation_type == GenerationType.AB_VARIANT:
                gen.result_variants = content if isinstance(content, list) else [content]
            else:
                gen.result_content = content if isinstance(content, str) else str(content)
            gen.status = GenerationStatus.COMPLETED
            gen.error_message = ""
        except Exception as exc:
            logger.exception("Generation failed for %s", generation_id)
            gen.status = GenerationStatus.FAILED
            gen.error_message = str(exc)

        gen.save(update_fields=[
            "result_content", "result_variants", "status", "error_message", "updated_at"
        ])

    @staticmethod
    def _call_rag(gen: AIContentGeneration):
        """Gọi RAG pipeline để sinh nội dung."""
        try:
            from apps.graph_rag.services.pipeline_service import PipelineService
            result = PipelineService.process_query(
                rag_instance_id=str(gen.rag_instance_id),
                query=gen.prompt,
                user_id=str(gen.created_by_id),
                conversation_id=None,
            )
            return result.get("message", {}).get("content", "")
        except (ImportError, AttributeError) as exc:
            raise RuntimeError(f"RAG pipeline không khả dụng: {exc}") from exc
