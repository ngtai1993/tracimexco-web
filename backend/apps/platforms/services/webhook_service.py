import hashlib
import hmac
import json
import logging
from datetime import datetime

import requests
from django.utils import timezone

from apps.platforms.constants import WebhookDirection, HealthStatus
from apps.platforms.exceptions import InvalidWebhookSignature, WebhookDeliveryError

logger = logging.getLogger(__name__)


class WebhookService:

    @staticmethod
    def send_outgoing(platform, schedule, post) -> dict:
        """Gửi payload bài viết đến platform.webhook_url kèm HMAC signature."""
        payload = {
            "schedule_id": str(schedule.id),
            "post_id": str(post.id),
            "title": post.title,
            "content": post.content,
            "hashtags": post.hashtags,
            "platform_type": post.platform_type,
            "published_at": timezone.now().isoformat(),
        }
        payload_str = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
        signature = WebhookService._sign(payload_str, platform.webhook_secret)
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "X-Webhook-Signature": f"sha256={signature}",
            "X-Webhook-Event": "publish",
            "X-Schedule-Id": str(schedule.id),
        }
        response_status = None
        response_body = ""
        error_message = ""
        try:
            response = requests.post(
                platform.webhook_url,
                data=payload_str.encode("utf-8"),
                headers=headers,
                timeout=30,
            )
            response_status = response.status_code
            response_body = response.text[:5000]
            if response.status_code >= 400:
                raise WebhookDeliveryError(
                    f"Platform returned {response.status_code}: {response_body[:200]}"
                )
        except requests.RequestException as exc:
            error_message = str(exc)
            raise WebhookDeliveryError(f"Request failed: {exc}") from exc
        finally:
            WebhookService._log(
                platform=platform,
                direction=WebhookDirection.OUTGOING,
                event_type="publish",
                payload=payload,
                response_status=response_status,
                response_body=response_body,
                schedule_id=str(schedule.id),
                error_message=error_message,
            )
        return {"status_code": response_status, "body": response_body}

    @staticmethod
    def verify_incoming_signature(platform_slug: str, raw_body: bytes, signature_header: str) -> "WebhookEndpoint":
        """Verify HMAC signature và trả về WebhookEndpoint nếu hợp lệ."""
        from apps.platforms.selectors.platform_selector import PlatformSelector
        from apps.platforms.exceptions import InvalidWebhookSignature

        try:
            endpoint = PlatformSelector.get_active_endpoint_by_slug(platform_slug)
        except Exception as exc:
            raise InvalidWebhookSignature("Platform hoặc endpoint không tồn tại.") from exc

        if not signature_header or not signature_header.startswith("sha256="):
            raise InvalidWebhookSignature("Header X-Webhook-Signature thiếu hoặc sai format.")

        provided_sig = signature_header[len("sha256="):]
        expected_sig = WebhookService._sign(raw_body.decode("utf-8", errors="replace"), endpoint.secret_key)
        if not hmac.compare_digest(provided_sig, expected_sig):
            raise InvalidWebhookSignature("Chữ ký HMAC không khớp.")
        return endpoint

    @staticmethod
    def process_incoming_event(platform_slug: str, event_type: str, payload: dict) -> None:
        """Xử lý sự kiện từ callback của nền tảng — cập nhật PostSchedule."""
        from apps.platforms.selectors.platform_selector import PlatformSelector
        try:
            platform = PlatformSelector.get_by_slug(platform_slug)
        except Exception:
            logger.warning("Platform %s not found for incoming event", platform_slug)
            return

        WebhookService._log(
            platform=platform,
            direction=WebhookDirection.INCOMING,
            event_type=event_type,
            payload=payload,
            response_status=200,
            schedule_id=payload.get("schedule_id"),
        )

        schedule_id = payload.get("schedule_id")
        if not schedule_id:
            return

        try:
            from apps.scheduling.models import PostSchedule, PublishAttempt
            from apps.scheduling.constants import ScheduleStatus, AttemptStatus
            schedule = PostSchedule.objects.get(id=schedule_id, is_deleted=False)
            if event_type == "publish_success":
                schedule.status = ScheduleStatus.PUBLISHED
                schedule.save(update_fields=["status", "updated_at"])
                PublishAttempt.objects.filter(schedule=schedule).order_by("-created_at").first()
            elif event_type == "publish_error":
                schedule.status = ScheduleStatus.FAILED
                schedule.save(update_fields=["status", "updated_at"])
        except Exception as exc:
            logger.warning("Could not update schedule from incoming event: %s", exc)

    @staticmethod
    def health_check(platform) -> str:
        """Ping webhook_url và trả về health_status."""
        from apps.platforms.constants import HealthStatus
        try:
            response = requests.head(platform.webhook_url, timeout=10)
            if response.status_code < 500:
                new_status = HealthStatus.HEALTHY
            else:
                new_status = HealthStatus.DEGRADED
        except requests.RequestException:
            new_status = HealthStatus.UNREACHABLE

        platform.health_status = new_status
        platform.last_health_check_at = timezone.now()
        platform.save(update_fields=["health_status", "last_health_check_at", "updated_at"])
        return new_status

    @staticmethod
    def _sign(payload: str, secret: str) -> str:
        return hmac.new(
            secret.encode("utf-8") if secret else b"",
            payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    @staticmethod
    def _log(
        platform,
        direction: str,
        event_type: str,
        payload: dict,
        response_status=None,
        response_body="",
        schedule_id=None,
        error_message="",
    ) -> None:
        try:
            from apps.platforms.models import WebhookLog
            WebhookLog.objects.create(
                platform=platform,
                direction=direction,
                event_type=event_type,
                payload=payload,
                response_status=response_status,
                response_body=response_body[:5000],
                schedule_id=schedule_id,
                error_message=error_message,
            )
        except Exception as exc:
            logger.warning("Failed to log webhook: %s", exc)
