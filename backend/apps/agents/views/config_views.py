from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser

from apps.agents.selectors.agent_selector import AgentSelector
from apps.agents.services.agent_key_service import AgentKeyService
from apps.agents.serializers import (
    AgentConfigWriteSerializer,
    AgentConfigUpdateSerializer,
    AgentConfigOutputSerializer,
)
from apps.agents.exceptions import AgentProviderNotFound, AgentConfigNotFound
from apps.agents.models import AgentConfig


class ConfigListCreateView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, slug):
        try:
            provider = AgentSelector.get_provider_by_slug_admin(slug)
        except AgentProviderNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        qs = AgentSelector.list_configs_for_provider(provider.id)
        serializer = AgentConfigOutputSerializer(qs, many=True)
        return Response({"data": serializer.data, "message": "success", "errors": None})

    def post(self, request, slug):
        try:
            provider = AgentSelector.get_provider_by_slug_admin(slug)
        except AgentProviderNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = AgentConfigWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        config = AgentKeyService.create_config(
            provider_id=provider.id,
            name=data["name"],
            model_name=data["model_name"],
            config_json=data.get("config_json", {}),
            is_default=data.get("is_default", False),
            is_active=data.get("is_active", True),
        )
        out = AgentConfigOutputSerializer(config)
        return Response(
            {"data": out.data, "message": "Config đã được tạo thành công", "errors": None},
            status=status.HTTP_201_CREATED,
        )


class ConfigDetailView(APIView):
    permission_classes = [IsAdminUser]

    def _get_config(self, slug: str, pk):
        try:
            return AgentConfig.objects.get(id=pk, provider__slug=slug, is_deleted=False)
        except AgentConfig.DoesNotExist:
            raise AgentConfigNotFound(f"Không tìm thấy config với id='{pk}'")

    def patch(self, request, slug, pk):
        try:
            config = self._get_config(slug, pk)
        except AgentConfigNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = AgentConfigUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        config = AgentKeyService.update_config(config.id, **serializer.validated_data)
        out = AgentConfigOutputSerializer(config)
        return Response(
            {"data": out.data, "message": "Config đã được cập nhật", "errors": None}
        )

    def delete(self, request, slug, pk):
        try:
            config = self._get_config(slug, pk)
        except AgentConfigNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        AgentKeyService.soft_delete_config(config.id)
        return Response(status=status.HTTP_204_NO_CONTENT)
