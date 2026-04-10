from django.urls import path
from apps.scheduling.views import (
    ScheduleListCreateView,
    ScheduleDetailView,
    ScheduleCancelView,
    ScheduleAttemptListView,
    QueueView,
)

app_name = "scheduling"

urlpatterns = [
    path("", ScheduleListCreateView.as_view(), name="schedule-list-create"),
    path("queue/", QueueView.as_view(), name="schedule-queue"),
    path("<uuid:pk>/", ScheduleDetailView.as_view(), name="schedule-detail"),
    path("<uuid:pk>/cancel/", ScheduleCancelView.as_view(), name="schedule-cancel"),
    path("<uuid:pk>/attempts/", ScheduleAttemptListView.as_view(), name="schedule-attempts"),
]
