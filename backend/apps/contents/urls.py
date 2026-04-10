from django.urls import path

from apps.contents.views import (
    CategoryListCreateView,
    CategoryDetailView,
    TagListCreateView,
    PostListCreateView,
    PostDetailView,
    PostDuplicateView,
    PostSubmitReviewView,
    PostApproveView,
    PostRejectView,
    PostVersionListView,
    PostMediaListCreateView,
    PostMediaDeleteView,
    PostCommentListCreateView,
    AIGenerateView,
    AIGenerationDetailView,
    AISuggestHashtagsView,
    AISummarizeView,
    AITranslateView,
    AIImproveView,
    AIGenerateCaptionView,
    BannerLayoutListView,
    BannerLayoutGenerateView,
    BannerLayoutDetailView,
    BannerLayoutApproveView,
    LayoutTemplateListCreateView,
    PostTemplateListCreateView,
    PostTemplateUseView,
    AnalyticsSummaryView,
    AnalyticsPostsView,
    AnalyticsPublishHistoryView,
)

app_name = "contents"

urlpatterns = [
    # Taxonomy
    path("categories/", CategoryListCreateView.as_view(), name="category-list"),
    path("categories/<slug:slug>/", CategoryDetailView.as_view(), name="category-detail"),
    path("tags/", TagListCreateView.as_view(), name="tag-list"),

    # Posts
    path("posts/", PostListCreateView.as_view(), name="post-list"),
    path("posts/<uuid:post_id>/", PostDetailView.as_view(), name="post-detail"),
    path("posts/<uuid:post_id>/duplicate/", PostDuplicateView.as_view(), name="post-duplicate"),
    path("posts/<uuid:post_id>/submit-review/", PostSubmitReviewView.as_view(), name="post-submit-review"),
    path("posts/<uuid:post_id>/approve/", PostApproveView.as_view(), name="post-approve"),
    path("posts/<uuid:post_id>/reject/", PostRejectView.as_view(), name="post-reject"),
    path("posts/<uuid:post_id>/versions/", PostVersionListView.as_view(), name="post-versions"),
    path("posts/<uuid:post_id>/media/", PostMediaListCreateView.as_view(), name="post-media-list"),
    path("posts/<uuid:post_id>/media/<uuid:media_id>/", PostMediaDeleteView.as_view(), name="post-media-detail"),
    path("posts/<uuid:post_id>/comments/", PostCommentListCreateView.as_view(), name="post-comments"),

    # Banner Layouts
    path("posts/<uuid:post_id>/banner-layouts/", BannerLayoutListView.as_view(), name="banner-layout-list"),
    path("posts/<uuid:post_id>/banner-layouts/generate/", BannerLayoutGenerateView.as_view(), name="banner-layout-generate"),
    path("posts/<uuid:post_id>/banner-layouts/<uuid:layout_id>/", BannerLayoutDetailView.as_view(), name="banner-layout-detail"),
    path("posts/<uuid:post_id>/banner-layouts/<uuid:layout_id>/approve/", BannerLayoutApproveView.as_view(), name="banner-layout-approve"),

    # AI Generation
    path("ai/generate/", AIGenerateView.as_view(), name="ai-generate"),
    path("ai/generations/<uuid:generation_id>/", AIGenerationDetailView.as_view(), name="ai-generation-detail"),
    path("ai/suggest-hashtags/", AISuggestHashtagsView.as_view(), name="ai-hashtags"),
    path("ai/summarize/", AISummarizeView.as_view(), name="ai-summarize"),
    path("ai/translate/", AITranslateView.as_view(), name="ai-translate"),
    path("ai/improve/", AIImproveView.as_view(), name="ai-improve"),
    path("ai/generate-caption/", AIGenerateCaptionView.as_view(), name="ai-caption"),

    # Templates
    path("layout-templates/", LayoutTemplateListCreateView.as_view(), name="layout-template-list"),
    path("templates/", PostTemplateListCreateView.as_view(), name="post-template-list"),
    path("templates/<uuid:template_id>/use/", PostTemplateUseView.as_view(), name="post-template-use"),

    # Analytics
    path("analytics/summary/", AnalyticsSummaryView.as_view(), name="analytics-summary"),
    path("analytics/posts/", AnalyticsPostsView.as_view(), name="analytics-posts"),
    path("analytics/publish-history/", AnalyticsPublishHistoryView.as_view(), name="analytics-publish-history"),
]
