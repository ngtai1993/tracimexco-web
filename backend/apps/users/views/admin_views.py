from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser

from apps.users.serializers import AdminUserOutputSerializer, AdminUserUpdateSerializer
from apps.users import services, selectors
from apps.users.exceptions import UserNotFoundError
from common.pagination import StandardResultsPagination


class AdminUserListView(APIView):
    """Admin: danh sách user."""

    permission_classes = [IsAdminUser]

    def get(self, request):
        is_active = request.query_params.get("is_active")
        search = request.query_params.get("search")

        if is_active is not None:
            is_active = is_active.lower() == "true"

        qs = selectors.list_users(is_active=is_active, search=search)
        paginator = StandardResultsPagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = AdminUserOutputSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class AdminUserDetailView(APIView):
    """Admin: xem / cập nhật / xóa một user."""

    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        try:
            user = selectors.get_user_by_id(pk)
        except UserNotFoundError as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = AdminUserOutputSerializer(user)
        return Response({"data": serializer.data, "message": "OK", "errors": None})

    def patch(self, request, pk):
        serializer = AdminUserUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        try:
            user = services.update_user_by_admin(pk, **serializer.validated_data)
        except UserNotFoundError as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        out = AdminUserOutputSerializer(user)
        return Response({"data": out.data, "message": "User đã được cập nhật", "errors": None})

    def delete(self, request, pk):
        try:
            services.deactivate_user(pk)
        except UserNotFoundError as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
