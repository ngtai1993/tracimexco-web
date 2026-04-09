from rest_framework.permissions import BasePermission


class IsOwnerOrAdmin(BasePermission):
    """Cho phép nếu user là chủ sở hữu object hoặc là admin."""

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        return hasattr(obj, "id") and obj.id == request.user.id
