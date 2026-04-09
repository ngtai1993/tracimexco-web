from .celery import app as celery_app
from . import email_tasks  # noqa: F401 — ensure tasks are registered

__all__ = ("celery_app",)
