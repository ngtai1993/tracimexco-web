from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.contents.exceptions import CategoryNotFound, CategoryHasChildren, CategoryHasPosts
from apps.contents.models import Category
from apps.contents.selectors import TaxonomySelector
from apps.contents.serializers import (
    CategoryWriteSerializer,
    CategoryOutputSerializer,
    TagWriteSerializer,
    TagOutputSerializer,
)
from apps.contents.exceptions import TagNotFound


class CategoryListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def get(self, request):
        categories = TaxonomySelector.get_root_categories()
        serializer = CategoryOutputSerializer(categories, many=True)
        return Response({"data": serializer.data, "message": "OK", "errors": None})

    def post(self, request):
        serializer = CategoryWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cat = Category(**serializer.validated_data)
        cat.save()
        out = CategoryOutputSerializer(cat)
        return Response(
            {"data": out.data, "message": "Danh mục đã được tạo.", "errors": None},
            status=status.HTTP_201_CREATED,
        )


class CategoryDetailView(APIView):
    permission_classes = [IsAdminUser]

    def _get(self, slug: str) -> Category:
        return TaxonomySelector.get_category_by_slug(slug)

    def patch(self, request, slug):
        try:
            cat = self._get(slug)
        except CategoryNotFound as e:
            return Response({"data": None, "message": str(e), "errors": None}, status=status.HTTP_404_NOT_FOUND)
        serializer = CategoryWriteSerializer(cat, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        for field, value in serializer.validated_data.items():
            setattr(cat, field, value)
        cat.save()
        return Response({"data": CategoryOutputSerializer(cat).data, "message": "Danh mục đã cập nhật.", "errors": None})

    def delete(self, request, slug):
        try:
            cat = self._get(slug)
        except CategoryNotFound as e:
            return Response({"data": None, "message": str(e), "errors": None}, status=status.HTTP_404_NOT_FOUND)
        if cat.children.filter(is_deleted=False).exists():
            return Response(
                {"data": None, "message": "Không thể xóa danh mục đang có danh mục con.", "errors": None},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if cat.posts.filter(is_deleted=False).exists():
            return Response(
                {"data": None, "message": "Không thể xóa danh mục đang có bài viết.", "errors": None},
                status=status.HTTP_400_BAD_REQUEST,
            )
        cat.soft_delete()
        return Response({"data": None, "message": "Danh mục đã được xóa.", "errors": None}, status=status.HTTP_204_NO_CONTENT)


class TagListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search = request.query_params.get("search")
        tags = TaxonomySelector.get_tags(search=search)
        serializer = TagOutputSerializer(tags, many=True)
        return Response({"data": serializer.data, "message": "OK", "errors": None})

    def post(self, request):
        serializer = TagWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        from apps.contents.models import Tag
        from django.utils.text import slugify
        tag = Tag(name=serializer.validated_data["name"])
        tag.save()
        return Response(
            {"data": TagOutputSerializer(tag).data, "message": "Tag đã được tạo.", "errors": None},
            status=status.HTTP_201_CREATED,
        )
