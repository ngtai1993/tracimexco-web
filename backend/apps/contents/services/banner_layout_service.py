import logging

from django.db import transaction

from apps.contents.models import BannerLayout
from apps.contents.exceptions import BannerLayoutNotFound

logger = logging.getLogger(__name__)


class BannerLayoutService:

    @staticmethod
    @transaction.atomic
    def generate(post, rag_instance=None, variants: int = 2) -> list:
        """Dispatch Celery task để RAG sinh layout JSON cho banner."""
        from tasks.content_tasks import task_generate_banner_layout
        task_generate_banner_layout.delay(str(post.id), str(rag_instance.id) if rag_instance else None, variants)
        return []

    @staticmethod
    def process_generation(post_id: str, rag_instance_id: str = None, variants: int = 2) -> None:
        """Được gọi bởi Celery task — gọi RAG và lưu BannerLayout records."""
        from apps.contents.models import Post
        try:
            post = Post.objects.get(id=post_id, is_deleted=False)
        except Post.DoesNotExist:
            logger.warning("Post %s not found for banner generation", post_id)
            return

        rag_instance = None
        if rag_instance_id:
            try:
                from apps.graph_rag.models import RAGInstance
                rag_instance = RAGInstance.objects.get(id=rag_instance_id, is_active=True)
            except Exception:
                logger.warning("RAGInstance %s not found", rag_instance_id)

        # Remove old non-approved layouts before regenerating
        post.banner_layouts.filter(is_approved=False, is_deleted=False).update(is_deleted=True)

        layouts = []
        for i in range(1, variants + 1):
            layout_json = BannerLayoutService._call_rag_for_layout(post, rag_instance, variant_index=i)
            layout = BannerLayout.objects.create(
                post=post,
                rag_instance=rag_instance,
                variant_index=i,
                layout_json=layout_json,
            )
            layouts.append(layout)

        return layouts

    @staticmethod
    def _call_rag_for_layout(post, rag_instance, variant_index: int) -> dict:
        """Gọi RAG để sinh layout JSON cho banner."""
        prompt = (
            f"Dựa trên nội dung bài viết sau, hãy tạo bố cục banner cho nền tảng "
            f"{post.platform_type} (phương án {variant_index}):\n\n"
            f"Tiêu đề: {post.title}\n"
            f"Nội dung: {post.content[:500]}\n\n"
            "Trả về JSON với các trường: title, tagline, background (type + value), "
            "title_position, font_family, accent_color, logo_placement, layout_style."
        )
        try:
            from apps.graph_rag.services.pipeline_service import PipelineService
            result = PipelineService.query(
                rag_instance=rag_instance,
                query=prompt,
                user=None,
                extra_context={"response_format": "json", "variant": variant_index},
            )
            answer = result.get("answer", result.get("content", "{}"))
            import json
            if isinstance(answer, str):
                try:
                    return json.loads(answer)
                except json.JSONDecodeError:
                    pass
            return answer if isinstance(answer, dict) else {}
        except Exception as exc:
            logger.warning("RAG banner generation variant %d failed: %s", variant_index, exc)
            return BannerLayoutService._default_layout(post, variant_index)

    @staticmethod
    def _default_layout(post, variant_index: int) -> dict:
        """Layout mặc định khi RAG không khả dụng."""
        styles = ["minimal", "bold", "gradient"]
        return {
            "title": post.title[:80],
            "tagline": "",
            "background": {"type": "color", "value": "#1A2B3C"},
            "title_position": "center",
            "font_family": "Inter",
            "accent_color": "#FF5733",
            "logo_placement": "top-left",
            "layout_style": styles[(variant_index - 1) % len(styles)],
        }

    @staticmethod
    @transaction.atomic
    def approve(layout: BannerLayout, approver) -> BannerLayout:
        """Duyệt một layout — bỏ duyệt các layout khác của cùng bài viết."""
        layout.post.banner_layouts.filter(is_approved=True, is_deleted=False).update(is_approved=False)
        layout.is_approved = True
        layout.approved_by = approver
        layout.save(update_fields=["is_approved", "approved_by", "updated_at"])
        return layout

    @staticmethod
    @transaction.atomic
    def update(layout: BannerLayout, layout_json: dict) -> BannerLayout:
        layout.layout_json = layout_json
        layout.save(update_fields=["layout_json", "updated_at"])
        return layout
