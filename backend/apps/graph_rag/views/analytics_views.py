from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from apps.graph_rag.selectors import RAGSelector
from apps.graph_rag.services.analytics_service import AnalyticsService
from apps.graph_rag.serializers import (
    UsageLogOutputSerializer,
    ConfigHistoryOutputSerializer,
)
from apps.graph_rag.exceptions import RAGInstanceNotFound
from rest_framework import status


class InstanceAnalyticsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, slug):
        try:
            instance = RAGSelector.get_instance_by_slug(slug)
        except RAGInstanceNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        days = int(request.query_params.get("days", 7))
        analytics = AnalyticsService.get_instance_analytics(str(instance.id), days)
        return Response({"data": analytics, "message": "success", "errors": None})


class UsageLogListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, slug):
        try:
            instance = RAGSelector.get_instance_by_slug(slug)
        except RAGInstanceNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        limit = int(request.query_params.get("limit", 50))
        logs = RAGSelector.list_usage_logs(str(instance.id), limit=limit)
        serializer = UsageLogOutputSerializer(logs, many=True)
        return Response({"data": serializer.data, "message": "success", "errors": None})


class ConfigHistoryListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, slug):
        try:
            instance = RAGSelector.get_instance_by_slug(slug)
        except RAGInstanceNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        limit = int(request.query_params.get("limit", 20))
        history = RAGSelector.list_config_history(str(instance.id), limit=limit)
        serializer = ConfigHistoryOutputSerializer(history, many=True)
        return Response({"data": serializer.data, "message": "success", "errors": None})
