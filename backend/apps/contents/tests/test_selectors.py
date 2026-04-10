"""
Unit tests cho selectors của contents app:
PostSelector, TaxonomySelector
"""

from django.test import TestCase

from apps.contents.constants import PostStatus, PlatformType
from apps.contents.exceptions import PostNotFound, CategoryNotFound, TagNotFound
from apps.contents.selectors import PostSelector, TaxonomySelector

from .factories import (
    CategoryFactory,
    PostFactory,
    PostVersionFactory,
    PostCommentFactory,
    TagFactory,
    UserFactory,
)


# ---------------------------------------------------------------------------
# PostSelector
# ---------------------------------------------------------------------------

class PostSelectorGetListTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()

    def test_returns_only_non_deleted_posts(self):
        active = PostFactory(author=self.user)
        deleted = PostFactory(author=self.user)
        deleted.soft_delete()

        qs = PostSelector.get_list()
        self.assertIn(active, qs)
        self.assertNotIn(deleted, qs)

    def test_filter_by_author_id(self):
        my_post = PostFactory(author=self.user)
        other_post = PostFactory(author=self.other_user)

        qs = PostSelector.get_list(author_id=str(self.user.id))
        self.assertIn(my_post, qs)
        self.assertNotIn(other_post, qs)

    def test_filter_by_status(self):
        draft = PostFactory(author=self.user, status=PostStatus.DRAFT)
        review = PostFactory(author=self.user, status=PostStatus.REVIEW)

        qs = PostSelector.get_list(status=PostStatus.DRAFT)
        self.assertIn(draft, qs)
        self.assertNotIn(review, qs)

    def test_filter_by_platform_type(self):
        fb_post = PostFactory(author=self.user, platform_type=PlatformType.FACEBOOK)
        zalo_post = PostFactory(author=self.user, platform_type=PlatformType.ZALO)

        qs = PostSelector.get_list(platform_type=PlatformType.FACEBOOK)
        self.assertIn(fb_post, qs)
        self.assertNotIn(zalo_post, qs)

    def test_filter_by_category_slug(self):
        cat = CategoryFactory(slug="promo")
        cat_post = PostFactory(author=self.user, category=cat)
        other_post = PostFactory(author=self.user)

        qs = PostSelector.get_list(category="promo")
        self.assertIn(cat_post, qs)
        self.assertNotIn(other_post, qs)

    def test_filter_by_search_title(self):
        matching = PostFactory(author=self.user, title="Flash Sale Campaign")
        not_matching = PostFactory(author=self.user, title="Regular Post")

        qs = PostSelector.get_list(search="Flash Sale")
        self.assertIn(matching, qs)
        self.assertNotIn(not_matching, qs)

    def test_filter_by_is_ai_generated_true(self):
        ai_post = PostFactory(author=self.user, is_ai_generated=True)
        manual_post = PostFactory(author=self.user, is_ai_generated=False)

        qs = PostSelector.get_list(is_ai_generated="true")
        self.assertIn(ai_post, qs)
        self.assertNotIn(manual_post, qs)

    def test_filter_by_is_ai_generated_false(self):
        ai_post = PostFactory(author=self.user, is_ai_generated=True)
        manual_post = PostFactory(author=self.user, is_ai_generated=False)

        qs = PostSelector.get_list(is_ai_generated="false")
        self.assertIn(manual_post, qs)
        self.assertNotIn(ai_post, qs)

    def test_no_filters_returns_all_active(self):
        p1 = PostFactory(author=self.user)
        p2 = PostFactory(author=self.other_user)

        qs = PostSelector.get_list()
        self.assertIn(p1, qs)
        self.assertIn(p2, qs)


class PostSelectorGetByIdTest(TestCase):

    def test_returns_post_by_id(self):
        post = PostFactory()
        result = PostSelector.get_by_id(str(post.id))
        self.assertEqual(result, post)

    def test_raises_post_not_found_for_missing_id(self):
        import uuid
        with self.assertRaises(PostNotFound):
            PostSelector.get_by_id(str(uuid.uuid4()))

    def test_raises_post_not_found_for_deleted_post(self):
        post = PostFactory()
        post.soft_delete()
        with self.assertRaises(PostNotFound):
            PostSelector.get_by_id(str(post.id))


