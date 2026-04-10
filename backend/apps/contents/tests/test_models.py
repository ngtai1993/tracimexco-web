"""
Unit tests cho contents app models:
Category, Tag, Post, PostVersion, BannerLayout
"""

from django.test import TestCase
from django.db import IntegrityError

from apps.contents.constants import PostStatus, PlatformType
from apps.contents.models import Category, Tag, Post, PostVersion, BannerLayout

from .factories import (
    UserFactory,
    CategoryFactory,
    TagFactory,
    PostFactory,
    PostVersionFactory,
    BannerLayoutFactory,
)


# ---------------------------------------------------------------------------
# Category
# ---------------------------------------------------------------------------

class CategoryModelTest(TestCase):

    def test_str_returns_name(self):
        cat = CategoryFactory(name="Marketing")
        self.assertEqual(str(cat), "Marketing")

    def test_slug_auto_generated_from_name(self):
        cat = Category(name="Social Media")
        cat.save()
        self.assertEqual(cat.slug, "social-media")

    def test_slug_not_overwritten_when_already_set(self):
        cat = CategoryFactory(name="Test Cat", slug="custom-slug")
        self.assertEqual(cat.slug, "custom-slug")

    def test_slug_must_be_unique(self):
        CategoryFactory(slug="unique-slug")
        with self.assertRaises(IntegrityError):
            CategoryFactory(slug="unique-slug")

    def test_parent_child_relationship(self):
        parent = CategoryFactory(name="Parent")
        child = CategoryFactory(name="Child", parent=parent)
        self.assertEqual(child.parent, parent)
        self.assertIn(child, parent.children.all())

    def test_soft_delete_sets_is_deleted_true(self):
        cat = CategoryFactory()
        cat_id = cat.id
        cat.soft_delete()
        cat.refresh_from_db()
        self.assertTrue(cat.is_deleted)
        self.assertTrue(Category.objects.filter(id=cat_id).exists())

    def test_restore_undeletes(self):
        cat = CategoryFactory()
        cat.soft_delete()
        cat.restore()
        cat.refresh_from_db()
        self.assertFalse(cat.is_deleted)

    def test_default_order_is_zero(self):
        cat = CategoryFactory()
        self.assertEqual(cat.order, 0)


# ---------------------------------------------------------------------------
# Tag
# ---------------------------------------------------------------------------

class TagModelTest(TestCase):

    def test_str_returns_name(self):
        tag = TagFactory(name="Django")
        self.assertEqual(str(tag), "Django")

    def test_slug_auto_generated_from_name(self):
        tag = Tag(name="Django REST")
        tag.save()
        self.assertEqual(tag.slug, "django-rest")

    def test_slug_not_overwritten_when_already_set(self):
        tag = TagFactory(name="React", slug="reactjs")
        self.assertEqual(tag.slug, "reactjs")

    def test_name_must_be_unique(self):
        TagFactory(name="unique-tag")
        with self.assertRaises(IntegrityError):
            TagFactory(name="unique-tag")

    def test_slug_must_be_unique(self):
        TagFactory(slug="my-tag")
        with self.assertRaises(IntegrityError):
            TagFactory(slug="my-tag")

    def test_soft_delete(self):
        tag = TagFactory()
        tag.soft_delete()
        tag.refresh_from_db()
        self.assertTrue(tag.is_deleted)


# ---------------------------------------------------------------------------
# Post
# ---------------------------------------------------------------------------

class PostModelTest(TestCase):

    def test_str_returns_title(self):
        post = PostFactory(title="Hello World")
        self.assertEqual(str(post), "Hello World")

    def test_default_status_is_draft(self):
        post = PostFactory()
        self.assertEqual(post.status, PostStatus.DRAFT)

    def test_default_is_ai_generated_false(self):
        post = PostFactory()
        self.assertFalse(post.is_ai_generated)

    def test_post_can_have_tags(self):
        tag1 = TagFactory()
        tag2 = TagFactory()
        post = PostFactory()
        post.tags.set([tag1, tag2])
        self.assertEqual(post.tags.count(), 2)

    def test_post_can_have_category(self):
        cat = CategoryFactory()
        post = PostFactory(category=cat)
        self.assertEqual(post.category, cat)

    def test_soft_delete_does_not_remove_from_db(self):
        post = PostFactory()
        post_id = post.id
        post.soft_delete()
        self.assertTrue(Post.objects.filter(id=post_id).exists())
        post.refresh_from_db()
        self.assertTrue(post.is_deleted)

    def test_restore_after_soft_delete(self):
        post = PostFactory()
        post.soft_delete()
        post.restore()
        post.refresh_from_db()
        self.assertFalse(post.is_deleted)

    def test_post_ordering_is_newest_first(self):
        user = UserFactory()
        post1 = PostFactory(author=user)
        post2 = PostFactory(author=user)
        posts = list(Post.objects.filter(author=user))
        self.assertEqual(posts[0], post2)

    def test_hashtags_default_is_empty_list(self):
        post = PostFactory()
        self.assertEqual(post.hashtags, [])


# ---------------------------------------------------------------------------
# PostVersion
# ---------------------------------------------------------------------------

class PostVersionModelTest(TestCase):

    def test_str_contains_title_and_version(self):
        post = PostFactory(title="My Post")
        version = PostVersionFactory(post=post, version_number=3)
        self.assertIn("My Post", str(version))
        self.assertIn("3", str(version))

    def test_unique_together_post_version_number(self):
        post = PostFactory()
        PostVersionFactory(post=post, version_number=1)
        with self.assertRaises(IntegrityError):
            PostVersionFactory(post=post, version_number=1)

    def test_version_ordering_newest_first(self):
        post = PostFactory()
        v1 = PostVersionFactory(post=post, version_number=1)
        v2 = PostVersionFactory(post=post, version_number=2)
        versions = list(PostVersion.objects.filter(post=post))
        self.assertEqual(versions[0], v2)


# ---------------------------------------------------------------------------
# BannerLayout
# ---------------------------------------------------------------------------

class BannerLayoutModelTest(TestCase):

    def test_str_contains_post_title_and_variant(self):
        post = PostFactory(title="Sale Post")
        layout = BannerLayoutFactory(post=post, variant_index=2)
        self.assertIn("Sale Post", str(layout))
        self.assertIn("2", str(layout))

    def test_default_is_approved_false(self):
        layout = BannerLayoutFactory()
        self.assertFalse(layout.is_approved)

    def test_unique_together_post_variant_index(self):
        post = PostFactory()
        BannerLayoutFactory(post=post, variant_index=1)
        with self.assertRaises(IntegrityError):
            BannerLayoutFactory(post=post, variant_index=1)

    def test_soft_delete(self):
        layout = BannerLayoutFactory()
        layout.soft_delete()
        layout.refresh_from_db()
        self.assertTrue(layout.is_deleted)
