"""
Unit tests cho services tầng business logic của contents app:
PostService, BannerLayoutService
"""

from unittest.mock import patch, MagicMock

from django.test import TestCase

from apps.contents.constants import PostStatus, PlatformType
from apps.contents.exceptions import InvalidStatusTransition
from apps.contents.models import Post, PostVersion, PostComment, BannerLayout
from apps.contents.services import PostService, BannerLayoutService

from .factories import (
    AdminUserFactory,
    CategoryFactory,
    PostFactory,
    TagFactory,
    UserFactory,
    BannerLayoutFactory,
)


# ---------------------------------------------------------------------------
# PostService.create
# ---------------------------------------------------------------------------

class PostServiceCreateTest(TestCase):

    def setUp(self):
        self.author = UserFactory()

    def test_create_returns_post_with_correct_fields(self):
        data = {
            "title": "New Post",
            "content": "Some content.",
            "platform_type": PlatformType.FACEBOOK,
        }
        post = PostService.create(data, author=self.author)
        self.assertIsInstance(post, Post)
        self.assertEqual(post.title, "New Post")
        self.assertEqual(post.author, self.author)
        self.assertEqual(post.status, PostStatus.DRAFT)

    def test_create_auto_creates_version_1(self):
        data = {
            "title": "Version Test Post",
            "content": "Content here.",
            "platform_type": PlatformType.FACEBOOK,
        }
        post = PostService.create(data, author=self.author)
        self.assertEqual(post.versions.count(), 1)
        self.assertEqual(post.versions.first().version_number, 1)

    def test_create_sets_tags(self):
        tag1 = TagFactory()
        tag2 = TagFactory()
        data = {
            "title": "Tagged Post",
            "content": "Content.",
            "platform_type": PlatformType.FACEBOOK,
            "tags": [tag1, tag2],
        }
        post = PostService.create(data, author=self.author)
        self.assertEqual(post.tags.count(), 2)

    def test_create_without_tags_saves_cleanly(self):
        data = {
            "title": "No Tags Post",
            "content": "Content.",
            "platform_type": PlatformType.FACEBOOK,
        }
        post = PostService.create(data, author=self.author)
        self.assertEqual(post.tags.count(), 0)

    def test_create_with_category(self):
        cat = CategoryFactory()
        data = {
            "title": "Categorised Post",
            "content": "Content.",
            "platform_type": PlatformType.FACEBOOK,
            "category": cat,
        }
        post = PostService.create(data, author=self.author)
        self.assertEqual(post.category, cat)


# ---------------------------------------------------------------------------
# PostService.update
# ---------------------------------------------------------------------------

class PostServiceUpdateTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.post = PostFactory(author=self.user, title="Old Title", content="Old content.")
        # Ensure version 1 exists
        PostVersion.objects.create(
            post=self.post, version_number=1,
            title=self.post.title, content=self.post.content, changed_by=self.user
        )

    def test_update_changes_title(self):
        PostService.update(self.post, {"title": "New Title"}, changed_by=self.user)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "New Title")

    def test_update_creates_new_version(self):
        initial_count = self.post.versions.count()
        PostService.update(self.post, {"title": "New Title"}, changed_by=self.user)
        self.assertEqual(self.post.versions.count(), initial_count + 1)

    def test_update_version_preserves_old_content(self):
        old_title = self.post.title
        PostService.update(self.post, {"title": "Updated"}, changed_by=self.user)
        versions = list(self.post.versions.order_by("version_number"))
        # version 1 still has the old title
        self.assertEqual(versions[0].title, old_title)

    def test_update_sets_tags_when_provided(self):
        tag = TagFactory()
        PostService.update(self.post, {"tags": [tag]}, changed_by=self.user)
        self.assertIn(tag, self.post.tags.all())

    def test_update_clears_tags_when_empty_list(self):
        tag = TagFactory()
        self.post.tags.set([tag])
        PostService.update(self.post, {"tags": []}, changed_by=self.user)
        self.assertEqual(self.post.tags.count(), 0)


# ---------------------------------------------------------------------------
# PostService.duplicate
# ---------------------------------------------------------------------------

class PostServiceDuplicateTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.post = PostFactory(
            author=self.user,
            title="Original Post",
            platform_type=PlatformType.FACEBOOK,
            hashtags=["#test"],
        )

    def test_duplicate_creates_new_post(self):
        new_post = PostService.duplicate(self.post, platform_type=PlatformType.ZALO, author=self.user)
        self.assertNotEqual(new_post.id, self.post.id)

    def test_duplicate_copies_content(self):
        new_post = PostService.duplicate(self.post, platform_type=PlatformType.ZALO, author=self.user)
        self.assertEqual(new_post.content, self.post.content)

    def test_duplicate_title_has_copy_suffix(self):
        new_post = PostService.duplicate(self.post, platform_type=PlatformType.ZALO, author=self.user)
        self.assertIn("copy", new_post.title.lower())

    def test_duplicate_new_status_is_draft(self):
        new_post = PostService.duplicate(self.post, platform_type=PlatformType.ZALO, author=self.user)
        self.assertEqual(new_post.status, PostStatus.DRAFT)

    def test_duplicate_creates_initial_version(self):
        new_post = PostService.duplicate(self.post, platform_type=PlatformType.ZALO, author=self.user)
        self.assertEqual(new_post.versions.count(), 1)

    def test_duplicate_copies_tags(self):
        tag = TagFactory()
        self.post.tags.set([tag])
        new_post = PostService.duplicate(self.post, platform_type=PlatformType.ZALO, author=self.user)
        self.assertIn(tag, new_post.tags.all())


# ---------------------------------------------------------------------------
# PostService.submit_review
# ---------------------------------------------------------------------------

