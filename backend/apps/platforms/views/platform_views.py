import json
import logging

from rest_framework import status as http_status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.platforms.exceptions import PlatformNotFound, InvalidWebhookSignature
from apps.platforms.models import Platform, WebhookEndpoint
from apps.platforms.selectors import PlatformSelector
from apps.platforms.serializers import (
    PlatformWriteSerializer,
    PlatformOutputSerializer,
    WebhookEndpointWriteSerializer,
    WebhookEndpointOutputSerializer,
    WebhookLogOutputSerializer,
)
from apps.platforms.services import WebhookService
from common.pagination import StandardResultsPagination

logger = logging.getLogger(__name__)


class PlatformListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def get(self, request):
        include_inactive = request.query_params.get("include_inactive", "false").lower() == "true"
        platforms = PlatformSelector.get_all(include_inactive=include_inactive)
        return Response({"data": PlatformOutputSerializer(platforms, many=True).data, "message": "OK", "errors": None})

    def post(self, request):
        serializer = PlatformWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        platform = Platform(**serializer.validated_data)
        platform.save()
        return Response(
            {"data": PlatformOutputSerializer(platform).data, "message": "Nền tảng đã được tạo.", "errors": None},
            status=http_status.HTTP_201_CREATED,
        )


class PlatformDetailView(APIView):
    permission_classes = [IsAdminUser]

    def _get(self, slug):
        return PlatformSelector.get_by_slug(slug)

    def patch(self, request, slug):
        try:
            platform = self._get(slug)
        except PlatformNotFound as e:
            return Response({"data": None, "message": str(e), "errors": None}, status=http_status.HTTP_404_NOT_FOUND)
        serializer = PlatformWriteSerializer(platform, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        for field, value in serializer.validated_data.items():
            setattr(platform, field, value)
        platform.save()
        return Response({"data": PlatformOutputSerializer(platform).data, "message": "Nền tảng đã cập nhật.", "errors": None})

    def delete(self, request, slug):
        try:
            platform = self._get(slug)
        except PlatformNotFound as e:
            return Response({"data": None, "message": str(e), "errors": None}, status=http_status.HTTP_404_NOT_FOUND)
        platform.soft_delete()
        return Response({"data": None, "message": "Nền tảng đã được xóa.", "errors": None}, status=http_status.HTTP_204_NO_CONTENT)


class PlatformHealthView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, slug):
        try:
            platform = PlatformSelector.get_by_slug(slug)
        except PlatformNotFound as e:
            return Response({"data": None, "message": str(e), "errors": None}, status=http_status.HTTP_404_NOT_FOUND)
        new_status = WebhookService.health_check(platform)
        return Response({"data": {"health_status": new_status}, "message": "Health check hoàn tất.", "errors": None})


class WebhookEndpointListCreateView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, slug):
        try:
            platform = PlatformSelector.get_by_slug(slug)
        except PlatformNotFound as e:
            return Response({"data": None, "message": str(e), "errors": None}, status=http_status.HTTP_404_NOT_FOUND)
        endpoints = PlatformSelector.get_endpoints(platform)
        return Response({"data": WebhookEndpointOutputSerializer(endpoints, many=True).data, "message": "OK", "errors": None})

    def post(self, request, slug):
        try:
            platform = PlatformSelector.get_by_slug(slug)
        except PlatformNotFound as e:
            return Response({"data": None, "message": str(e), "errors": None}, status=http_status.HTTP_404_NOT_FOUND)
        serializer = WebhookEndpointWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        endpoint = WebhookEndpoint.objects.create(platform=platform, **serializer.validated_data)
        return Response(
            {"data": WebhookEndpointOutputSerializer(endpoint).data, "message": "Endpoint đã được thêm.", "errors": None},
            status=http_status.HTTP_201_CREATED,
        )


class WebhookIncomingView(APIView):
    """Public endpoint nhận callback từ nền tảng bên ngoài."""
    permission_classes = []
    authentication_classes = []

    def post(self, request, platform_slug):
        raw_body = request.body
        signature_header = request.headers.get("X-Webhook-Signature", "")

        try:
            WebhookService.verify_incoming_signature(platform_slug, raw_body, signature_header)
        except InvalidWebhookSignature as e:
            logger.warning("Invalid webhook signature for platform %s: %s", platform_slug, e)
            return Response({"error": "Invalid signature"}, status=http_status.HTTP_401_UNAUTHORIZED)

        try:
            payload = json.loads(raw_body)
        except (json.JSONDecodeError, ValueError):
            return Response({"error": "Invalid JSON body"}, status=http_status.HTTP_400_BAD_REQUEST)

        event_type = payload.get("event_type", "")
        WebhookService.process_incoming_event(platform_slug, event_type, payload)
        return Response({"data": None, "message": "OK", "errors": None})


class WebhookLogListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, slug):
        try:
            platform = PlatformSelector.get_by_slug(slug)
        except PlatformNotFound as e:
            return Response({"data": None, "message": str(e), "errors": None}, status=http_status.HTTP_404_NOT_FOUND)
        direction = request.query_params.get("direction")
        logs = PlatformSelector.get_logs(platform, direction=direction)
        paginator = StandardResultsPagination()
        page = paginator.paginate_queryset(logs, request)
        return paginator.get_paginated_response(WebhookLogOutputSerializer(page, many=True).data)
