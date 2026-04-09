from django.urls import path
from apps.agents.views import (
    ProviderListCreateView,
    ProviderDetailView,
    KeyListCreateView,
    KeyDetailView,
    ConfigListCreateView,
    ConfigDetailView,
)

app_name = "agents"

urlpatterns = [
    path("providers/", ProviderListCreateView.as_view(), name="provider-list"),
    path("providers/<slug:slug>/", ProviderDetailView.as_view(), name="provider-detail"),
    path("providers/<slug:slug>/keys/", KeyListCreateView.as_view(), name="key-list"),
    path("providers/<slug:slug>/keys/<uuid:pk>/", KeyDetailView.as_view(), name="key-detail"),
    path("providers/<slug:slug>/configs/", ConfigListCreateView.as_view(), name="config-list"),
    path("providers/<slug:slug>/configs/<uuid:pk>/", ConfigDetailView.as_view(), name="config-detail"),
]
