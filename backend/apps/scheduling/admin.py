from django.contrib import admin
from apps.scheduling.models import PostSchedule, PublishAttempt


@admin.register(PostSchedule)
class PostScheduleAdmin(admin.ModelAdmin):
    list_display = ["id", "post", "platform", "scheduled_at", "timezone", "status", "created_at"]
    list_filter = ["status", "platform", "timezone"]
    search_fields = ["post__title", "platform__name"]
    readonly_fields = ["id", "created_at", "updated_at"]
    ordering = ["scheduled_at"]


@admin.register(PublishAttempt)
class PublishAttemptAdmin(admin.ModelAdmin):
    list_display = ["id", "schedule", "attempt_number", "attempted_at", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["schedule__post__title"]
    readonly_fields = ["id", "created_at", "updated_at"]
    ordering = ["-attempted_at"]
