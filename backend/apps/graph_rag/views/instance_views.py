from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from apps.graph_rag.selectors import RAGSelector
from apps.graph_rag.services.rag_instance_service import RAGInstanceService
from apps.graph_rag.serializers import (
    RAGInstanceWriteSerializer,
    RAGInstanceUpdateSerializer,
    RAGInstanceOutputSerializer,
    RAGConfigUpdateSerializer,
    RAGInstanceCloneSerializer,
    RAGInstanceKBAssignSerializer,
    RAGInstanceSkillAssignSerializer,
)
from apps.graph_rag.exceptions import RAGInstanceNotFound


class RAGInstanceListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get(self, request):
        """List instances user có quyền truy cập."""
        include_inactive = (
            request.query_params.get("include_inactive", "false").lower() == "true"
            and request.user.is_staff
        )
        qs = RAGSelector.list_instances(
            user=request.user, include_inactive=include_inactive
        )
        serializer = RAGInstanceOutputSerializer(qs, many=True)
        return Response({"data": serializer.data, "message": "success", "errors": None})

    def post(self, request):
        """Tạo RAG instance (admin only)."""
        serializer = RAGInstanceWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = RAGInstanceService.create(
            **serializer.validated_data, created_by=request.user
        )
        out = RAGInstanceOutputSerializer(instance)
        return Response(
            {"data": out.data, "message": "RAG instance đã được tạo", "errors": None},
            status=status.HTTP_201_CREATED,
        )


class RAGInstanceDetailView(APIView):
    def get_permissions(self):
        if self.request.method in ("PATCH", "DELETE"):
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get(self, request, slug):
        try:
            instance = RAGSelector.get_instance_by_slug(slug)
        except RAGInstanceNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        out = RAGInstanceOutputSerializer(instance)
        return Response({"data": out.data, "message": "success", "errors": None})

    def patch(self, request, slug):
        try:
            instance = RAGSelector.get_instance_by_slug(slug)
        except RAGInstanceNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = RAGInstanceUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        for field, value in serializer.validated_data.items():
            setattr(instance, field, value)
        instance.save()
        out = RAGInstanceOutputSerializer(instance)
        return Response(
            {"data": out.data, "message": "RAG instance đã được cập nhật", "errors": None}
        )

    def delete(self, request, slug):
        try:
            instance = RAGSelector.get_instance_by_slug(slug)
        except RAGInstanceNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        RAGInstanceService.soft_delete(instance.id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RAGInstanceConfigView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, slug):
        """Update retrieval/generation config với history logging."""
        try:
            instance = RAGSelector.get_instance_by_slug(slug)
        except RAGInstanceNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = RAGConfigUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = RAGInstanceService.update_config(
            instance_id=instance.id,
            config_type=serializer.validated_data["config_type"],
            new_config=serializer.validated_data["config"],
            changed_by=request.user,
            reason=serializer.validated_data.get("reason", ""),
        )
        out = RAGInstanceOutputSerializer(updated)
        return Response(
            {"data": out.data, "message": "Config đã được cập nhật", "errors": None}
        )


class RAGInstanceCloneView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, slug):
        try:
            instance = RAGSelector.get_instance_by_slug(slug)
        except RAGInstanceNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = RAGInstanceCloneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        clone = RAGInstanceService.clone(
            source_id=instance.id,
            new_name=serializer.validated_data["new_name"],
            new_slug=serializer.validated_data["new_slug"],
            created_by=request.user,
        )
        out = RAGInstanceOutputSerializer(clone)
        return Response(
            {"data": out.data, "message": "RAG instance đã được clone", "errors": None},
            status=status.HTTP_201_CREATED,
        )


class RAGInstanceKBView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, slug):
        try:
            instance = RAGSelector.get_instance_by_slug(slug)
        except RAGInstanceNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        from apps.graph_rag.serializers import KnowledgeBaseOutputSerializer

        assignments = RAGSelector.list_instance_kbs(instance.id)
        data = [
            {
                "priority": a.priority,
                "knowledge_base": KnowledgeBaseOutputSerializer(a.knowledge_base).data,
            }
            for a in assignments
        ]
        return Response({"data": data, "message": "success", "errors": None})

    def post(self, request, slug):
        try:
            instance = RAGSelector.get_instance_by_slug(slug)
        except RAGInstanceNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = RAGInstanceKBAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        RAGInstanceService.assign_knowledge_base(
            instance_id=instance.id,
            kb_id=serializer.validated_data["knowledge_base_id"],
            priority=serializer.validated_data["priority"],
        )
        return Response(
            {"data": None, "message": "Knowledge Base đã được gán", "errors": None},
            status=status.HTTP_201_CREATED,
        )


class RAGInstanceKBRemoveView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, slug, kb_id):
        try:
            instance = RAGSelector.get_instance_by_slug(slug)
        except RAGInstanceNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        removed = RAGInstanceService.remove_knowledge_base(
            instance_id=instance.id,
            kb_id=kb_id,
        )
        if not removed:
            return Response(
                {"data": None, "message": "Knowledge Base không được gán cho instance này", "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class RAGInstanceSkillView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, slug):
        try:
            instance = RAGSelector.get_instance_by_slug(slug)
        except RAGInstanceNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        from apps.graph_rag.serializers import RAGSkillOutputSerializer

        assignments = RAGSelector.list_instance_skills(instance.id)
        data = [
            {
                "is_enabled": a.is_enabled,
                "config_override": a.config_override,
                "skill": RAGSkillOutputSerializer(a.skill).data,
            }
            for a in assignments
        ]
        return Response({"data": data, "message": "success", "errors": None})

    def post(self, request, slug):
        try:
            instance = RAGSelector.get_instance_by_slug(slug)
        except RAGInstanceNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = RAGInstanceSkillAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        RAGInstanceService.assign_skill(
            instance_id=instance.id,
            skill_id=serializer.validated_data["skill_id"],
            config_override=serializer.validated_data.get("config_override"),
        )
        return Response(
            {"data": None, "message": "Skill đã được gán", "errors": None},
            status=status.HTTP_201_CREATED,
        )


class RAGInstanceSkillRemoveView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, slug, skill_id):
        try:
            instance = RAGSelector.get_instance_by_slug(slug)
        except RAGInstanceNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        removed = RAGInstanceService.remove_skill(
            instance_id=instance.id,
            skill_id=skill_id,
        )
        if not removed:
            return Response(
                {"data": None, "message": "Skill không được gán cho instance này", "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class RAGSkillListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        from apps.graph_rag.serializers import RAGSkillOutputSerializer

        skills = RAGSelector.list_skills()
        return Response(
            {"data": RAGSkillOutputSerializer(skills, many=True).data, "message": "success", "errors": None}
        )
