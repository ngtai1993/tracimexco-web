from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from common.pagination import StandardResultsPagination

from apps.scheduling.selectors import ScheduleSelector
from apps.scheduling.services import SchedulingService
from apps.scheduling.serializers import (
    ScheduleWriteSerializer,
    ScheduleRescheduleSerializer,
    ScheduleOutputSerializer,
    AttemptOutputSerializer,
)
from apps.scheduling.exceptions import ScheduleNotFound
from apps.contents.selectors import PostSelector
from apps.platforms.selectors import PlatformSelector


class ScheduleListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = ScheduleSelector.get_list(
            user=request.user,
            status=request.query_params.get("status"),
            platform_slug=request.query_params.get("platform"),
            from_dt=request.query_params.get("from_dt"),
            to_dt=request.query_params.get("to_dt"),
        )
        paginator = StandardResultsPagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = ScheduleOutputSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = ScheduleWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        post = PostSelector.get_by_id(str(data["post_id"]))
        platform = PlatformSelector.get_by_slug(data["platform_slug"])

        schedule = SchedulingService.create_schedule(
            post=post,
            platform=platform,
            scheduled_at=data["scheduled_at"],
            timezone_str=data.get("timezone", "Asia/Ho_Chi_Minh"),
        )
        out = ScheduleOutputSerializer(schedule)
        return Response(
            {"data": out.data, "message": "Lịch đăng được tạo thành công.", "errors": None},
            status=status.HTTP_201_CREATED,
        )


class ScheduleDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        schedule = ScheduleSelector.get_by_id(str(pk))
        if not request.user.is_staff and schedule.post.author != request.user:
            return Response({"data": None, "message": "Không có quyền.", "errors": None}, status=status.HTTP_403_FORBIDDEN)
        out = ScheduleOutputSerializer(schedule)
        return Response({"data": out.data, "message": "OK", "errors": None})

    def patch(self, request, pk):
        schedule = ScheduleSelector.get_by_id(str(pk))
        if not request.user.is_staff and schedule.post.author != request.user:
            return Response({"data": None, "message": "Không có quyền.", "errors": None}, status=status.HTTP_403_FORBIDDEN)
        serializer = ScheduleRescheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        schedule = SchedulingService.reschedule(schedule, serializer.validated_data["scheduled_at"])
        out = ScheduleOutputSerializer(schedule)
        return Response({"data": out.data, "message": "Lịch đã được cập nhật.", "errors": None})


class ScheduleCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        schedule = ScheduleSelector.get_by_id(str(pk))
        if not request.user.is_staff and schedule.post.author != request.user:
            return Response({"data": None, "message": "Không có quyền.", "errors": None}, status=status.HTTP_403_FORBIDDEN)
        schedule = SchedulingService.cancel(schedule)
        out = ScheduleOutputSerializer(schedule)
        return Response({"data": out.data, "message": "Đã hủy lịch đăng.", "errors": None})


class ScheduleAttemptListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        schedule = ScheduleSelector.get_by_id(str(pk))
        if not request.user.is_staff and schedule.post.author != request.user:
            return Response({"data": None, "message": "Không có quyền.", "errors": None}, status=status.HTTP_403_FORBIDDEN)
        attempts = ScheduleSelector.get_attempts(str(pk))
        out = AttemptOutputSerializer(attempts, many=True)
        return Response({"data": out.data, "message": "OK", "errors": None})


class QueueView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        """Hàng đợi lịch Pending trong 24 giờ tới (Admin only)."""
        hours = int(request.query_params.get("hours", 24))
        qs = ScheduleSelector.get_queue(hours=hours)
        out = ScheduleOutputSerializer(qs, many=True)
        return Response({"data": out.data, "message": "OK", "errors": None})
