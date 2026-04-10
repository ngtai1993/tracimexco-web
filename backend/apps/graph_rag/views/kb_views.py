from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser

from apps.graph_rag.selectors import RAGSelector
from apps.graph_rag.services.knowledge_base_service import KnowledgeBaseService
from apps.graph_rag.serializers import (
    KnowledgeBaseWriteSerializer,
    KnowledgeBaseOutputSerializer,
    DocumentUploadSerializer,
    DocumentTextSerializer,
    DocumentURLSerializer,
    DocumentOutputSerializer,
    DocumentChunkOutputSerializer,
)
from apps.graph_rag.exceptions import KnowledgeBaseNotFound, DocumentNotFound, DocumentProcessingError


class KnowledgeBaseListCreateView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        include_inactive = request.query_params.get("include_inactive", "false").lower() == "true"
        qs = RAGSelector.list_kbs(include_inactive=include_inactive)
        serializer = KnowledgeBaseOutputSerializer(qs, many=True)
        return Response({"data": serializer.data, "message": "success", "errors": None})

    def post(self, request):
        serializer = KnowledgeBaseWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        kb = KnowledgeBaseService.create_kb(
            **serializer.validated_data, created_by=request.user
        )
        out = KnowledgeBaseOutputSerializer(kb)
        return Response(
            {"data": out.data, "message": "Knowledge Base đã được tạo", "errors": None},
            status=status.HTTP_201_CREATED,
        )


class KnowledgeBaseDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, slug):
        try:
            kb = RAGSelector.get_kb_by_slug(slug)
        except KnowledgeBaseNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        out = KnowledgeBaseOutputSerializer(kb)
        return Response({"data": out.data, "message": "success", "errors": None})

    def delete(self, request, slug):
        try:
            kb = RAGSelector.get_kb_by_slug(slug)
        except KnowledgeBaseNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        KnowledgeBaseService.soft_delete_kb(kb.id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class DocumentListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, slug):
        try:
            kb = RAGSelector.get_kb_by_slug(slug)
        except KnowledgeBaseNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        is_image = request.query_params.get("is_image")
        if is_image is not None:
            is_image = is_image.lower() == "true"
        docs = RAGSelector.list_documents(kb.id, is_image=is_image)
        serializer = DocumentOutputSerializer(docs, many=True)
        return Response({"data": serializer.data, "message": "success", "errors": None})


class DocumentUploadView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, slug):
        try:
            kb = RAGSelector.get_kb_by_slug(slug)
        except KnowledgeBaseNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = DocumentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            doc = KnowledgeBaseService.upload_document(
                knowledge_base_id=kb.id,
                title=serializer.validated_data["title"],
                file=serializer.validated_data["file"],
                description=serializer.validated_data.get("description", ""),
                created_by=request.user,
            )
        except DocumentProcessingError as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_400_BAD_REQUEST,
            )
        out = DocumentOutputSerializer(doc)
        msg = "Hình ảnh đã được upload" if doc.is_image else "Document đã được upload"
        return Response(
            {"data": out.data, "message": f"{msg} và đang xử lý", "errors": None},
            status=status.HTTP_201_CREATED,
        )


class DocumentTextView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, slug):
        try:
            kb = RAGSelector.get_kb_by_slug(slug)
        except KnowledgeBaseNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = DocumentTextSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        doc = KnowledgeBaseService.add_text_document(
            knowledge_base_id=kb.id,
            **serializer.validated_data,
        )
        out = DocumentOutputSerializer(doc)
        return Response(
            {"data": out.data, "message": "Text document đã được thêm", "errors": None},
            status=status.HTTP_201_CREATED,
        )


class DocumentURLView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, slug):
        try:
            kb = RAGSelector.get_kb_by_slug(slug)
        except KnowledgeBaseNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = DocumentURLSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        doc = KnowledgeBaseService.add_url_document(
            knowledge_base_id=kb.id,
            **serializer.validated_data,
        )
        out = DocumentOutputSerializer(doc)
        return Response(
            {"data": out.data, "message": "URL document đã được thêm", "errors": None},
            status=status.HTTP_201_CREATED,
        )


class DocumentDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        try:
            doc = RAGSelector.get_document(pk)
        except DocumentNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        out = DocumentOutputSerializer(doc)
        return Response({"data": out.data, "message": "success", "errors": None})

    def delete(self, request, pk):
        try:
            RAGSelector.get_document(pk)  # Check exists
        except DocumentNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        KnowledgeBaseService.soft_delete_document(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


class DocumentChunkListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        try:
            RAGSelector.get_document(pk)
        except DocumentNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        is_image = request.query_params.get("is_image_chunk")
        if is_image is not None:
            is_image = is_image.lower() == "true"
        chunks = RAGSelector.list_chunks(pk, is_image_chunk=is_image)
        serializer = DocumentChunkOutputSerializer(chunks, many=True)
        return Response({"data": serializer.data, "message": "success", "errors": None})


class KnowledgeBaseGraphBuildView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, slug):
        """Trigger graph build cho KB."""
        try:
            kb = RAGSelector.get_kb_by_slug(slug)
        except KnowledgeBaseNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        # Dispatch async
        try:
            from tasks.graph_rag_tasks import task_build_graph
            task_build_graph.delay(str(kb.id))
            msg = "Graph build đã được bắt đầu"
        except Exception:
            # Fallback: run sync
            from apps.graph_rag.services.graph_builder_service import GraphBuilderService
            GraphBuilderService.build_graph(str(kb.id))
            msg = "Graph build hoàn tất"

        return Response(
            {"data": None, "message": msg, "errors": None},
            status=status.HTTP_202_ACCEPTED,
        )
