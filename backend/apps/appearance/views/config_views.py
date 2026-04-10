from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from apps.appearance.services.appearance_cache_service import AppearanceCacheService
from apps.appearance.selectors.appearance_selector import AppearanceSelector
from apps.appearance.constants import ColorMode


class AppearanceConfigView(APIView):
    """GET /api/v1/appearance/config/ — public endpoint trả toàn bộ tokens + assets."""

    permission_classes = [AllowAny]

    def get(self, request):
        payload = AppearanceCacheService.get_config()

        # Sau khi lấy từ cache (không có request), build lại absolute URL cho media
        # bằng cách dùng request hiện tại mà không ảnh hưởng cache
        if payload.get("media"):
            media = {}
            for key, asset_data in payload["media"].items():
                url = asset_data.get("url")
                if url and url.startswith("/"):
                    url = request.build_absolute_uri(url)
                media[key] = {"url": url, "alt": asset_data.get("alt", "")}
            payload = {**payload, "media": media}

        return Response({"data": payload, "message": "OK"})


class AppearanceCSSView(APIView):
    """GET /api/v1/appearance/config/css/ — trả CSS custom properties cho cả light và dark mode."""

    permission_classes = [AllowAny]

    def get(self, request):
        payload = AppearanceCacheService.get_config()
        colors = payload.get("colors", {})

        def build_vars(mode_tokens: dict) -> str:
            lines = []
            for tokens in mode_tokens.values():
                for token in tokens:
                    lines.append(f"  --color-{token['key']}: {token['value']};")
            return "\n".join(lines)

        light_vars = build_vars(colors.get(ColorMode.LIGHT, {}))
        dark_vars = build_vars(colors.get(ColorMode.DARK, {}))

        css = f":root {{\n{light_vars}\n}}\n\n[data-theme=\"dark\"] {{\n{dark_vars}\n}}\n"
        return HttpResponse(css, content_type="text/css")
