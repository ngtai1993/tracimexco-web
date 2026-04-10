from apps.contents.models import Post, PostVersion, PostComment
from apps.contents.exceptions import PostNotFound


class PostSelector:

    @staticmethod
    def get_list(
        author_id: str = None,
        status: str = None,
        platform_type: str = None,
        category: str = None,
        search: str = None,
        is_ai_generated: str = None,
    ):
        qs = Post.objects.filter(is_deleted=False).select_related(
            "author", "category"
        ).prefetch_related("tags")
        if author_id:
            qs = qs.filter(author_id=author_id)
        if status:
            qs = qs.filter(status=status)
        if platform_type:
            qs = qs.filter(platform_type=platform_type)
        if category:
            qs = qs.filter(category__slug=category)
        if search:
            qs = qs.filter(title__icontains=search)
        if is_ai_generated is not None:
            val = is_ai_generated.lower() == "true"
            qs = qs.filter(is_ai_generated=val)
        return qs

    @staticmethod
    def get_by_id(post_id: str) -> Post:
        try:
            return Post.objects.select_related("author", "category", "rag_instance").prefetch_related(
                "tags", "media", "banner_layouts", "comments"
            ).get(id=post_id, is_deleted=False)
        except Post.DoesNotExist:
            raise PostNotFound(f"Không tìm thấy bài viết với id={post_id}")

    @staticmethod
    def get_versions(post: Post):
        return PostVersion.objects.filter(post=post, is_deleted=False).select_related("changed_by")

    @staticmethod
    def get_comments(post: Post):
        return PostComment.objects.filter(post=post, is_deleted=False).select_related("author")
