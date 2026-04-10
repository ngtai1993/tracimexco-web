import logging
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone

from apps.graph_rag.models import RAGUsageLog

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Usage logging và stats queries."""

    @staticmethod
    def log_usage(data: dict) -> None:
        """Tạo usage log entry (thường gọi từ Celery task)."""
        RAGUsageLog.objects.create(
            rag_instance_id=data["rag_instance_id"],
            user_id=data.get("user_id"),
            conversation_id=data.get("conversation_id"),
            query=data.get("query", ""),
            retrieval_strategy=data.get("retrieval_strategy", "hybrid"),
            tokens_in=data.get("tokens_in", 0),
            tokens_out=data.get("tokens_out", 0),
            latency_ms=data.get("latency_ms", 0),
            sources_count=data.get("sources_count", 0),
            images_returned=data.get("images_returned", 0),
            skills_used=data.get("skills_used", []),
        )

    @staticmethod
    def get_instance_analytics(instance_id: str, days: int = 7) -> dict:
        """Analytics cho 1 RAG instance trong N ngày gần nhất."""
        since = timezone.now() - timezone.timedelta(days=days)
        qs = RAGUsageLog.objects.filter(
            rag_instance_id=instance_id,
            created_at__gte=since,
        )

        stats = qs.aggregate(
            total_queries=Count("id"),
            unique_users=Count("user_id", distinct=True),
            total_tokens_in=Sum("tokens_in"),
            total_tokens_out=Sum("tokens_out"),
            avg_latency_ms=Avg("latency_ms"),
            total_images=Sum("images_returned"),
        )

        return {
            "period_days": days,
            "total_queries": stats["total_queries"] or 0,
            "unique_users": stats["unique_users"] or 0,
            "total_tokens_in": stats["total_tokens_in"] or 0,
            "total_tokens_out": stats["total_tokens_out"] or 0,
            "avg_latency_ms": int(stats["avg_latency_ms"] or 0),
            "total_images_returned": stats["total_images"] or 0,
        }
