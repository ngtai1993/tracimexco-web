from collections import defaultdict
from apps.appearance.models import ColorToken, MediaAsset
from apps.appearance.constants import ColorMode, ColorGroup
from apps.appearance.exceptions import ColorTokenNotFound, MediaAssetNotFound


class AppearanceSelector:

    @staticmethod
    def get_active_color_tokens(mode: str) -> list:
        """Trả danh sách ColorToken active theo mode, sắp xếp theo group rồi order."""
        return list(
            ColorToken.objects.filter(
                mode=mode,
                is_active=True,
                is_deleted=False,
            ).order_by("group", "order", "key")
        )

    @staticmethod
    def get_active_media_assets() -> list:
        """Trả danh sách MediaAsset active."""
        return list(
            MediaAsset.objects.filter(
                is_active=True,
                is_deleted=False,
            ).order_by("key")
        )

    @staticmethod
    def get_token_by_id(pk) -> ColorToken:
        try:
            return ColorToken.objects.get(pk=pk, is_deleted=False)
        except ColorToken.DoesNotExist:
            raise ColorTokenNotFound(f"Không tìm thấy color token id='{pk}'")

    @staticmethod
    def get_asset_by_id(pk) -> MediaAsset:
        try:
            return MediaAsset.objects.get(pk=pk, is_deleted=False)
        except MediaAsset.DoesNotExist:
            raise MediaAssetNotFound(f"Không tìm thấy media asset id='{pk}'")

    @staticmethod
    def list_all_tokens(include_inactive: bool = False):
        qs = ColorToken.objects.filter(is_deleted=False)
        if not include_inactive:
            qs = qs.filter(is_active=True)
        return qs.order_by("mode", "group", "order", "key")

    @staticmethod
    def list_all_assets(include_inactive: bool = False):
        qs = MediaAsset.objects.filter(is_deleted=False)
        if not include_inactive:
            qs = qs.filter(is_active=True)
        return qs.order_by("key")

    @classmethod
    def build_config_payload(cls, request=None) -> dict:
        """
        Gom token light + dark + assets thành dict phục vụ endpoint public.
        Cấu trúc:
          {
            "colors": {
              "light": { "brand": [...], "semantic": [...], "neutral": [...] },
              "dark":  { "brand": [...], "semantic": [...], "neutral": [...] },
            },
            "media": { "logo": {"url": "...", "alt": "..."}, ... }
          }
        """
        colors = {}
        for mode in [ColorMode.LIGHT, ColorMode.DARK]:
            grouped = defaultdict(list)
            for token in cls.get_active_color_tokens(mode):
                grouped[token.group].append({
                    "key": token.key,
                    "value": token.value,
                    "name": token.name,
                })
            # Đảm bảo thứ tự nhóm chuẩn
            ordered = {}
            for group in [ColorGroup.BRAND, ColorGroup.SEMANTIC, ColorGroup.NEUTRAL]:
                if group in grouped:
                    ordered[group] = grouped[group]
            # custom group nếu có
            for group, tokens in grouped.items():
                if group not in ordered:
                    ordered[group] = tokens
            colors[mode] = ordered

        media = {}
        for asset in cls.get_active_media_assets():
            url = None
            if asset.file:
                if request is not None:
                    url = request.build_absolute_uri(asset.file.url)
                else:
                    url = asset.file.url
            media[asset.key] = {"url": url, "alt": asset.alt_text}

        return {"colors": colors, "media": media}
