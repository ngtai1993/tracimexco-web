import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2)
def task_mark_key_used(self, key_id: str):
    """Cập nhật last_used_at cho API key sau khi được sử dụng (fire-and-forget)."""
    try:
        from apps.agents.services.agent_key_service import AgentKeyService
        AgentKeyService.mark_key_used(key_id)
    except Exception as exc:
        logger.warning("task_mark_key_used failed for key_id=%s: %s", key_id, exc)
