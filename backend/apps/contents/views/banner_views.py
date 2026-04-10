from rest_framework import status as http_status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.contents.exceptions import BannerLayoutNotFound, PostNotFound
from apps.contents.models import BannerLayout, LayoutTemplate, PostTemplate
from apps.contents.selectors import PostSelector
from apps.contents.services import BannerLayoutService
from apps.contents.serializers import (
    BannerLayoutOutputSerializer,
    BannerLayoutWriteSerializer,
    BannerLayoutGenerateSerializer,
    LayoutTemplateOutputSerializer,
    LayoutTemplateWriteSerializer,
    PostTemplateOutputSerializer,
    PostTemplateWriteSerializer,
)


class BannerLayoutListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, post_id):
        try:
            post = PostSelector.get_by_id(post_id)
        except PostNotFound as e:
            return Response({"data": None, "message": str(e), "errors": None}, status=http_status.HTTP_404_NOT_FOUND)
        layouts = post.banner_layouts.filter(is_deleted=False).order_by("variant_index")
        return Response({"data": BannerLayoutOutputSerializer(layouts, many=True).data, "message": "OK", "errors": None})


class BannerLayoutGenerateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        try:
            post = PostSelector.get_by_id(post_id)
        except PostNotFound as e:
            return Response({"data": None, "message": str(e), "errors": None}, status=http_status.HTTP_404_NOT_FOUND)

        serializer = BannerLayoutGenerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        rag_instance = None
        if data.get("rag_instance"):
            try:
                from apps.graph_rag.models import RAGInstance
                rag_instance = RAGInstance.objects.get(id=data["rag_instance"], is_active=True, is_deleted=False)
            except Exception:
                pass

        BannerLayoutService.generate(post=post, rag_instance=rag_instance, variants=data.get("variants", 2))
        return Response(
            {"data": None, "message": "Đang tạo banner layout. Vui lòng kiểm tra lại sau vài giây.", "errors": None},
            status=http_status.HTTP_202_ACCEPTED,
        )


class BannerLayoutDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_layout(self, post_id, layout_id):
        try:
            return BannerLayout.objects.get(id=layout_id, post_id=post_id, is_deleted=False)
        except BannerLayout.DoesNotExist:
            raise BannerLayoutNotFound("Không tìm thấy banner layout.")

    def patch(self, request, post_id, layout_id):
        try:
            layout = self._get_layout(post_id, layout_id)
        except BannerLayoutNotFound as e:
            return Response({"data": None, "message": str(e), "errors": None}, status=http_status.HTTP_404_NOT_FOUND)
        serializer = BannerLayoutWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        layout = BannerLayoutService.update(layout, layout_json=serializer.validated_data["layout_json"])
        return Response({"data": BannerLayoutOutputSerializer(layout).data, "message": "Layout đã cập nhật.", "errors": None})


class BannerLayoutApproveView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, post_id, layout_id):
        try:
            layout = BannerLayout.objects.get(id=layout_id, post_id=post_id, is_deleted=False)
        except BannerLayout.DoesNotExist:
            return Response({"data": None, "message": "Không tìm thấy banner layout.", "errors": None}, status=http_status.HTTP_404_NOT_FOUND)
        layout = BannerLayoutService.approve(layout, approver=request.user)
        return Response({"data": BannerLayoutOutputSerializer(layout).data, "message": "Banner layout đã được duyệt.", "errors": None})


class LayoutTemplateListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def get(self, request):
        templates = LayoutTemplate.objects.filter(is_active=True, is_deleted=False).order_by("-created_at")
        platform_type = request.query_params.get("platform_type")
        if platform_type:
            templates = templates.filter(platform_type=platform_type)
        return Response({"data": LayoutTemplateOutputSerializer(templates, many=True).data, "message": "OK", "errors": None})

    def post(self, request):
        serializer = LayoutTemplateWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        template = LayoutTemplate.objects.create(**serializer.validated_data)
        return Response(
            {"data": LayoutTemplateOutputSerializer(template).data, "message": "Layout template đã được lưu.", "errors": None},
            status=http_status.HTTP_201_CREATED,
        )


class PostTemplateListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def get(self, request):
        templates = PostTemplate.objects.filter(is_active=True, is_deleted=False)
        platform_type = request.query_params.get("platform_type")
        if platform_type:
            templates = templates.filter(platform_type=platform_type)
        return Response({"data": PostTemplateOutputSerializer(templates, many=True).data, "message": "OK", "errors": None})

    def post(self, request):
        serializer = PostTemplateWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        template = PostTemplate.objects.create(**serializer.validated_data)
        return Response(
            {"data": PostTemplateOutputSerializer(template).data, "message": "Post template đã được lưu.", "errors": None},
            status=http_status.HTTP_201_CREATED,
        )


class PostTemplateUseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, template_id):
        try:
            template = PostTemplate.objects.get(id=template_id, is_active=True, is_deleted=False)
        except PostTemplate.DoesNotExist:
            return Response({"data": None, "message": "Không tìm thấy template.", "errors": None}, status=http_status.HTTP_404_NOT_FOUND)
        from apps.contents.models import Post
        from apps.contents.services import PostService
        from apps.contents.constants import PostStatus
        post_data = {
            "title": f"(Draft từ template) {template.name}",
            "content": template.content_template,
            "platform_type": template.platform_type,
            "category": template.category,
        }
        post = PostService.create(post_data, author=request.user)
        from apps.contents.serializers import PostDetailSerializer
        return Response(
            {"data": PostDetailSerializer(post).data, "message": "Bài viết đã được tạo từ template.", "errors": None},
            status=http_status.HTTP_201_CREATED,
        )
