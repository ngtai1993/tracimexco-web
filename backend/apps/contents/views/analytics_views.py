from django.db.models import Count, Q
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.contents.models import Post
from apps.contents.constants import PostStatus


class AnalyticsSummaryView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        qs = Post.objects.filter(is_deleted=False)
        total = qs.count()
        by_status = {
            s[0]: qs.filter(status=s[0]).count()
            for s in PostStatus.CHOICES
        }
        from apps.contents.constants import PlatformType
        by_platform = {
            p[0]: qs.filter(platform_type=p[0]).count()
            for p in PlatformType.CHOICES
        }
        ai_count = qs.filter(is_ai_generated=True).count()

        # Publish success rate from scheduling
        try:
            from apps.scheduling.models import PublishAttempt
            from apps.scheduling.constants import AttemptStatus
            total_attempts = PublishAttempt.objects.filter(is_deleted=False).count()
            success_attempts = PublishAttempt.objects.filter(status=AttemptStatus.SUCCESS, is_deleted=False).count()
            publish_success_rate = round(success_attempts / total_attempts * 100, 1) if total_attempts else None
        except Exception:
            publish_success_rate = None

        data = {
            "total_posts": total,
            "by_status": by_status,
            "by_platform": by_platform,
            "ai_generated_count": ai_count,
            "publish_success_rate": publish_success_rate,
        }
        return Response({"data": data, "message": "OK", "errors": None})


class AnalyticsPostsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        from django.utils import timezone
        from datetime import timedelta
        date_from = request.query_params.get("from")
        date_to = request.query_params.get("to")
        qs = Post.objects.filter(is_deleted=False)
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)

        from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
        group_by = request.query_params.get("group_by", "day")
        trunc_map = {"day": TruncDay, "week": TruncWeek, "month": TruncMonth}
        TruncFn = trunc_map.get(group_by, TruncDay)

        data = (
            qs.annotate(period=TruncFn("created_at"))
            .values("period")
            .annotate(count=Count("id"))
            .order_by("period")
        )
        result = [{"period": str(row["period"].date()), "count": row["count"]} for row in data]
        return Response({"data": result, "message": "OK", "errors": None})


class AnalyticsPublishHistoryView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        try:
            from apps.scheduling.models import PostSchedule
            from apps.scheduling.serializers import ScheduleOutputSerializer
            qs = PostSchedule.objects.filter(is_deleted=False).select_related("post", "platform").order_by("-created_at")
            platform = request.query_params.get("platform")
            sched_status = request.query_params.get("status")
            if platform:
                qs = qs.filter(platform__slug=platform)
            if sched_status:
                qs = qs.filter(status=sched_status)
            from common.pagination import StandardResultsPagination
            paginator = StandardResultsPagination()
            page = paginator.paginate_queryset(qs, request)
            return paginator.get_paginated_response(ScheduleOutputSerializer(page, many=True).data)
        except Exception as exc:
            return Response({"data": [], "message": str(exc), "errors": None})
