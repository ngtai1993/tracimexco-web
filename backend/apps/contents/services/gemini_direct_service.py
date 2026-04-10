"""
GeminiDirectService — gọi Gemini trực tiếp (không qua RAG pipeline) cho
các tác vụ AI nhỏ trong app contents: hashtags, summary, translate, improve.
"""
import logging
import re

import google.generativeai as genai

from apps.agents.services.agent_key_service import AgentKeyService

logger = logging.getLogger(__name__)

_PROVIDER_SLUG = "google-gemini"
_DEFAULT_MODEL = "gemini-2.0-flash"


def _get_model() -> genai.GenerativeModel:
    api_key = AgentKeyService.get_active_key(_PROVIDER_SLUG)
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(
        _DEFAULT_MODEL,
        generation_config=genai.GenerationConfig(temperature=0.5, max_output_tokens=1024),
    )


class GeminiDirectService:

    @staticmethod
    def suggest_hashtags(content: str, platform_type: str, count: int) -> list[str]:
        """Trả về list hashtag (tối đa `count`) phù hợp với nội dung và nền tảng."""
        platform_label = platform_type or "mạng xã hội"
        prompt = (
            f"Đề xuất đúng {count} hashtag phù hợp nhất cho bài viết trên {platform_label}.\n\n"
            f"Nội dung bài viết:\n{content}\n\n"
            "Yêu cầu:\n"
            "- Mỗi hashtag bắt đầu bằng # (không có khoảng trắng)\n"
            "- Liệt kê mỗi hashtag trên một dòng riêng\n"
            "- Không thêm giải thích hay văn bản nào khác"
        )
        model = _get_model()
        response = model.generate_content(prompt)
        raw = response.text or ""
        hashtags = [
            tag.strip()
            for tag in re.findall(r"#\S+", raw)
        ]
        return hashtags[:count]

    @staticmethod
    def summarize(content: str, platform_type: str, max_length: int) -> str:
        """Tóm tắt nội dung phù hợp với nền tảng, tối đa `max_length` ký tự."""
        platform_label = platform_type or "mạng xã hội"
        prompt = (
            f"Tóm tắt bài viết sau để đăng trên {platform_label}.\n\n"
            f"Bài viết gốc:\n{content}\n\n"
            f"Yêu cầu:\n"
            f"- Tối đa {max_length} ký tự\n"
            "- Giữ ý chính và tone ban đầu\n"
            "- Chỉ trả về nội dung tóm tắt, không thêm giải thích"
        )
        model = _get_model()
        response = model.generate_content(prompt)
        summary = (response.text or "").strip()
        return summary[:max_length]

    @staticmethod
    def translate(content: str, target_language: str) -> str:
        """Dịch nội dung sang ngôn ngữ đích."""
        lang_map = {
            "en": "tiếng Anh",
            "vi": "tiếng Việt",
            "ja": "tiếng Nhật",
            "ko": "tiếng Hàn",
            "zh": "tiếng Trung",
            "fr": "tiếng Pháp",
            "de": "tiếng Đức",
        }
        lang_label = lang_map.get(target_language.lower(), target_language)
        prompt = (
            f"Dịch đoạn văn bản sau sang {lang_label}.\n\n"
            f"Văn bản gốc:\n{content}\n\n"
            "Chỉ trả về bản dịch, không thêm chú thích hay giải thích."
        )
        model = _get_model()
        response = model.generate_content(prompt)
        return (response.text or "").strip()

    @staticmethod
    def improve(content: str, improvement_type: str) -> str:
        """Cải thiện nội dung theo `improvement_type`."""
        type_prompt_map = {
            "tone": (
                "Viết lại đoạn văn này với tone chuyên nghiệp hơn, "
                "phù hợp với bài đăng doanh nghiệp."
            ),
            "engagement": (
                "Viết lại đoạn văn này để tăng engagement: "
                "thêm call-to-action, đặt câu hỏi, dùng ngôn ngữ sinh động."
            ),
            "clarity": (
                "Viết lại đoạn văn này rõ ràng và ngắn gọn hơn: "
                "loại bỏ từ thừa, dùng câu ngắn, cấu trúc mạch lạc."
            ),
            "seo": (
                "Viết lại đoạn văn này tối ưu SEO: "
                "thêm từ khóa tự nhiên, tăng khả năng tìm kiếm, "
                "dùng tiêu đề và cấu trúc rõ ràng."
            ),
        }
        instruction = type_prompt_map.get(
            improvement_type,
            f"Cải thiện đoạn văn theo hướng '{improvement_type}'."
        )
        prompt = (
            f"{instruction}\n\n"
            f"Văn bản gốc:\n{content}\n\n"
            "Chỉ trả về văn bản đã cải thiện, không thêm giải thích."
        )
        model = _get_model()
        response = model.generate_content(prompt)
        return (response.text or "").strip()
