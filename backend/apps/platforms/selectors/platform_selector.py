from apps.platforms.models import Platform, WebhookEndpoint, WebhookLog
from apps.platforms.exceptions import PlatformNotFound, WebhookEndpointNotFound


class PlatformSelector:

    @staticmethod
    def get_all(include_inactive: bool = False):
        qs = Platform.objects.filter(is_deleted=False)
        if not include_inactive:
            qs = qs.filter(is_active=True)
        return qs.order_by("name")

    @staticmethod
    def get_by_slug(slug: str) -> Platform:
        try:
            return Platform.objects.get(slug=slug, is_deleted=False)
        except Platform.DoesNotExist:
            raise PlatformNotFound(f"Không tìm thấy nền tảng slug='{slug}'")

    @staticmethod
    def get_endpoints(platform: Platform):
        return WebhookEndpoint.objects.filter(
            platform=platform, is_active=True, is_deleted=False
        )

    @staticmethod
    def get_active_endpoint_by_slug(platform_slug: str) -> WebhookEndpoint:
        """Lấy active incoming endpoint của platform — dùng cho HMAC verify."""
        try:
            platform = PlatformSelector.get_by_slug(platform_slug)
        except PlatformNotFound as exc:
            raise WebhookEndpointNotFound(str(exc)) from exc
        endpoint = (
            WebhookEndpoint.objects
            .filter(platform=platform, is_active=True, is_deleted=False)
            .first()
        )
        if not endpoint:
            raise WebhookEndpointNotFound(f"Không có active endpoint cho platform '{platform_slug}'")
        return endpoint

    @staticmethod
    def get_logs(platform: Platform, direction: str = None):
        qs = WebhookLog.objects.filter(platform=platform, is_deleted=False)
        if direction:
            qs = qs.filter(direction=direction)
        return qs.order_by("-created_at")
