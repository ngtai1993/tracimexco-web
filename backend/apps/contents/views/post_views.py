from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.contents.exceptions import PostNotFound, InvalidStatusTransition, PostMediaNotFound
from apps.contents.models import PostMedia, PostComment
from apps.contents.selectors import PostSelector
from apps.contents.services import PostService
from apps.contents.serializers import (
    PostListSerializer,
    PostDetailSerializer,
    PostWriteSerializer,
    PostMediaWriteSerializer,
    PostMediaOutputSerializer,
    PostVersionOutputSerializer,
    PostCommentWriteSerializer,
    PostCommentOutputSerializer,
)
from common.pagination import StandardResultsPagination


class PostListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        filters = {
            "status": request.query_params.get("status"),
            "platform_type": request.query_params.get("platform_type"),
            "category": request.query_params.get("category"),
            "search": request.query_params.get("search"),
            "is_ai_generated": request.query_params.get("is_ai_generated"),
        }
        # Creator only sees own posts; staff sees all
        if not request.user.is_staff:
            filters["author_id"] = str(request.user.id)
        active_filters = {k: v for k, v in filters.items() if v is not None}
        posts = PostSelector.get_list(**active_filters)
        paginator = StandardResultsPagination()
        page = paginator.paginate_queryset(posts, request)
        serializer = PostListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = PostWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        post = PostService.create(dict(serializer.validated_data), author=request.user)
        return Response(
            {"data": PostDetailSerializer(post).data, "message": "Bài viết đã được tạo.", "errors": None},
            status=status.HTTP_201_CREATED,
        )


class PostDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_post(self, post_id: str):
        return PostSelector.get_by_id(post_id)

    def get(self, request, post_id):
        try:
            post = self._get_post(post_id)
        except PostNotFound as e:
            return Response({"data": None, "message": str(e), "errors": None}, status=status.HTTP_404_NOT_FOUND)
        return Response({"data": PostDetailSerializer(post, context={"request": request}).data, "message": "OK", "errors": None})

    def patch(self, request, post_id):
        try:
            post = self._get_post(post_id)
        except PostNotFound as e:
            return Response({"data": None, "message": str(e), "errors": None}, status=status.HTTP_404_NOT_FOUND)
        if not request.user.is_staff and post.author_id != request.user.id:
            return Response({"data": None, "message": "Không có quyền chỉnh sửa.", "errors": None}, status=status.HTTP_403_FORBIDDEN)
        serializer = PostWriteSerializer(post, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        post = PostService.update(post, dict(serializer.validated_data), changed_by=request.user)
        return Response({"data": PostDetailSerializer(post).data, "message": "Bài viết đã cập nhật.", "errors": None})

    def delete(self, request, post_id):
        try:
            post = self._get_post(post_id)
        except PostNotFound as e:
            return Response({"data": None, "message": str(e), "errors": None}, status=status.HTTP_404_NOT_FOUND)
        try:
            PostService.soft_delete(post, request.user)
        except InvalidStatusTransition as e:
            return Response({"data": None, "message": str(e), "errors": None}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"data": None, "message": "Bài viết đã được xóa.", "errors": None}, status=status.HTTP_204_NO_CONTENT)


class PostDuplicateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        try:
            post = PostSelector.get_by_id(post_id)
        except PostNotFound as e:
            return Response({"data": None, "message": str(e), "errors": None}, status=status.HTTP_404_NOT_FOUND)
        platform_type = request.data.get("platform_type", post.platform_type)
        new_post = PostService.duplicate(post, platform_type=platform_type, author=request.user)
        return Response(
            {"data": PostDetailSerializer(new_post).data, "message": "Bài viết đã được nhân bản.", "errors": None},
            status=status.HTTP_201_CREATED,
        )


class PostSubmitReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        try:
            post = PostSelector.get_by_id(post_id)
        except PostNotFound as e:
            return Response({"data": None, "message": str(e), "errors": None}, status=status.HTTP_404_NOT_FOUND)
        if post.author_id != request.user.id:
            return Response({"data": None, "message": "Chỉ tác giả mới có thể nộp review.", "errors": None}, status=status.HTTP_403_FORBIDDEN)
        try:
            post = PostService.submit_review(post)
        except InvalidStatusTransition as e:
            return Response({"data": None, "message": str(e), "errors": None}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"data": PostDetailSerializer(post).data, "message": "Đã nộp để review.", "errors": None})


class PostApproveView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, post_id):
        try:
            post = PostSelector.get_by_id(post_id)
        except PostNotFound as e:
            return Response({"data": None, "message": str(e), "errors": None}, status=status.HTTP_404_NOT_FOUND)
        try:
            post = PostService.approve(post)
        except InvalidStatusTransition as e:
            return Response({"data": None, "message": str(e), "errors": None}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"data": PostDetailSerializer(post).data, "message": "Bài viết đã được duyệt.", "errors": None})


class PostRejectView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, post_id):
        try:
            post = PostSelector.get_by_id(post_id)
        except PostNotFound as e:
            return Response({"data": None, "message": str(e), "errors": None}, status=status.HTTP_404_NOT_FOUND)
        reason = request.data.get("reason", "")
        if not reason:
            return Response({"data": None, "message": "Vui lòng nhập lý do trả về.", "errors": None}, status=status.HTTP_400_BAD_REQUEST)
        try:
            post = PostService.reject(post, reason=reason, rejector=request.user)
        except InvalidStatusTransition as e:
            return Response({"data": None, "message": str(e), "errors": None}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"data": PostDetailSerializer(post).data, "message": "Bài viết đã được trả về.", "errors": None})


class PostVersionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, post_id):
        try:
            post = PostSelector.get_by_id(post_id)
        except PostNotFound as e:
            return Response({"data": None, "message": str(e), "errors": None}, status=status.HTTP_404_NOT_FOUND)
        versions = PostSelector.get_versions(post)
        return Response({"data": PostVersionOutputSerializer(versions, many=True).data, "message": "OK", "errors": None})


class PostMediaListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        try:
            post = PostSelector.get_by_id(post_id)
        except PostNotFound as e:
            return Response({"data": None, "message": str(e), "errors": None}, status=status.HTTP_404_NOT_FOUND)
        serializer = PostMediaWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        media = PostMedia.objects.create(post=post, **serializer.validated_data)
        return Response(
            {"data": PostMediaOutputSerializer(media, context={"request": request}).data, "message": "Media đã được tải lên.", "errors": None},
            status=status.HTTP_201_CREATED,
        )


class PostMediaDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, post_id, media_id):
        try:
            media = PostMedia.objects.get(id=media_id, post_id=post_id, is_deleted=False)
        except PostMedia.DoesNotExist:
            return Response({"data": None, "message": "Không tìm thấy media.", "errors": None}, status=status.HTTP_404_NOT_FOUND)
        media.soft_delete()
        return Response({"data": None, "message": "Media đã được xóa.", "errors": None}, status=status.HTTP_204_NO_CONTENT)


class PostCommentListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, post_id):
        try:
            post = PostSelector.get_by_id(post_id)
        except PostNotFound as e:
            return Response({"data": None, "message": str(e), "errors": None}, status=status.HTTP_404_NOT_FOUND)
        comments = PostSelector.get_comments(post)
        return Response({"data": PostCommentOutputSerializer(comments, many=True).data, "message": "OK", "errors": None})

    def post(self, request, post_id):
        try:
            post = PostSelector.get_by_id(post_id)
        except PostNotFound as e:
            return Response({"data": None, "message": str(e), "errors": None}, status=status.HTTP_404_NOT_FOUND)
        serializer = PostCommentWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = PostComment.objects.create(post=post, author=request.user, **serializer.validated_data)
        return Response(
            {"data": PostCommentOutputSerializer(comment).data, "message": "Comment đã được thêm.", "errors": None},
            status=status.HTTP_201_CREATED,
        )
