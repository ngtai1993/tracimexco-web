from django.db import transaction
from django.utils import timezone

from apps.scheduling.models import PostSchedule, PublishAttempt
from apps.scheduling.constants import ScheduleStatus, AttemptStatus
from apps.scheduling.exceptions import (
    ScheduleNotFound,
    InvalidScheduleStatus,
    PostNotApproved,
    ScheduleTimeInPast,
)
from apps.contents.constants import PostStatus


class SchedulingService:

    @staticmethod
    @transaction.atomic
    def create_schedule(post, platform, scheduled_at, timezone_str: str = "Asia/Ho_Chi_Minh") -> PostSchedule:
        """Lên lịch đăng bài — bài phải ở trạng thái approved."""
        if post.status != PostStatus.APPROVED:
            raise PostNotApproved("Bài viết phải được duyệt (approved) trước khi lên lịch.")
        if scheduled_at <= timezone.now():
            raise ScheduleTimeInPast("Thời gian đăng bài phải ở tương lai.")
        schedule = PostSchedule.objects.create(
            post=post,
            platform=platform,
            scheduled_at=scheduled_at,
            timezone=timezone_str,
            status=ScheduleStatus.PENDING,
        )
        # Update post status to scheduled
        from apps.contents.models import Post as PostModel
        PostModel.objects.filter(id=post.id).update(status=PostStatus.SCHEDULED)
        return schedule

    @staticmethod
    @transaction.atomic
    def reschedule(schedule: PostSchedule, new_time) -> PostSchedule:
        if schedule.status != ScheduleStatus.PENDING:
            raise InvalidScheduleStatus("Chỉ có thể thay đổi lịch ở trạng thái Pending.")
        if new_time <= timezone.now():
            raise ScheduleTimeInPast("Thời gian đăng bài phải ở tương lai.")
        schedule.scheduled_at = new_time
        schedule.save(update_fields=["scheduled_at", "updated_at"])
        return schedule

    @staticmethod
    def cancel(schedule: PostSchedule) -> PostSchedule:
        if schedule.status not in [ScheduleStatus.PENDING, ScheduleStatus.FAILED]:
            raise InvalidScheduleStatus("Chỉ có thể hủy lịch ở trạng thái Pending hoặc Failed.")
        schedule.status = ScheduleStatus.CANCELLED
        schedule.save(update_fields=["status", "updated_at"])
        # Revert post status to approved if no other active schedules
        if not PostSchedule.objects.filter(
            post=schedule.post,
            status__in=[ScheduleStatus.PENDING, ScheduleStatus.PROCESSING, ScheduleStatus.PUBLISHED],
            is_deleted=False,
        ).exclude(id=schedule.id).exists():
            from apps.contents.models import Post as PostModel
            PostModel.objects.filter(id=schedule.post_id).update(status=PostStatus.APPROVED)
        return schedule

    @staticmethod
    @transaction.atomic
    def record_attempt(schedule: PostSchedule, attempt_number: int, success: bool, error_message: str = "", response_data: dict = None) -> PublishAttempt:
        attempt_status = AttemptStatus.SUCCESS if success else AttemptStatus.FAILED
        attempt = PublishAttempt.objects.create(
            schedule=schedule,
            attempt_number=attempt_number,
            status=attempt_status,
            error_message=error_message,
            response_data=response_data or {},
        )
        if success:
            schedule.status = ScheduleStatus.PUBLISHED
            schedule.save(update_fields=["status", "updated_at"])
            from apps.contents.models import Post as PostModel
            PostModel.objects.filter(id=schedule.post_id).update(status=PostStatus.PUBLISHED)
        elif attempt_number >= 3:
            schedule.status = ScheduleStatus.FAILED
            schedule.save(update_fields=["status", "updated_at"])
        return attempt
