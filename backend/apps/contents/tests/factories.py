import factory
from factory.django import DjangoModelFactory

from apps.contents.constants import (
    PostStatus,
    PlatformType,
    MediaType,
    GenerationType,
    GenerationStatus,
)
from apps.contents.models import (
    Category,
    Tag,
    Post,
    PostMedia,
    PostVersion,
    PostComment,
    PostTemplate,
    LayoutTemplate,
    BannerLayout,
    AIContentGeneration,
)


class UserFactory(DjangoModelFactory):
    """Tạo user test."""

    class Meta:
        model = "users.User"

    email = factory.Sequence(lambda n: f"user{n}@test.com")
    username = factory.Sequence(lambda n: f"user{n}")
    full_name = factory.Sequence(lambda n: f"User {n}")
    is_active = True
    is_staff = False

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.pop("password", "testpass123")
        obj = model_class(**kwargs)
        obj.set_password(password)
        obj.save()
        return obj


class AdminUserFactory(UserFactory):
    is_staff = True
    is_superuser = True


class CategoryFactory(DjangoModelFactory):
    """Tạo category test."""

    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Category {n}")
    slug = factory.Sequence(lambda n: f"category-{n}")
    description = ""
    order = 0
    parent = None


class TagFactory(DjangoModelFactory):
    """Tạo tag test."""

    class Meta:
        model = Tag

    name = factory.Sequence(lambda n: f"tag{n}")
    slug = factory.Sequence(lambda n: f"tag-{n}")


class PostFactory(DjangoModelFactory):
    """Tạo bài viết test."""

    class Meta:
        model = Post

    title = factory.Sequence(lambda n: f"Post Title {n}")
    content = factory.Sequence(lambda n: f"Post content for post {n}")
    hashtags = factory.LazyFunction(list)
    platform_type = PlatformType.FACEBOOK
    status = PostStatus.DRAFT
    author = factory.SubFactory(UserFactory)
    category = None
    is_ai_generated = False


class PostMediaFactory(DjangoModelFactory):
    """Tạo media upload test."""

    class Meta:
        model = PostMedia

    post = factory.SubFactory(PostFactory)
    media_type = MediaType.IMAGE
    file = factory.django.FileField(filename="test.jpg")
    caption = ""
    order = 0


class PostVersionFactory(DjangoModelFactory):
    """Tạo version snapshot bài viết."""

    class Meta:
        model = PostVersion

    post = factory.SubFactory(PostFactory)
    version_number = 1
    title = factory.LazyAttribute(lambda obj: obj.post.title)
    content = factory.LazyAttribute(lambda obj: obj.post.content)
    changed_by = factory.SubFactory(UserFactory)


class PostCommentFactory(DjangoModelFactory):
    """Tạo comment bài viết test."""

    class Meta:
        model = PostComment

    post = factory.SubFactory(PostFactory)
    author = factory.SubFactory(UserFactory)
    content = "Test comment content."


class PostTemplateFactory(DjangoModelFactory):
    """Tạo post template test."""

    class Meta:
        model = PostTemplate

    name = factory.Sequence(lambda n: f"Template {n}")
    platform_type = PlatformType.FACEBOOK
    content_template = "Template content with {placeholder}."
    is_active = True


class LayoutTemplateFactory(DjangoModelFactory):
    """Tạo layout template test."""

    class Meta:
        model = LayoutTemplate

    name = factory.Sequence(lambda n: f"Layout Template {n}")
    platform_type = PlatformType.FACEBOOK
    layout_json = factory.LazyFunction(lambda: {"title": "Test", "layout_style": "minimal"})
    is_active = True


class BannerLayoutFactory(DjangoModelFactory):
    """Tạo banner layout test."""

    class Meta:
        model = BannerLayout

    post = factory.SubFactory(PostFactory)
    variant_index = 1
    layout_json = factory.LazyFunction(lambda: {
        "title": "Banner Title",
        "tagline": "Tagline",
        "background": {"type": "color", "value": "#1A2B3C"},
        "title_position": "center",
        "font_family": "Inter",
        "accent_color": "#FF5733",
        "logo_placement": "top-left",
        "layout_style": "minimal",
    })
    is_approved = False


class AIContentGenerationFactory(DjangoModelFactory):
    """Tạo AI generation record test."""

    class Meta:
        model = AIContentGeneration

    created_by = factory.SubFactory(UserFactory)
    generation_type = GenerationType.FULL_POST
    prompt = "Test prompt for generating content."
    context_data = factory.LazyFunction(dict)
    status = GenerationStatus.PENDING
