from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser

from apps.agents.selectors.agent_selector import AgentSelector
from apps.agents.services.agent_key_service import AgentKeyService
from apps.agents.serializers import (
    AgentAPIKeyWriteSerializer,
    AgentAPIKeyUpdateSerializer,
    AgentAPIKeyOutputSerializer,
)
from apps.agents.exceptions import AgentProviderNotFound, AgentAPIKeyNotFound
from apps.agents.models import AgentAPIKey


class KeyListCreateView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, slug):
        try:
            provider = AgentSelector.get_provider_by_slug_admin(slug)
        except AgentProviderNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        qs = AgentSelector.list_keys_for_provider(provider.id)
        serializer = AgentAPIKeyOutputSerializer(qs, many=True)
        return Response({"data": serializer.data, "message": "success", "errors": None})

    def post(self, request, slug):
        try:
            provider = AgentSelector.get_provider_by_slug_admin(slug)
        except AgentProviderNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = AgentAPIKeyWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        key = AgentKeyService.create_key(
            provider_id=provider.id,
            name=data["name"],
            raw_key=data["raw_key"],
            priority=data.get("priority", 1),
            expires_at=data.get("expires_at"),
            created_by=request.user,
        )
        out = AgentAPIKeyOutputSerializer(key)
        return Response(
            {"data": out.data, "message": "API key đã được thêm thành công", "errors": None},
            status=status.HTTP_201_CREATED,
        )


class KeyDetailView(APIView):
    permission_classes = [IsAdminUser]

    def _get_key(self, slug: str, pk):
        try:
            return AgentAPIKey.objects.get(id=pk, provider__slug=slug, is_deleted=False)
        except AgentAPIKey.DoesNotExist:
            raise AgentAPIKeyNotFound(f"Không tìm thấy key với id='{pk}'")

    def patch(self, request, slug, pk):
        try:
            key = self._get_key(slug, pk)
        except AgentAPIKeyNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = AgentAPIKeyUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        key = AgentKeyService.update_key(key.id, **serializer.validated_data)
        out = AgentAPIKeyOutputSerializer(key)
        return Response(
            {"data": out.data, "message": "API key đã được cập nhật", "errors": None}
        )

    def delete(self, request, slug, pk):
        try:
            key = self._get_key(slug, pk)
        except AgentAPIKeyNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        AgentKeyService.soft_delete_key(key.id)
        return Response(status=status.HTTP_204_NO_CONTENT)
