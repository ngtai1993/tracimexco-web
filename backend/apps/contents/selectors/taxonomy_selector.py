from apps.contents.models import Category, Tag
from apps.contents.exceptions import CategoryNotFound, TagNotFound


class TaxonomySelector:

    @staticmethod
    def get_root_categories():
        """Lấy categories gốc (không có parent) kèm children."""
        return (
            Category.objects
            .filter(parent__isnull=True, is_deleted=False)
            .prefetch_related("children")
            .order_by("order", "name")
        )

    @staticmethod
    def get_all_categories():
        """Lấy toàn bộ categories (flat list) — dùng để build tree ở service/serializer."""
        return Category.objects.filter(is_deleted=False).select_related("parent").order_by("order", "name")

    @staticmethod
    def get_category_by_slug(slug: str) -> Category:
        try:
            return Category.objects.get(slug=slug, is_deleted=False)
        except Category.DoesNotExist:
            raise CategoryNotFound(f"Không tìm thấy danh mục slug='{slug}'")

    @staticmethod
    def get_tags(search: str = None):
        qs = Tag.objects.filter(is_deleted=False)
        if search:
            qs = qs.filter(name__icontains=search)
        return qs

    @staticmethod
    def get_tag_by_id(tag_id: str) -> Tag:
        try:
            return Tag.objects.get(id=tag_id, is_deleted=False)
        except Tag.DoesNotExist:
            raise TagNotFound(f"Không tìm thấy tag id='{tag_id}'")
