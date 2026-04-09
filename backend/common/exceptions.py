from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Global exception handler — bọc tất cả lỗi vào format chuẩn:
    { "data": null, "message": "...", "errors": { ... } }
    """
    response = exception_handler(exc, context)

    if response is not None:
        errors = response.data if isinstance(response.data, dict) else {"detail": response.data}
        message = _extract_message(errors)
        response.data = {
            "data": None,
            "message": message,
            "errors": errors,
        }
    else:
        logger.exception("Unhandled exception", exc_info=exc)
        response = Response(
            {
                "data": None,
                "message": "Lỗi hệ thống nội bộ. Vui lòng thử lại sau.",
                "errors": None,
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response


def _extract_message(errors: dict) -> str:
    """Lấy message đầu tiên từ errors dict làm message tổng."""
    if "detail" in errors:
        detail = errors["detail"]
        return str(detail) if not isinstance(detail, list) else str(detail[0])
    for value in errors.values():
        if isinstance(value, list) and value:
            return str(value[0])
        if isinstance(value, str):
            return value
    return "Dữ liệu không hợp lệ"
