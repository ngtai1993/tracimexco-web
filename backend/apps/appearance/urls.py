from django.urls import path
from apps.appearance.views import (
    AppearanceConfigView,
    AppearanceCSSView,
    TokenListCreateView,
    TokenDetailView,
    AssetListCreateView,
    AssetDetailView,
)

app_name = "appearance"

urlpatterns = [
    # Public
    path("config/", AppearanceConfigView.as_view(), name="config"),
    path("config/css/", AppearanceCSSView.as_view(), name="config-css"),
    # Admin
    path("tokens/", TokenListCreateView.as_view(), name="token-list"),
    path("tokens/<uuid:pk>/", TokenDetailView.as_view(), name="token-detail"),
    path("assets/", AssetListCreateView.as_view(), name="asset-list"),
    path("assets/<uuid:pk>/", AssetDetailView.as_view(), name="asset-detail"),
]
