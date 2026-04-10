from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.scheduling.models import PostSchedule, PublishAttempt
from apps.scheduling.constants import ScheduleStatus

User = get_user_model()


class ScheduleSelector:

    @staticmethod
    def get_list(user=None, status=None, platform_slug=None, from_dt=None, to_dt=None):
        """Trả về danh sách lịch đăng. Non-staff chỉ xem bài của mình."""
        qs = PostSchedule.objects.filter(is_deleted=False).select_related("post", "platform")
        if user and not user.is_staff:
            qs = qs.filter(post__author=user)
        if status:
            qs = qs.filter(status=status)
        if platform_slug:
            qs = qs.filter(platform__slug=platform_slug)
        if from_dt:
            qs = qs.filter(scheduled_at__gte=from_dt)
        if to_dt:
            qs = qs.filter(scheduled_at__lte=to_dt)
        return qs.order_by("scheduled_at")

    @staticmethod
    def get_by_id(schedule_id: str) -> PostSchedule:
        from apps.scheduling.exceptions import ScheduleNotFound
        try:
            return PostSchedule.objects.select_related("post", "platform").get(id=schedule_id, is_deleted=False)
        except PostSchedule.DoesNotExist:
            raise ScheduleNotFound(f"Lịch đăng {schedule_id} không tồn tại.")

    @staticmethod
    def get_attempts(schedule_id: str):
        return PublishAttempt.objects.filter(schedule_id=schedule_id).order_by("attempt_number")

    @staticmethod
    def get_pending_due():
        """Trả về tất cả lịch Pending đã đến giờ đăng."""
        return PostSchedule.objects.filter(
            status=ScheduleStatus.PENDING,
            scheduled_at__lte=timezone.now(),
            is_deleted=False,
        ).select_related("post", "platform")

    @staticmethod
    def get_queue(hours: int = 24):
        """Hàng đợi: lịch Pending trong N giờ tới."""
        now = timezone.now()
        future = now + timezone.timedelta(hours=hours)
        return PostSchedule.objects.filter(
            status=ScheduleStatus.PENDING,
            scheduled_at__gte=now,
            scheduled_at__lte=future,
            is_deleted=False,
        ).select_related("post", "platform").order_by("scheduled_at")
