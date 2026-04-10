from django.core.cache import cache
from django.conf import settings
from apps.appearance.constants import APPEARANCE_CACHE_KEY


class AppearanceCacheService:

    @staticmethod
    def get_ttl() -> int:
        return getattr(settings, "APPEARANCE_CACHE_TTL", 3600)

    @classmethod
    def get_config(cls, request=None) -> dict:
        """
        Trả config từ cache. Nếu cache miss thì build từ DB và set cache.
        Lưu ý: khi có request (để build absolute URL) thì không cache
        vì URL phụ thuộc vào host. Cache chỉ lưu path tương đối.
        """
        # Build và cache với path tương đối (request=None)
        cached = cache.get(APPEARANCE_CACHE_KEY)
        if cached is not None:
            return cached

        from apps.appearance.selectors.appearance_selector import AppearanceSelector
        payload = AppearanceSelector.build_config_payload(request=None)
        cache.set(APPEARANCE_CACHE_KEY, payload, timeout=cls.get_ttl())
        return payload

    @staticmethod
    def invalidate_config() -> None:
        """Xóa cache config — gọi sau mỗi lần cập nhật token hoặc asset."""
        cache.delete(APPEARANCE_CACHE_KEY)
