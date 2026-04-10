from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from apps.graph_rag.selectors import RAGSelector
from apps.graph_rag.services.access_service import AccessService
from apps.graph_rag.serializers import (
    GrantAccessSerializer,
    AccessPermissionOutputSerializer,
)
from apps.graph_rag.exceptions import RAGInstanceNotFound


class AccessPermissionListCreateView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, slug):
        try:
            instance = RAGSelector.get_instance_by_slug(slug)
        except RAGInstanceNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        perms = RAGSelector.list_access_permissions(instance.id)
        serializer = AccessPermissionOutputSerializer(perms, many=True)
        return Response({"data": serializer.data, "message": "success", "errors": None})

    def post(self, request, slug):
        try:
            instance = RAGSelector.get_instance_by_slug(slug)
        except RAGInstanceNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = GrantAccessSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        perm = AccessService.grant_access(
            instance_id=str(instance.id),
            granted_by=request.user,
            **serializer.validated_data,
        )
        out = AccessPermissionOutputSerializer(perm)
        return Response(
            {"data": out.data, "message": "Quyền truy cập đã được cấp", "errors": None},
            status=status.HTTP_201_CREATED,
        )


class AccessPermissionDeleteView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, slug, pk):
        from apps.graph_rag.models import RAGAccessPermission

        try:
            perm = RAGAccessPermission.objects.get(
                id=pk, rag_instance__slug=slug, is_deleted=False
            )
        except RAGAccessPermission.DoesNotExist:
            return Response(
                {"data": None, "message": "Permission không tồn tại", "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        perm.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MyAccessView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug):
        """Xem quyền truy cập và quota còn lại."""
        try:
            instance = RAGSelector.get_instance_by_slug(slug)
        except RAGInstanceNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        access = AccessService.get_my_access(
            instance_id=str(instance.id), user_id=str(request.user.id)
        )
        if access is None:
            if instance.is_public:
                access = {"has_access": True, "access_level": "use", "note": "Public instance"}
            else:
                access = {"has_access": False}
        return Response({"data": access, "message": "success", "errors": None})
