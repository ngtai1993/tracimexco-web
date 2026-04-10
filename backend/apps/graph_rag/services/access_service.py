import logging
from django.utils import timezone
from datetime import timedelta

from apps.graph_rag.models import RAGAccessPermission, RAGUsageLog
from apps.graph_rag.exceptions import RAGAccessDenied, RAGQuotaExceeded

logger = logging.getLogger(__name__)


class AccessService:
    """Permission & quota management."""

    @staticmethod
    def check_access(*, instance_id: str, user_id: str) -> bool:
        """Kiểm tra user có quyền truy cập RAG instance không."""
        return RAGAccessPermission.objects.filter(
            rag_instance_id=instance_id,
            user_id=user_id,
            is_deleted=False,
        ).filter(
            # Chưa hết hạn
            models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=timezone.now())
        ).exists()

    @staticmethod
    def check_quota(*, instance_id: str, user_id: str) -> None:
        """Kiểm tra quota. Raise RAGQuotaExceeded nếu vượt quá."""
        try:
            perm = RAGAccessPermission.objects.get(
                rag_instance_id=instance_id,
                user_id=user_id,
                is_deleted=False,
            )
        except RAGAccessPermission.DoesNotExist:
            return  # Public instance hoặc admin — không cần kiểm tra quota

        # Daily query limit
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        daily_count = RAGUsageLog.objects.filter(
            rag_instance_id=instance_id,
            user_id=user_id,
            created_at__gte=today_start,
        ).count()

        if daily_count >= perm.daily_query_limit:
            raise RAGQuotaExceeded(
                f"Bạn đã đạt giới hạn {perm.daily_query_limit} queries/ngày"
            )

        # Monthly token limit
        month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_tokens = RAGUsageLog.objects.filter(
            rag_instance_id=instance_id,
            user_id=user_id,
            created_at__gte=month_start,
        ).aggregate(total=models.Sum("tokens_in") + models.Sum("tokens_out"))

        total = monthly_tokens.get("total") or 0
        if total >= perm.monthly_token_limit:
            raise RAGQuotaExceeded(
                f"Bạn đã đạt giới hạn {perm.monthly_token_limit:,} tokens/tháng"
            )

    @staticmethod
    def grant_access(
        *,
        instance_id: str,
        user_id: str,
        access_level: str = "use",
        daily_query_limit: int = 100,
        monthly_token_limit: int = 1_000_000,
        granted_by=None,
        expires_at=None,
    ) -> RAGAccessPermission:
        return RAGAccessPermission.objects.create(
            rag_instance_id=instance_id,
            user_id=user_id,
            access_level=access_level,
            daily_query_limit=daily_query_limit,
            monthly_token_limit=monthly_token_limit,
            granted_by=granted_by,
            expires_at=expires_at,
        )

    @staticmethod
    def get_my_access(*, instance_id: str, user_id: str) -> dict | None:
        """Lấy thông tin access của user cho instance."""
        try:
            perm = RAGAccessPermission.objects.get(
                rag_instance_id=instance_id,
                user_id=user_id,
                is_deleted=False,
            )
        except RAGAccessPermission.DoesNotExist:
            return None

        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        daily_used = RAGUsageLog.objects.filter(
            rag_instance_id=instance_id,
            user_id=user_id,
            created_at__gte=today_start,
        ).count()

        month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_tokens = RAGUsageLog.objects.filter(
            rag_instance_id=instance_id,
            user_id=user_id,
            created_at__gte=month_start,
        ).aggregate(total=models.Sum("tokens_in"))

        return {
            "has_access": True,
            "access_level": perm.access_level,
            "daily_query_limit": perm.daily_query_limit,
            "daily_queries_used": daily_used,
            "monthly_token_limit": perm.monthly_token_limit,
            "monthly_tokens_used": monthly_tokens.get("total") or 0,
            "expires_at": perm.expires_at.isoformat() if perm.expires_at else None,
        }


# Import at bottom for models.Q, models.Sum usage
from django.db import models  # noqa: E402
