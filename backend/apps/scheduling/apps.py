from django.apps import AppConfig


class SchedulingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.scheduling"

    def ready(self):
        from django.db.models.signals import post_migrate
        post_migrate.connect(_setup_periodic_tasks, sender=self)


def _setup_periodic_tasks(sender, **kwargs):
    """Đăng ký Celery Beat periodic task sau khi migrate."""
    try:
        from django_celery_beat.models import PeriodicTask, IntervalSchedule
        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=1,
            period=IntervalSchedule.MINUTES,
        )
        PeriodicTask.objects.update_or_create(
            name="scan-pending-schedules",
            defaults={
                "task": "tasks.content_tasks.task_scan_pending_schedules",
                "interval": schedule,
                "enabled": True,
            },
        )
        health_schedule, _ = IntervalSchedule.objects.get_or_create(
            every=15,
            period=IntervalSchedule.MINUTES,
        )
        PeriodicTask.objects.update_or_create(
            name="webhook-health-check-all",
            defaults={
                "task": "tasks.content_tasks.task_health_check_all_platforms",
                "interval": health_schedule,
                "enabled": True,
            },
        )
    except Exception:
        # Table might not exist yet during the very first migration
        pass
