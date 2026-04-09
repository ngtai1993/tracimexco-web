import json
from rest_framework.renderers import JSONRenderer


class StandardJSONRenderer(JSONRenderer):
    """
    Renderer bọc response vào format chuẩn:
    { "data": ..., "message": "...", "errors": null }
    Nếu response đã ở format này (từ exception handler hoặc paginator), giữ nguyên.
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if _is_already_wrapped(data):
            return super().render(data, accepted_media_type, renderer_context)

        response = renderer_context.get("response") if renderer_context else None
        status_code = response.status_code if response else 200

        wrapped = {
            "data": data if status_code < 400 else None,
            "message": _default_message(status_code),
            "errors": data if status_code >= 400 else None,
        }
        return super().render(wrapped, accepted_media_type, renderer_context)


def _is_already_wrapped(data) -> bool:
    return (
        isinstance(data, dict)
        and "data" in data
        and "message" in data
        and "errors" in data
    )


def _default_message(status_code: int) -> str:
    if status_code < 300:
        return "OK"
    if status_code < 500:
        return "Yêu cầu không hợp lệ"
    return "Lỗi hệ thống"