class PostSelectorGetVersionsTest(TestCase):

    def test_returns_versions_for_post(self):
        post = PostFactory()
        v1 = PostVersionFactory(post=post, version_number=1)
        v2 = PostVersionFactory(post=post, version_number=2)
        versions = list(PostSelector.get_versions(post))
        self.assertIn(v1, versions)
        self.assertIn(v2, versions)

    def test_excludes_deleted_versions(self):
        post = PostFactory()
        v1 = PostVersionFactory(post=post, version_number=1)
        v1.soft_delete()
        versions = list(PostSelector.get_versions(post))
        self.assertNotIn(v1, versions)


class PostSelectorGetCommentsTest(TestCase):

    def test_returns_comments_for_post(self):
        post = PostFactory()
        comment = PostCommentFactory(post=post)
        comments = list(PostSelector.get_comments(post))
        self.assertIn(comment, comments)

    def test_excludes_deleted_comments(self):
        post = PostFactory()
        comment = PostCommentFactory(post=post)
        comment.soft_delete()
        comments = list(PostSelector.get_comments(post))
        self.assertNotIn(comment, comments)


# ---------------------------------------------------------------------------
# TaxonomySelector
# ---------------------------------------------------------------------------

class TaxonomySelectorCategoryTest(TestCase):

    def test_get_root_categories_excludes_children(self):
        parent = CategoryFactory(name="Parent")
        child = CategoryFactory(name="Child", parent=parent)

        roots = list(TaxonomySelector.get_root_categories())
        self.assertIn(parent, roots)
        self.assertNotIn(child, roots)

    def test_get_root_categories_excludes_deleted(self):
        cat = CategoryFactory()
        cat.soft_delete()
        roots = list(TaxonomySelector.get_root_categories())
        self.assertNotIn(cat, roots)

    def test_get_all_categories_returns_all(self):
        parent = CategoryFactory()
        child = CategoryFactory(parent=parent)
        all_cats = list(TaxonomySelector.get_all_categories())
        self.assertIn(parent, all_cats)
        self.assertIn(child, all_cats)

    def test_get_all_categories_excludes_deleted(self):
        cat = CategoryFactory()
        cat.soft_delete()
        all_cats = list(TaxonomySelector.get_all_categories())
        self.assertNotIn(cat, all_cats)

    def test_get_category_by_slug_returns_category(self):
        cat = CategoryFactory(slug="promo")
        result = TaxonomySelector.get_category_by_slug("promo")
        self.assertEqual(result, cat)

    def test_get_category_by_slug_raises_not_found(self):
        with self.assertRaises(CategoryNotFound):
            TaxonomySelector.get_category_by_slug("nonexistent-slug")

    def test_get_category_by_slug_raises_for_deleted(self):
        cat = CategoryFactory(slug="deleted-cat")
        cat.soft_delete()
        with self.assertRaises(CategoryNotFound):
            TaxonomySelector.get_category_by_slug("deleted-cat")


class TaxonomySelectorTagTest(TestCase):

    def test_get_tags_returns_all_active(self):
        t1 = TagFactory(name="Python")
        t2 = TagFactory(name="Django")
        tags = list(TaxonomySelector.get_tags())
        self.assertIn(t1, tags)
        self.assertIn(t2, tags)

    def test_get_tags_excludes_deleted(self):
        tag = TagFactory()
        tag.soft_delete()
        tags = list(TaxonomySelector.get_tags())
        self.assertNotIn(tag, tags)

    def test_get_tags_search_filter(self):
        matching = TagFactory(name="Python Framework")
        not_matching = TagFactory(name="JavaScript")

        tags = list(TaxonomySelector.get_tags(search="Python"))
        self.assertIn(matching, tags)
        self.assertNotIn(not_matching, tags)

    def test_get_tag_by_id_returns_tag(self):
        tag = TagFactory()
        result = TaxonomySelector.get_tag_by_id(str(tag.id))
        self.assertEqual(result, tag)

    def test_get_tag_by_id_raises_not_found(self):
        import uuid
        with self.assertRaises(TagNotFound):
            TaxonomySelector.get_tag_by_id(str(uuid.uuid4()))

    def test_get_tag_by_id_raises_for_deleted(self):
        tag = TagFactory()
        tag.soft_delete()
        with self.assertRaises(TagNotFound):
            TaxonomySelector.get_tag_by_id(str(tag.id))
