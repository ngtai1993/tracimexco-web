from django.urls import path

from apps.platforms.views import (
    PlatformListCreateView,
    PlatformDetailView,
    PlatformHealthView,
    WebhookEndpointListCreateView,
    WebhookIncomingView,
    WebhookLogListView,
)

app_name = "platforms"

urlpatterns = [
    path("", PlatformListCreateView.as_view(), name="platform-list"),
    path("<slug:slug>/", PlatformDetailView.as_view(), name="platform-detail"),
    path("<slug:slug>/health/", PlatformHealthView.as_view(), name="platform-health"),
    path("<slug:slug>/webhooks/", WebhookEndpointListCreateView.as_view(), name="webhook-endpoint-list"),
    path("<slug:slug>/logs/", WebhookLogListView.as_view(), name="webhook-log-list"),
    # Public incoming endpoint
    path("incoming/<slug:platform_slug>/", WebhookIncomingView.as_view(), name="webhook-incoming"),
]
