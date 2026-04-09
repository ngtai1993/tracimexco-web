from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser

from apps.agents.models import AgentProvider
from apps.agents.selectors.agent_selector import AgentSelector
from apps.agents.services.agent_key_service import AgentKeyService
from apps.agents.serializers import AgentProviderWriteSerializer, AgentProviderOutputSerializer
from apps.agents.exceptions import AgentProviderNotFound


class ProviderListCreateView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        include_inactive = request.query_params.get("include_inactive", "false").lower() == "true"
        qs = AgentSelector.list_providers(include_inactive=include_inactive)
        serializer = AgentProviderOutputSerializer(qs, many=True)
        return Response({"data": serializer.data, "message": "success", "errors": None})

    def post(self, request):
        serializer = AgentProviderWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        provider = AgentProvider.objects.create(**serializer.validated_data)
        out = AgentProviderOutputSerializer(provider)
        return Response(
            {"data": out.data, "message": "Provider đã được tạo thành công", "errors": None},
            status=status.HTTP_201_CREATED,
        )


class ProviderDetailView(APIView):
    permission_classes = [IsAdminUser]

    def _get_provider(self, slug: str) -> AgentProvider:
        return AgentSelector.get_provider_by_slug_admin(slug)

    def get(self, request, slug):
        try:
            provider = self._get_provider(slug)
        except AgentProviderNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        out = AgentProviderOutputSerializer(provider)
        return Response({"data": out.data, "message": "success", "errors": None})

    def patch(self, request, slug):
        try:
            provider = self._get_provider(slug)
        except AgentProviderNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = AgentProviderWriteSerializer(provider, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        for field, value in serializer.validated_data.items():
            setattr(provider, field, value)
        provider.save()
        out = AgentProviderOutputSerializer(provider)
        return Response(
            {"data": out.data, "message": "Provider đã được cập nhật", "errors": None}
        )

    def delete(self, request, slug):
        try:
            AgentKeyService.soft_delete_provider(slug)
        except AgentProviderNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
