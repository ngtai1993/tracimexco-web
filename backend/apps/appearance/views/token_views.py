from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser

from apps.appearance.models import ColorToken
from apps.appearance.selectors.appearance_selector import AppearanceSelector
from apps.appearance.serializers import ColorTokenWriteSerializer, ColorTokenOutputSerializer
from apps.appearance.exceptions import ColorTokenNotFound


class TokenListCreateView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        include_inactive = request.query_params.get("include_inactive", "false").lower() == "true"
        qs = AppearanceSelector.list_all_tokens(include_inactive=include_inactive)
        serializer = ColorTokenOutputSerializer(qs, many=True)
        return Response({"data": serializer.data, "message": "success", "errors": None})

    def post(self, request):
        serializer = ColorTokenWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = ColorToken.objects.create(**serializer.validated_data)
        out = ColorTokenOutputSerializer(token)
        return Response(
            {"data": out.data, "message": "Token đã được tạo thành công.", "errors": None},
            status=status.HTTP_201_CREATED,
        )


class TokenDetailView(APIView):
    permission_classes = [IsAdminUser]

    def _get_token(self, pk) -> ColorToken:
        return AppearanceSelector.get_token_by_id(pk)

    def get(self, request, pk):
        try:
            token = self._get_token(pk)
        except ColorTokenNotFound as e:
            return Response({"data": None, "message": str(e), "errors": None}, status=status.HTTP_404_NOT_FOUND)
        return Response({"data": ColorTokenOutputSerializer(token).data, "message": "success", "errors": None})

    def patch(self, request, pk):
        try:
            token = self._get_token(pk)
        except ColorTokenNotFound as e:
            return Response({"data": None, "message": str(e), "errors": None}, status=status.HTTP_404_NOT_FOUND)

        serializer = ColorTokenWriteSerializer(token, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        for field, value in serializer.validated_data.items():
            setattr(token, field, value)
        token.save()
        return Response({"data": ColorTokenOutputSerializer(token).data, "message": "Token đã được cập nhật.", "errors": None})

    def delete(self, request, pk):
        try:
            token = self._get_token(pk)
        except ColorTokenNotFound as e:
            return Response({"data": None, "message": str(e), "errors": None}, status=status.HTTP_404_NOT_FOUND)
        token.soft_delete()
        return Response({"data": None, "message": "Token đã được xóa.", "errors": None}, status=status.HTTP_204_NO_CONTENT)
