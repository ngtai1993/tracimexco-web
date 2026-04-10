from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser

from apps.appearance.models import MediaAsset
from apps.appearance.selectors.appearance_selector import AppearanceSelector
from apps.appearance.serializers import MediaAssetWriteSerializer, MediaAssetOutputSerializer
from apps.appearance.exceptions import MediaAssetNotFound


class AssetListCreateView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        include_inactive = request.query_params.get("include_inactive", "false").lower() == "true"
        qs = AppearanceSelector.list_all_assets(include_inactive=include_inactive)
        serializer = MediaAssetOutputSerializer(qs, many=True, context={"request": request})
        return Response({"data": serializer.data, "message": "success", "errors": None})

    def post(self, request):
        serializer = MediaAssetWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        asset = MediaAsset.objects.create(**serializer.validated_data)
        out = MediaAssetOutputSerializer(asset, context={"request": request})
        return Response(
            {"data": out.data, "message": "Asset đã được tạo thành công.", "errors": None},
            status=status.HTTP_201_CREATED,
        )


class AssetDetailView(APIView):
    permission_classes = [IsAdminUser]

    def _get_asset(self, pk) -> MediaAsset:
        return AppearanceSelector.get_asset_by_id(pk)

    def get(self, request, pk):
        try:
            asset = self._get_asset(pk)
        except MediaAssetNotFound as e:
            return Response({"data": None, "message": str(e), "errors": None}, status=status.HTTP_404_NOT_FOUND)
        return Response({"data": MediaAssetOutputSerializer(asset, context={"request": request}).data, "message": "success", "errors": None})

    def patch(self, request, pk):
        try:
            asset = self._get_asset(pk)
        except MediaAssetNotFound as e:
            return Response({"data": None, "message": str(e), "errors": None}, status=status.HTTP_404_NOT_FOUND)

        serializer = MediaAssetWriteSerializer(asset, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        for field, value in serializer.validated_data.items():
            setattr(asset, field, value)
        asset.save()
        return Response({"data": MediaAssetOutputSerializer(asset, context={"request": request}).data, "message": "Asset đã được cập nhật.", "errors": None})

    def delete(self, request, pk):
        try:
            asset = self._get_asset(pk)
        except MediaAssetNotFound as e:
            return Response({"data": None, "message": str(e), "errors": None}, status=status.HTTP_404_NOT_FOUND)
        asset.soft_delete()
        return Response({"data": None, "message": "Asset đã được xóa.", "errors": None}, status=status.HTTP_204_NO_CONTENT)
