"""
API integration tests cho contents app endpoints:
Posts, Categories, Tags, BannerLayouts
"""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from apps.contents.constants import PostStatus, PlatformType
from apps.contents.models import Post, PostVersion, PostComment, BannerLayout, Category, Tag

from .factories import (
    AdminUserFactory,
    BannerLayoutFactory,
    CategoryFactory,
    PostFactory,
    PostCommentFactory,
    PostVersionFactory,
    TagFactory,
    UserFactory,
    LayoutTemplateFactory,
    PostTemplateFactory,
)


class BaseAPITestCase(APITestCase):
    """Base class dùng chung — tự xử lý authentication."""

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.admin = AdminUserFactory()

    def authenticate(self, user=None):
        self.client.force_authenticate(user=user or self.user)

    def authenticate_admin(self):
        self.client.force_authenticate(user=self.admin)


# ---------------------------------------------------------------------------
# POST LIST / CREATE — GET|POST /api/v1/contents/posts/
# ---------------------------------------------------------------------------

class PostListCreateAPITest(BaseAPITestCase):

    def setUp(self):
        super().setUp()
        self.url = reverse("contents:post-list")

    # --- GET ---

    def test_unauthenticated_get_returns_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_sees_only_own_posts(self):
        self.authenticate()
        my_post = PostFactory(author=self.user)
        other_post = PostFactory()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in response.data["data"]["results"]]
        self.assertIn(str(my_post.id), ids)
        self.assertNotIn(str(other_post.id), ids)

    def test_staff_sees_all_posts(self):
        self.authenticate_admin()
        post1 = PostFactory(author=self.user)
        post2 = PostFactory()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in response.data["data"]["results"]]
        self.assertIn(str(post1.id), ids)
        self.assertIn(str(post2.id), ids)

    def test_filter_by_status(self):
        self.authenticate_admin()
        draft = PostFactory(status=PostStatus.DRAFT)
        review = PostFactory(status=PostStatus.REVIEW)

        response = self.client.get(self.url, {"status": PostStatus.DRAFT})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in response.data["data"]["results"]]
        self.assertIn(str(draft.id), ids)
        self.assertNotIn(str(review.id), ids)

    def test_filter_by_platform_type(self):
        self.authenticate_admin()
        fb = PostFactory(platform_type=PlatformType.FACEBOOK)
        zalo = PostFactory(platform_type=PlatformType.ZALO)

        response = self.client.get(self.url, {"platform_type": PlatformType.FACEBOOK})

        ids = [item["id"] for item in response.data["data"]["results"]]
        self.assertIn(str(fb.id), ids)
        self.assertNotIn(str(zalo.id), ids)

    def test_search_filter(self):
        self.authenticate_admin()
        matching = PostFactory(title="Flash Sale Campaign")
        not_matching = PostFactory(title="Regular Update")

        response = self.client.get(self.url, {"search": "Flash"})

        ids = [item["id"] for item in response.data["data"]["results"]]
        self.assertIn(str(matching.id), ids)
        self.assertNotIn(str(not_matching.id), ids)

    def test_response_has_pagination_fields(self):
        self.authenticate()
        response = self.client.get(self.url)
        self.assertIn("count", response.data["data"])
        self.assertIn("results", response.data["data"])

    # --- POST ---

    def test_unauthenticated_post_returns_401(self):
        payload = {
            "title": "Test",
            "content": "Content",
            "platform_type": PlatformType.FACEBOOK,
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_post_returns_201(self):
        self.authenticate()
        payload = {
            "title": "New Post",
            "content": "Post content here.",
            "platform_type": PlatformType.FACEBOOK,
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data["data"])

    def test_create_post_default_status_is_draft(self):
        self.authenticate()
        payload = {
            "title": "Draft Post",
            "content": "Content.",
            "platform_type": PlatformType.FACEBOOK,
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.data["data"]["status"], PostStatus.DRAFT)

    def test_create_post_missing_title_returns_400(self):
        self.authenticate()
        response = self.client.post(self.url, {"content": "x", "platform_type": "facebook"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_post_missing_platform_type_returns_400(self):
        self.authenticate()
        response = self.client.post(self.url, {"title": "T", "content": "C"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_post_author_is_request_user(self):
        self.authenticate()
        payload = {
            "title": "Author Test",
            "content": "Content.",
            "platform_type": PlatformType.FACEBOOK,
        }
        response = self.client.post(self.url, payload, format="json")
        post_id = response.data["data"]["id"]
        post = Post.objects.get(id=post_id)
        self.assertEqual(post.author, self.user)

    def test_create_post_creates_version_1(self):
        self.authenticate()
        payload = {
            "title": "Versioned Post",
            "content": "Content.",
            "platform_type": PlatformType.FACEBOOK,
        }
        response = self.client.post(self.url, payload, format="json")
        post_id = response.data["data"]["id"]
        self.assertEqual(PostVersion.objects.filter(post_id=post_id).count(), 1)


# ---------------------------------------------------------------------------
# POST DETAIL — GET|PATCH|DELETE /api/v1/contents/posts/{post_id}/
# ---------------------------------------------------------------------------

class PostDetailAPITest(BaseAPITestCase):

    def setUp(self):
        super().setUp()
        self.post = PostFactory(author=self.user, status=PostStatus.DRAFT)
        self.url = reverse("contents:post-detail", kwargs={"post_id": self.post.id})

    # --- GET ---

    def test_unauthenticated_get_returns_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_own_post_returns_200(self):
        self.authenticate()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["id"], str(self.post.id))

    def test_get_nonexistent_post_returns_404(self):
        import uuid
        self.authenticate()
        url = reverse("contents:post-detail", kwargs={"post_id": uuid.uuid4()})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # --- PATCH ---

    def test_patch_own_post_updates_title(self):
        self.authenticate()
        response = self.client.patch(self.url, {"title": "Updated Title"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Updated Title")

    def test_patch_creates_new_version(self):
        self.authenticate()
        initial_versions = PostVersion.objects.filter(post=self.post).count()
        self.client.patch(self.url, {"title": "New Title"}, format="json")
        self.assertGreater(PostVersion.objects.filter(post=self.post).count(), initial_versions)

    def test_patch_other_users_post_returns_403(self):
        other_post = PostFactory(status=PostStatus.DRAFT)
        url = reverse("contents:post-detail", kwargs={"post_id": other_post.id})
        self.authenticate()
        response = self.client.patch(url, {"title": "Hack"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_patch_any_post(self):
        self.authenticate_admin()
        response = self.client.patch(self.url, {"title": "Admin Edit"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # --- DELETE ---

    def test_delete_own_draft_post_returns_204(self):
        self.authenticate()
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.post.refresh_from_db()
        self.assertTrue(self.post.is_deleted)

    def test_cannot_delete_scheduled_post(self):
        post = PostFactory(author=self.user, status=PostStatus.SCHEDULED)
        url = reverse("contents:post-detail", kwargs={"post_id": post.id})
        self.authenticate()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_nonexistent_post_returns_404(self):
        import uuid
        self.authenticate()
        url = reverse("contents:post-detail", kwargs={"post_id": uuid.uuid4()})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# ---------------------------------------------------------------------------
# POST STATUS TRANSITIONS
# ---------------------------------------------------------------------------

class PostSubmitReviewAPITest(BaseAPITestCase):

    def test_author_can_submit_draft_for_review(self):
        post = PostFactory(author=self.user, status=PostStatus.DRAFT)
        url = reverse("contents:post-submit-review", kwargs={"post_id": post.id})
        self.authenticate()
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        post.refresh_from_db()
        self.assertEqual(post.status, PostStatus.REVIEW)

    def test_non_author_cannot_submit_review(self):
        other_post = PostFactory(status=PostStatus.DRAFT)
        url = reverse("contents:post-submit-review", kwargs={"post_id": other_post.id})
        self.authenticate()
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_submit_already_review_post_returns_400(self):
        post = PostFactory(author=self.user, status=PostStatus.REVIEW)
        url = reverse("contents:post-submit-review", kwargs={"post_id": post.id})
        self.authenticate()
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PostApproveAPITest(BaseAPITestCase):

    def test_admin_can_approve_review_post(self):
        post = PostFactory(status=PostStatus.REVIEW)
        url = reverse("contents:post-approve", kwargs={"post_id": post.id})
        self.authenticate_admin()
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        post.refresh_from_db()
        self.assertEqual(post.status, PostStatus.APPROVED)

    def test_non_admin_cannot_approve(self):
        post = PostFactory(status=PostStatus.REVIEW)
        url = reverse("contents:post-approve", kwargs={"post_id": post.id})
        self.authenticate()
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_approve_draft_returns_400(self):
        post = PostFactory(status=PostStatus.DRAFT)
        url = reverse("contents:post-approve", kwargs={"post_id": post.id})
        self.authenticate_admin()
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PostRejectAPITest(BaseAPITestCase):

    def test_admin_can_reject_review_post(self):
        post = PostFactory(status=PostStatus.REVIEW)
        url = reverse("contents:post-reject", kwargs={"post_id": post.id})
        self.authenticate_admin()
        response = self.client.post(url, {"reason": "Needs more detail."}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        post.refresh_from_db()
        self.assertEqual(post.status, PostStatus.DRAFT)

    def test_reject_without_reason_returns_400(self):
        post = PostFactory(status=PostStatus.REVIEW)
        url = reverse("contents:post-reject", kwargs={"post_id": post.id})
        self.authenticate_admin()
        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reject_creates_comment(self):
        post = PostFactory(status=PostStatus.REVIEW)
        url = reverse("contents:post-reject", kwargs={"post_id": post.id})
        self.authenticate_admin()
        self.client.post(url, {"reason": "Rewrite needed."}, format="json")
        comment = PostComment.objects.filter(post=post).last()
        self.assertIsNotNone(comment)
        self.assertIn("Rewrite needed.", comment.content)

    def test_non_admin_cannot_reject(self):
        post = PostFactory(status=PostStatus.REVIEW)
        url = reverse("contents:post-reject", kwargs={"post_id": post.id})
        self.authenticate()
        response = self.client.post(url, {"reason": "nope"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# ---------------------------------------------------------------------------
# POST DUPLICATE
# ---------------------------------------------------------------------------

class PostDuplicateAPITest(BaseAPITestCase):

    def test_duplicate_post_returns_201(self):
        post = PostFactory(author=self.user)
        url = reverse("contents:post-duplicate", kwargs={"post_id": post.id})
        self.authenticate()
        response = self.client.post(url, {"platform_type": PlatformType.ZALO}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(response.data["data"]["id"], str(post.id))

    def test_duplicate_creates_draft_status(self):
        post = PostFactory(author=self.user, status=PostStatus.APPROVED)
        url = reverse("contents:post-duplicate", kwargs={"post_id": post.id})
        self.authenticate()
        response = self.client.post(url, {"platform_type": PlatformType.ZALO}, format="json")
        self.assertEqual(response.data["data"]["status"], PostStatus.DRAFT)

    def test_duplicate_nonexistent_post_returns_404(self):
        import uuid
        url = reverse("contents:post-duplicate", kwargs={"post_id": uuid.uuid4()})
        self.authenticate()
        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# ---------------------------------------------------------------------------
# POST VERSIONS
# ---------------------------------------------------------------------------

class PostVersionListAPITest(BaseAPITestCase):

    def test_get_versions_returns_200(self):
        post = PostFactory(author=self.user)
        PostVersionFactory(post=post, version_number=1)
        PostVersionFactory(post=post, version_number=2)
        url = reverse("contents:post-versions", kwargs={"post_id": post.id})
        self.authenticate()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 2)

    def test_unauthenticated_returns_401(self):
        post = PostFactory()
        url = reverse("contents:post-versions", kwargs={"post_id": post.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# ---------------------------------------------------------------------------
# COMMENTS
# ---------------------------------------------------------------------------

class PostCommentAPITest(BaseAPITestCase):

    def setUp(self):
        super().setUp()
        self.post = PostFactory(author=self.user)
        self.url = reverse("contents:post-comments", kwargs={"post_id": self.post.id})

    def test_get_comments_returns_200(self):
        PostCommentFactory(post=self.post)
        self.authenticate()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)

    def test_post_comment_returns_201(self):
        self.authenticate()
        response = self.client.post(self.url, {"content": "Great post!"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PostComment.objects.filter(post=self.post).count(), 1)

    def test_post_comment_empty_content_returns_400(self):
        self.authenticate()
        response = self.client.post(self.url, {"content": ""}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_cannot_comment(self):
        response = self.client.post(self.url, {"content": "Test"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# ---------------------------------------------------------------------------
# CATEGORIES
# ---------------------------------------------------------------------------

class CategoryListCreateAPITest(BaseAPITestCase):

    def setUp(self):
        super().setUp()
        self.url = reverse("contents:category-list")

    def test_authenticated_user_can_list_categories(self):
        CategoryFactory()
        self.authenticate()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_cannot_list_categories(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_can_create_category(self):
        self.authenticate_admin()
        response = self.client.post(self.url, {"name": "Marketing", "slug": "marketing"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Category.objects.filter(slug="marketing").exists())

    def test_non_admin_cannot_create_category(self):
        self.authenticate()
        response = self.client.post(self.url, {"name": "Marketing"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_category_without_slug_auto_generates(self):
        self.authenticate_admin()
        response = self.client.post(self.url, {"name": "Social Media"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Category.objects.filter(slug="social-media").exists())


class CategoryDetailAPITest(BaseAPITestCase):

    def test_admin_can_patch_category(self):
        cat = CategoryFactory(slug="tech")
        url = reverse("contents:category-detail", kwargs={"slug": "tech"})
        self.authenticate_admin()
        response = self.client.patch(url, {"name": "Technology"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_delete_empty_category(self):
        cat = CategoryFactory(slug="empty-cat")
        url = reverse("contents:category-detail", kwargs={"slug": "empty-cat"})
        self.authenticate_admin()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        cat.refresh_from_db()
        self.assertTrue(cat.is_deleted)

    def test_cannot_delete_category_with_children(self):
        parent = CategoryFactory(slug="parent-cat")
        CategoryFactory(parent=parent)
        url = reverse("contents:category-detail", kwargs={"slug": "parent-cat"})
        self.authenticate_admin()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_delete_category_with_posts(self):
        cat = CategoryFactory(slug="cat-with-posts")
        PostFactory(category=cat)
        url = reverse("contents:category-detail", kwargs={"slug": "cat-with-posts"})
        self.authenticate_admin()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_admin_cannot_delete_category(self):
        cat = CategoryFactory(slug="my-cat")
        url = reverse("contents:category-detail", kwargs={"slug": "my-cat"})
        self.authenticate()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_nonexistent_category_returns_404(self):
        url = reverse("contents:category-detail", kwargs={"slug": "no-such-cat"})
        self.authenticate_admin()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# ---------------------------------------------------------------------------
# TAGS
# ---------------------------------------------------------------------------

class TagListCreateAPITest(BaseAPITestCase):

    def setUp(self):
        super().setUp()
        self.url = reverse("contents:tag-list")

    def test_authenticated_user_can_list_tags(self):
        TagFactory()
        self.authenticate()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["data"]), 1)

    def test_search_filter_returns_matching_tags(self):
        TagFactory(name="Python Backend")
        TagFactory(name="JavaScript Frontend")
        self.authenticate()
        response = self.client.get(self.url, {"search": "Python"})
        names = [t["name"] for t in response.data["data"]]
        self.assertIn("Python Backend", names)
        self.assertNotIn("JavaScript Frontend", names)

    def test_authenticated_user_can_create_tag(self):
        self.authenticate()
        response = self.client.post(self.url, {"name": "django"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Tag.objects.filter(name="django").exists())

    def test_unauthenticated_cannot_create_tag(self):
        response = self.client.post(self.url, {"name": "test"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# ---------------------------------------------------------------------------
# BANNER LAYOUTS
# ---------------------------------------------------------------------------

class BannerLayoutAPITest(BaseAPITestCase):

    def setUp(self):
        super().setUp()
        self.post = PostFactory(author=self.user)
        self.list_url = reverse("contents:banner-layout-list", kwargs={"post_id": self.post.id})

    def test_list_banner_layouts_returns_200(self):
        BannerLayoutFactory(post=self.post, variant_index=1)
        self.authenticate()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)

    def test_unauthenticated_cannot_list_banner_layouts(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_nonexistent_post_returns_404(self):
        import uuid
        url = reverse("contents:banner-layout-list", kwargs={"post_id": uuid.uuid4()})
        self.authenticate()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class BannerLayoutApproveAPITest(BaseAPITestCase):

    def test_admin_can_approve_layout(self):
        post = PostFactory()
        layout = BannerLayoutFactory(post=post, variant_index=1)
        url = reverse(
            "contents:banner-layout-approve",
            kwargs={"post_id": post.id, "layout_id": layout.id},
        )
        self.authenticate_admin()
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        layout.refresh_from_db()
        self.assertTrue(layout.is_approved)

    def test_non_admin_cannot_approve_layout(self):
        post = PostFactory()
        layout = BannerLayoutFactory(post=post, variant_index=1)
        url = reverse(
            "contents:banner-layout-approve",
            kwargs={"post_id": post.id, "layout_id": layout.id},
        )
        self.authenticate()
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# ---------------------------------------------------------------------------
# LAYOUT TEMPLATES
# ---------------------------------------------------------------------------

class LayoutTemplateAPITest(BaseAPITestCase):

    def setUp(self):
        super().setUp()
        self.url = reverse("contents:layout-template-list")

    def test_authenticated_user_can_list_templates(self):
        LayoutTemplateFactory()
        self.authenticate()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["data"]), 1)

    def test_admin_can_create_layout_template(self):
        self.authenticate_admin()
        payload = {
            "name": "Bold Layout",
            "platform_type": PlatformType.FACEBOOK,
            "layout_json": {"title": "Test", "layout_style": "bold"},
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_non_admin_cannot_create_layout_template(self):
        self.authenticate()
        payload = {
            "name": "Minimal",
            "platform_type": PlatformType.FACEBOOK,
            "layout_json": {},
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_by_platform_type(self):
        LayoutTemplateFactory(platform_type=PlatformType.FACEBOOK)
        LayoutTemplateFactory(platform_type=PlatformType.TIKTOK)
        self.authenticate()
        response = self.client.get(self.url, {"platform_type": PlatformType.FACEBOOK})
        for item in response.data["data"]:
            self.assertEqual(item["platform_type"], PlatformType.FACEBOOK)


# ---------------------------------------------------------------------------
# POST TEMPLATES
# ---------------------------------------------------------------------------

class PostTemplateAPITest(BaseAPITestCase):

    def setUp(self):
        super().setUp()
        self.url = reverse("contents:post-template-list")

    def test_admin_can_create_post_template(self):
        self.authenticate_admin()
        payload = {
            "name": "Sale Template",
            "platform_type": PlatformType.FACEBOOK,
            "content_template": "Check out our {product} today!",
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_use_template_creates_draft_post(self):
        template = PostTemplateFactory()
        url = reverse("contents:post-template-use", kwargs={"template_id": template.id})
        self.authenticate()
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["data"]["status"], PostStatus.DRAFT)

    def test_use_nonexistent_template_returns_404(self):
        import uuid
        url = reverse("contents:post-template-use", kwargs={"template_id": uuid.uuid4()})
        self.authenticate()
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
