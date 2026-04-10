from rest_framework import serializers

from apps.scheduling.models import PostSchedule, PublishAttempt
from apps.scheduling.constants import ScheduleStatus


class ScheduleWriteSerializer(serializers.Serializer):
    post_id = serializers.UUIDField()
    platform_slug = serializers.CharField()
    scheduled_at = serializers.DateTimeField()
    timezone = serializers.CharField(default="Asia/Ho_Chi_Minh", max_length=50)


class ScheduleRescheduleSerializer(serializers.Serializer):
    scheduled_at = serializers.DateTimeField()


class AttemptOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublishAttempt
        fields = ["id", "attempt_number", "attempted_at", "status", "error_message", "response_data", "created_at"]


class ScheduleOutputSerializer(serializers.ModelSerializer):
    post_title = serializers.CharField(source="post.title", read_only=True)
    post_status = serializers.CharField(source="post.status", read_only=True)
    platform_name = serializers.CharField(source="platform.name", read_only=True)
    platform_slug = serializers.CharField(source="platform.slug", read_only=True)
    attempts = AttemptOutputSerializer(many=True, read_only=True)

    class Meta:
        model = PostSchedule
        fields = [
            "id",
            "post_id",
            "post_title",
            "post_status",
            "platform_id",
            "platform_name",
            "platform_slug",
            "scheduled_at",
            "timezone",
            "status",
            "attempts",
            "created_at",
            "updated_at",
        ]
