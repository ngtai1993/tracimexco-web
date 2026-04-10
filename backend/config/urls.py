from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", include("apps.core.urls", namespace="core")),
    path("api/v1/auth/", include("apps.authentication.urls", namespace="authentication")),
    path("api/v1/users/", include("apps.users.urls", namespace="users")),
    path("api/v1/agents/", include("apps.agents.urls", namespace="agents")),
    path("api/v1/appearance/", include("apps.appearance.urls", namespace="appearance")),
    path("api/v1/graph-rag/", include("apps.graph_rag.urls", namespace="graph_rag")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    try:
        import debug_toolbar
        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
    except ImportError:
        pass
