from django.db import connection
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status


class HealthCheckView(APIView):
    """Kiểm tra trạng thái hệ thống: DB và Redis."""

    permission_classes = [AllowAny]

    def get(self, request):
        db_status = self._check_database()
        redis_status = self._check_redis()

        all_ok = db_status == "ok" and redis_status == "ok"
        http_status = status.HTTP_200_OK if all_ok else status.HTTP_503_SERVICE_UNAVAILABLE

        return Response(
            {
                "data": {
                    "status": "ok" if all_ok else "error",
                    "database": db_status,
                    "redis": redis_status,
                },
                "message": "Service is healthy" if all_ok else "Service degraded",
                "errors": None,
            },
            status=http_status,
        )

    def _check_database(self) -> str:
        try:
            connection.ensure_connection()
            return "ok"
        except Exception:
            return "error"

    def _check_redis(self) -> str:
        try:
            cache.set("health_check", "ok", timeout=10)
            result = cache.get("health_check")
            return "ok" if result == "ok" else "error"
        except Exception:
            return "error"
