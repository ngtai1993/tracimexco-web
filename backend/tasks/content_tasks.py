"""
Celery tasks cho hệ thống contents, scheduling, và platforms.
"""
import logging
import uuid

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name="task_scan_pending_schedules")
def task_scan_pending_schedules():
    """Quét tất cả PostSchedule pending đã đến giờ đăng, dispatch task_publish_post."""
    from apps.scheduling.selectors import ScheduleSelector
    from apps.scheduling.models import PostSchedule
    from apps.scheduling.constants import ScheduleStatus

    due = ScheduleSelector.get_pending_due()
    count = 0
    for schedule in due:
        # Set processing để tránh scan lại
        PostSchedule.objects.filter(id=schedule.id).update(status=ScheduleStatus.PROCESSING)
        task_publish_post.delay(str(schedule.id))
        count += 1
    logger.info(f"[scan_pending_schedules] Dispatched {count} publish tasks.")
    return count


@shared_task(
    name="task_generate_content",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
)
def task_generate_content(self, generation_id: str):
    """Gọi RAG để generate nội dung bài viết."""
    from apps.contents.services import AIGenerationService
    try:
        AIGenerationService.process_generation(generation_id)
        logger.info(f"[generate_content] generation={generation_id} done.")
    except Exception as exc:
        logger.error(f"[generate_content] generation={generation_id} error: {exc}")
        raise self.retry(exc=exc)


@shared_task(
    name="task_generate_banner_layout",
    bind=True,
    max_retries=2,
    default_retry_delay=30,
)
def task_generate_banner_layout(self, post_id: str, rag_instance_id: str, variants: int = 3):
    """Gọi RAG để generate banner layout cho bài viết."""
    from apps.contents.services import BannerLayoutService
    try:
        BannerLayoutService.process_generation(post_id, rag_instance_id, variants)
        logger.info(f"[generate_banner_layout] post={post_id} done.")
    except Exception as exc:
        logger.error(f"[generate_banner_layout] post={post_id} error: {exc}")
        raise self.retry(exc=exc)


@shared_task(
    name="task_publish_post",
    bind=True,
    max_retries=3,
)
def task_publish_post(self, schedule_id: str):
    """Đăng bài lên platform qua webhook. Retry với exponential backoff."""
    from apps.scheduling.selectors import ScheduleSelector
    from apps.scheduling.services import SchedulingService
    from apps.scheduling.constants import RETRY_DELAYS
    from apps.platforms.services import WebhookService

    try:
        schedule = ScheduleSelector.get_by_id(schedule_id)
    except Exception as exc:
        logger.error(f"[publish_post] schedule={schedule_id} not found: {exc}")
        return

    attempt_number = self.request.retries + 1
    try:
        WebhookService.send_outgoing(
            platform=schedule.platform,
            schedule_id=str(schedule.id),
            post=schedule.post,
        )
        SchedulingService.record_attempt(
            schedule=schedule,
            attempt_number=attempt_number,
            success=True,
        )
        logger.info(f"[publish_post] schedule={schedule_id} published (attempt {attempt_number}).")
    except Exception as exc:
        logger.warning(f"[publish_post] schedule={schedule_id} attempt {attempt_number} failed: {exc}")
        SchedulingService.record_attempt(
            schedule=schedule,
            attempt_number=attempt_number,
            success=False,
            error_message=str(exc),
        )
        if attempt_number <= len(RETRY_DELAYS):
            delay = RETRY_DELAYS[attempt_number - 1]
            raise self.retry(exc=exc, countdown=delay)


@shared_task(name="task_log_webhook")
def task_log_webhook(log_data: dict):
    """Fire-and-forget: lưu WebhookLog từ background."""
    from apps.platforms.models import WebhookLog
    try:
        WebhookLog.objects.create(**log_data)
    except Exception as exc:
        logger.error(f"[log_webhook] Failed to save log: {exc}")


@shared_task(name="task_health_check_all_platforms")
def task_health_check_all_platforms():
    """Kiểm tra sức khỏe tất cả platform đang active."""
    from apps.platforms.models import Platform
    from apps.platforms.services import WebhookService

    platforms = Platform.objects.filter(is_active=True, is_deleted=False)
    results = {}
    for platform in platforms:
        try:
            health = WebhookService.health_check(platform)
            results[str(platform.id)] = health
        except Exception as exc:
            logger.error(f"[health_check] platform={platform.slug} error: {exc}")
            results[str(platform.id)] = "error"
    logger.info(f"[health_check_all_platforms] Results: {results}")
    return results
