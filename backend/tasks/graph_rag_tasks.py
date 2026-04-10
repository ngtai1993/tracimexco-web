import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def task_process_document(self, document_id: str):
    """Process a single document (parse → chunk → embed) hoặc image (caption → embed)."""
    try:
        from apps.graph_rag.services.document_processor import DocumentProcessorService
        DocumentProcessorService.process_document(document_id)
        logger.info("Document %s processed successfully", document_id)
    except Exception as exc:
        logger.exception("Document processing failed for %s", document_id)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def task_build_graph(self, knowledge_base_id: str):
    """Build knowledge graph cho Knowledge Base."""
    try:
        from apps.graph_rag.services.graph_builder_service import GraphBuilderService
        GraphBuilderService.build_graph(knowledge_base_id)
        logger.info("Graph built successfully for KB %s", knowledge_base_id)
    except Exception as exc:
        logger.exception("Graph build failed for KB %s", knowledge_base_id)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def task_rebuild_graph(self, knowledge_base_id: str):
    """Rebuild knowledge graph (xóa cũ + build lại)."""
    try:
        from apps.graph_rag.services.graph_builder_service import GraphBuilderService
        GraphBuilderService.rebuild_graph(knowledge_base_id)
        logger.info("Graph rebuilt successfully for KB %s", knowledge_base_id)
    except Exception as exc:
        logger.exception("Graph rebuild failed for KB %s", knowledge_base_id)
        raise self.retry(exc=exc)


@shared_task
def task_log_usage(data: dict):
    """Log usage analytics (fire-and-forget)."""
    try:
        from apps.graph_rag.services.analytics_service import AnalyticsService
        AnalyticsService.log_usage(data)
    except Exception:
        logger.exception("Failed to log usage: %s", data)
