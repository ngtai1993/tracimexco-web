from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from apps.graph_rag.selectors import RAGSelector
from apps.graph_rag.services.pipeline_service import PipelineService
from apps.graph_rag.services.conversation_service import ConversationService
from apps.graph_rag.serializers import (
    QuerySerializer,
    ConversationOutputSerializer,
    MessageOutputSerializer,
    FeedbackSerializer,
)
from apps.graph_rag.exceptions import (
    RAGInstanceNotFound,
    RAGConversationNotFound,
    RAGAccessDenied,
    RAGQuotaExceeded,
)


class ChatQueryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        """Gửi query tới RAG instance."""
        try:
            instance = RAGSelector.get_instance_by_slug(slug)
        except RAGInstanceNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = QuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = PipelineService.process_query(
                rag_instance_id=str(instance.id),
                query=serializer.validated_data["query"],
                conversation_id=(
                    str(serializer.validated_data["conversation_id"])
                    if serializer.validated_data.get("conversation_id")
                    else None
                ),
                user_id=str(request.user.id),
            )
        except RAGAccessDenied as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_403_FORBIDDEN,
            )
        except RAGQuotaExceeded as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        return Response({"data": result, "message": "success", "errors": None})


class ConversationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug):
        """List conversations của user trong 1 instance."""
        try:
            instance = RAGSelector.get_instance_by_slug(slug)
        except RAGInstanceNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        conversations = RAGSelector.list_conversations(
            instance_id=str(instance.id), user_id=str(request.user.id)
        )
        serializer = ConversationOutputSerializer(conversations, many=True)
        return Response({"data": serializer.data, "message": "success", "errors": None})


class ConversationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug, conversation_id):
        """Lấy messages của conversation."""
        try:
            messages = ConversationService.get_conversation_messages(
                str(conversation_id), str(request.user.id)
            )
        except RAGConversationNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({"data": messages, "message": "success", "errors": None})

    def delete(self, request, slug, conversation_id):
        try:
            ConversationService.soft_delete_conversation(
                str(conversation_id), str(request.user.id)
            )
        except RAGConversationNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class MessageFeedbackView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, message_id):
        serializer = FeedbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ConversationService.update_feedback(
            message_id=str(message_id),
            feedback=serializer.validated_data["feedback"],
            comment=serializer.validated_data.get("comment", ""),
        )
        return Response(
            {"data": None, "message": "Feedback đã được ghi nhận", "errors": None}
        )
