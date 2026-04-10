from rest_framework import status as http_status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.contents.constants import GenerationType
from apps.contents.exceptions import AIGenerationNotFound
from apps.contents.models import AIContentGeneration
from apps.contents.serializers import (
    AIGenerationOutputSerializer,
    AIGenerateWriteSerializer,
    AISuggestHashtagsSerializer,
    AISummarizeSerializer,
    AITranslateSerializer,
    AIImproveSerializer,
    AIGenerateCaptionSerializer,
)
from apps.contents.services import AIGenerationService


class AIGenerateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AIGenerateWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            from apps.graph_rag.models import RAGInstance
            rag_instance = RAGInstance.objects.get(id=data["rag_instance"], is_active=True, is_deleted=False)
        except Exception:
            return Response({"data": None, "message": "RAG Instance không tồn tại hoặc không hoạt động.", "errors": None}, status=http_status.HTTP_400_BAD_REQUEST)

        context_data = {
            "platform_type": data.get("platform_type", ""),
            "variants": data.get("variants", 1),
            "language": data.get("language", "vi"),
        }
        gen_type = GenerationType.AB_VARIANT if data.get("variants", 1) > 1 else GenerationType.FULL_POST

        gen = AIGenerationService.create_generation(
            rag_instance=rag_instance,
            created_by=request.user,
            generation_type=gen_type,
            prompt=data["prompt"],
            context_data=context_data,
        )
        return Response(
            {"data": {"generation_id": str(gen.id), "status": gen.status}, "message": "Đang xử lý.", "errors": None},
            status=http_status.HTTP_202_ACCEPTED,
        )


class AIGenerationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, generation_id):
        try:
            gen = AIContentGeneration.objects.get(id=generation_id, is_deleted=False)
        except AIContentGeneration.DoesNotExist:
            return Response({"data": None, "message": "Không tìm thấy generation.", "errors": None}, status=http_status.HTTP_404_NOT_FOUND)
        if not request.user.is_staff and gen.created_by_id != request.user.id:
            return Response({"data": None, "message": "Không có quyền truy cập.", "errors": None}, status=http_status.HTTP_403_FORBIDDEN)
        return Response({"data": AIGenerationOutputSerializer(gen).data, "message": "OK", "errors": None})


class AISuggestHashtagsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AISuggestHashtagsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        count = data.get("count", 10)
        prompt = (
            f"Đề xuất {count} hashtag phù hợp cho bài viết trên nền tảng "
            f"{data.get('platform_type', 'mạng xã hội')}.\n\n"
            f"Nội dung:\n{data['content']}\n\n"
            "Trả về danh sách hashtag, mỗi hashtag bắt đầu bằng #."
        )
        # Simple stub — returns placeholder; full implementation hooks into RAG
        return Response({"data": {"hashtags": [], "prompt_used": prompt}, "message": "Tính năng sẽ hoạt động khi RAG được cấu hình.", "errors": None})


class AISummarizeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AISummarizeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"data": {"summary": ""}, "message": "Tính năng sẽ hoạt động khi RAG được cấu hình.", "errors": None})


class AITranslateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AITranslateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"data": {"translated": ""}, "message": "Tính năng sẽ hoạt động khi RAG được cấu hình.", "errors": None})


class AIImproveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AIImproveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"data": {"improved": ""}, "message": "Tính năng sẽ hoạt động khi RAG được cấu hình.", "errors": None})


class AIGenerateCaptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AIGenerateCaptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"data": {"caption": ""}, "message": "Tính năng sẽ hoạt động khi RAG được cấu hình.", "errors": None})
