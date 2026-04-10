from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser

from apps.graph_rag.selectors import RAGSelector
from apps.graph_rag.models import RAGSkill
from apps.graph_rag.serializers import RAGSkillWriteSerializer, RAGSkillOutputSerializer
from apps.graph_rag.exceptions import RAGSkillNotFound


class RAGSkillListCreateView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        skills = RAGSelector.list_skills()
        return Response(
            {"data": RAGSkillOutputSerializer(skills, many=True).data, "message": "success", "errors": None}
        )

    def post(self, request):
        serializer = RAGSkillWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        skill = serializer.save(created_by=request.user)
        return Response(
            {"data": RAGSkillOutputSerializer(skill).data, "message": "Skill đã được tạo", "errors": None},
            status=status.HTTP_201_CREATED,
        )


class RAGSkillDetailView(APIView):
    permission_classes = [IsAdminUser]

    def _get_skill(self, pk):
        try:
            return RAGSkill.objects.get(id=pk, is_deleted=False)
        except RAGSkill.DoesNotExist:
            raise RAGSkillNotFound(f"Skill không tồn tại")

    def get(self, request, pk):
        try:
            skill = self._get_skill(pk)
        except RAGSkillNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {"data": RAGSkillOutputSerializer(skill).data, "message": "success", "errors": None}
        )

    def patch(self, request, pk):
        try:
            skill = self._get_skill(pk)
        except RAGSkillNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = RAGSkillWriteSerializer(skill, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        skill = serializer.save()
        return Response(
            {"data": RAGSkillOutputSerializer(skill).data, "message": "Đã cập nhật skill", "errors": None}
        )

    def delete(self, request, pk):
        try:
            skill = self._get_skill(pk)
        except RAGSkillNotFound as e:
            return Response(
                {"data": None, "message": str(e), "errors": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        skill.is_deleted = True
        skill.save(update_fields=["is_deleted"])
        return Response(status=status.HTTP_204_NO_CONTENT)
