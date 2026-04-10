class PlatformType:
    FACEBOOK = "facebook"
    ZALO = "zalo"
    TIKTOK = "tiktok"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    CUSTOM = "custom"

    CHOICES = [
        (FACEBOOK, "Facebook"),
        (ZALO, "Zalo"),
        (TIKTOK, "TikTok"),
        (LINKEDIN, "LinkedIn"),
        (TWITTER, "Twitter/X"),
        (CUSTOM, "Custom"),
    ]


class HealthStatus:
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNREACHABLE = "unreachable"
    UNKNOWN = "unknown"

    CHOICES = [
        (HEALTHY, "Healthy"),
        (DEGRADED, "Degraded"),
        (UNREACHABLE, "Unreachable"),
        (UNKNOWN, "Unknown"),
    ]


class WebhookDirection:
    OUTGOING = "outgoing"
    INCOMING = "incoming"

    CHOICES = [
        (OUTGOING, "Outgoing"),
        (INCOMING, "Incoming"),
    ]


WEBHOOK_EVENTS = [
    "publish",
    "publish_success",
    "publish_error",
    "engagement",
]
