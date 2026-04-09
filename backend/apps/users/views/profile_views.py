from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, JSONParser

from apps.users.serializers import UserOutputSerializer, UserUpdateSerializer
from apps.users import services


class MeView(APIView):
    """Xem và cập nhật profile của user đang đăng nhập."""

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, JSONParser]

    def get(self, request):
        serializer = UserOutputSerializer(request.user)
        return Response({"data": serializer.data, "message": "OK", "errors": None})

    def patch(self, request):
        serializer = UserUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = services.update_profile(request.user, **serializer.validated_data)
        out = UserOutputSerializer(user)
        return Response({"data": out.data, "message": "Profile đã được cập nhật", "errors": None})
