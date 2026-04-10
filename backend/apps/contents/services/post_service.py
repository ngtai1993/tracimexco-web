from django.db import transaction

from apps.contents.models import Post, PostVersion, PostComment
from apps.contents.constants import PostStatus
from apps.contents.exceptions import PostNotFound, InvalidStatusTransition


class PostService:

    @staticmethod
    @transaction.atomic
    def create(data: dict, author) -> Post:
        """Tạo bài viết mới — tự động tạo PostVersion đầu tiên."""
        tags = data.pop("tags", [])
        post = Post(author=author, **data)
        post.full_clean()
        post.save()
        if tags:
            post.tags.set(tags)
        PostVersion.objects.create(
            post=post,
            version_number=1,
            title=post.title,
            content=post.content,
            changed_by=author,
        )
        return post

    @staticmethod
    @transaction.atomic
    def update(post: Post, data: dict, changed_by) -> Post:
        """Cập nhật bài viết — lưu phiên bản cũ vào PostVersion trước khi ghi đè."""
        tags = data.pop("tags", None)
        latest_version = post.versions.first()
        next_version_number = (latest_version.version_number + 1) if latest_version else 2
        PostVersion.objects.create(
            post=post,
            version_number=next_version_number,
            title=post.title,
            content=post.content,
            changed_by=changed_by,
        )
        for field, value in data.items():
            setattr(post, field, value)
        post.full_clean()
        post.save()
        if tags is not None:
            post.tags.set(tags)
        return post

    @staticmethod
    @transaction.atomic
    def duplicate(post: Post, platform_type: str, author) -> Post:
        """Nhân bản bài viết sang nền tảng khác."""
        new_post = Post(
            title=f"{post.title} (copy)",
            content=post.content,
            hashtags=list(post.hashtags),
            platform_type=platform_type,
            status=PostStatus.DRAFT,
            author=author,
            category=post.category,
            rag_instance=post.rag_instance,
            is_ai_generated=post.is_ai_generated,
        )
        new_post.save()
        new_post.tags.set(post.tags.all())
        PostVersion.objects.create(
            post=new_post,
            version_number=1,
            title=new_post.title,
            content=new_post.content,
            changed_by=author,
        )
        return new_post

    @staticmethod
    def submit_review(post: Post) -> Post:
        """Nộp bài để review (draft → review)."""
        if post.status != PostStatus.DRAFT:
            raise InvalidStatusTransition(
                "Chỉ bài viết ở trạng thái Draft mới có thể nộp review."
            )
        post.status = PostStatus.REVIEW
        post.save(update_fields=["status", "updated_at"])
        return post

    @staticmethod
    def approve(post: Post) -> Post:
        """Duyệt bài (review → approved)."""
        if post.status != PostStatus.REVIEW:
            raise InvalidStatusTransition(
                "Chỉ bài viết đang ở trạng thái Review mới có thể duyệt."
            )
        post.status = PostStatus.APPROVED
        post.save(update_fields=["status", "updated_at"])
        return post

    @staticmethod
    @transaction.atomic
    def reject(post: Post, reason: str, rejector) -> Post:
        """Trả bài về draft kèm lý do (review → draft)."""
        if post.status != PostStatus.REVIEW:
            raise InvalidStatusTransition(
                "Chỉ bài viết đang ở trạng thái Review mới có thể trả về."
            )
        post.status = PostStatus.DRAFT
        post.save(update_fields=["status", "updated_at"])
        PostComment.objects.create(
            post=post,
            author=rejector,
            content=f"[Rejected] {reason}",
        )
        return post

    @staticmethod
    def soft_delete(post: Post, user) -> None:
        """Soft delete bài viết — chỉ được xóa khi draft hoặc user là admin."""
        if post.status in [PostStatus.SCHEDULED, PostStatus.PUBLISHED]:
            raise InvalidStatusTransition(
                "Không thể xóa bài viết đang lên lịch hoặc đã được đăng."
            )
        if post.status != PostStatus.DRAFT and not user.is_staff:
            raise InvalidStatusTransition(
                "Chỉ Admin mới có thể xóa bài viết không ở trạng thái Draft."
            )
        post.soft_delete()