class PostServiceSubmitReviewTest(TestCase):

    def test_submit_draft_changes_status_to_review(self):
        post = PostFactory(status=PostStatus.DRAFT)
        PostService.submit_review(post)
        post.refresh_from_db()
        self.assertEqual(post.status, PostStatus.REVIEW)

    def test_submit_non_draft_raises_invalid_transition(self):
        post = PostFactory(status=PostStatus.REVIEW)
        with self.assertRaises(InvalidStatusTransition):
            PostService.submit_review(post)

    def test_submit_approved_post_raises_invalid_transition(self):
        post = PostFactory(status=PostStatus.APPROVED)
        with self.assertRaises(InvalidStatusTransition):
            PostService.submit_review(post)


# ---------------------------------------------------------------------------
# PostService.approve
# ---------------------------------------------------------------------------

class PostServiceApproveTest(TestCase):

    def test_approve_review_post_changes_status(self):
        post = PostFactory(status=PostStatus.REVIEW)
        PostService.approve(post)
        post.refresh_from_db()
        self.assertEqual(post.status, PostStatus.APPROVED)

    def test_approve_draft_raises_invalid_transition(self):
        post = PostFactory(status=PostStatus.DRAFT)
        with self.assertRaises(InvalidStatusTransition):
            PostService.approve(post)


# ---------------------------------------------------------------------------
# PostService.reject
# ---------------------------------------------------------------------------

class PostServiceRejectTest(TestCase):

    def setUp(self):
        self.admin = UserFactory(is_staff=True)

    def test_reject_review_post_returns_to_draft(self):
        post = PostFactory(status=PostStatus.REVIEW)
        PostService.reject(post, reason="Needs revision.", rejector=self.admin)
        post.refresh_from_db()
        self.assertEqual(post.status, PostStatus.DRAFT)

    def test_reject_creates_comment_with_reason(self):
        post = PostFactory(status=PostStatus.REVIEW)
        PostService.reject(post, reason="Fix grammar.", rejector=self.admin)
        comment = PostComment.objects.filter(post=post).last()
        self.assertIsNotNone(comment)
        self.assertIn("Fix grammar.", comment.content)
        self.assertIn("[Rejected]", comment.content)

    def test_reject_non_review_post_raises_invalid_transition(self):
        post = PostFactory(status=PostStatus.DRAFT)
        with self.assertRaises(InvalidStatusTransition):
            PostService.reject(post, reason="reason", rejector=self.admin)


# ---------------------------------------------------------------------------
# PostService.soft_delete
# ---------------------------------------------------------------------------

class PostServiceSoftDeleteTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.admin = AdminUserFactory()

    def test_soft_delete_draft_post(self):
        post = PostFactory(status=PostStatus.DRAFT, author=self.user)
        PostService.soft_delete(post, user=self.user)
        post.refresh_from_db()
        self.assertTrue(post.is_deleted)

    def test_cannot_delete_scheduled_post(self):
        post = PostFactory(status=PostStatus.SCHEDULED)
        with self.assertRaises(InvalidStatusTransition):
            PostService.soft_delete(post, user=self.user)

    def test_cannot_delete_published_post(self):
        post = PostFactory(status=PostStatus.PUBLISHED)
        with self.assertRaises(InvalidStatusTransition):
            PostService.soft_delete(post, user=self.user)

    def test_non_draft_post_requires_admin(self):
        post = PostFactory(status=PostStatus.REVIEW)
        with self.assertRaises(InvalidStatusTransition):
            PostService.soft_delete(post, user=self.user)

    def test_admin_can_delete_non_draft_review_post(self):
        post = PostFactory(status=PostStatus.REVIEW)
        PostService.soft_delete(post, user=self.admin)
        post.refresh_from_db()
        self.assertTrue(post.is_deleted)


# ---------------------------------------------------------------------------
# BannerLayoutService.approve
# ---------------------------------------------------------------------------

class BannerLayoutServiceApproveTest(TestCase):

    def setUp(self):
        self.admin = AdminUserFactory()
        self.post = PostFactory()

    def test_approve_sets_is_approved_true(self):
        layout = BannerLayoutFactory(post=self.post, variant_index=1)
        BannerLayoutService.approve(layout, approver=self.admin)
        layout.refresh_from_db()
        self.assertTrue(layout.is_approved)
        self.assertEqual(layout.approved_by, self.admin)

    def test_approve_deactivates_other_layouts_of_same_post(self):
        layout1 = BannerLayoutFactory(post=self.post, variant_index=1, is_approved=True)
        layout2 = BannerLayoutFactory(post=self.post, variant_index=2)
        BannerLayoutService.approve(layout2, approver=self.admin)
        layout1.refresh_from_db()
        self.assertFalse(layout1.is_approved)

    def test_approve_only_one_layout_per_post(self):
        layout1 = BannerLayoutFactory(post=self.post, variant_index=1)
        layout2 = BannerLayoutFactory(post=self.post, variant_index=2)
        BannerLayoutService.approve(layout1, approver=self.admin)
        BannerLayoutService.approve(layout2, approver=self.admin)
        approved_count = BannerLayout.objects.filter(
            post=self.post, is_approved=True, is_deleted=False
        ).count()
        self.assertEqual(approved_count, 1)


# ---------------------------------------------------------------------------
# BannerLayoutService.update
# ---------------------------------------------------------------------------

class BannerLayoutServiceUpdateTest(TestCase):

    def test_update_replaces_layout_json(self):
        layout = BannerLayoutFactory()
        new_json = {"title": "Updated", "layout_style": "bold"}
        BannerLayoutService.update(layout, layout_json=new_json)
        layout.refresh_from_db()
        self.assertEqual(layout.layout_json, new_json)
