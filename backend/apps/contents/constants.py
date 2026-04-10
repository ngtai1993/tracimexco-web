class PostStatus:
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    ARCHIVED = "archived"

    CHOICES = [
        (DRAFT, "Draft"),
        (REVIEW, "Chờ Review"),
        (APPROVED, "Đã Duyệt"),
        (SCHEDULED, "Đã Lên Lịch"),
        (PUBLISHED, "Đã Đăng"),
        (ARCHIVED, "Lưu Trữ"),
    ]

    EDITABLE = [DRAFT]
    DELETABLE = [DRAFT]


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


class MediaType:
    IMAGE = "image"
    VIDEO = "video"
    FILE = "file"

    CHOICES = [
        (IMAGE, "Image"),
        (VIDEO, "Video"),
        (FILE, "File"),
    ]


class GenerationType:
    FULL_POST = "full_post"
    HASHTAGS = "hashtags"
    SUMMARY = "summary"
    CAPTION = "caption"
    TRANSLATION = "translation"
    IMPROVEMENT = "improvement"
    AB_VARIANT = "ab_variant"

    CHOICES = [
        (FULL_POST, "Full Post"),
        (HASHTAGS, "Hashtags"),
        (SUMMARY, "Summary"),
        (CAPTION, "Caption"),
        (TRANSLATION, "Translation"),
        (IMPROVEMENT, "Improvement"),
        (AB_VARIANT, "A/B Variant"),
    ]


class GenerationStatus:
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

    CHOICES = [
        (PENDING, "Pending"),
        (PROCESSING, "Processing"),
        (COMPLETED, "Completed"),
        (FAILED, "Failed"),
    ]


class ImprovementType:
    TONE = "tone"
    ENGAGEMENT = "engagement"
    CLARITY = "clarity"
    SEO = "seo"

    CHOICES = [
        (TONE, "Tone"),
        (ENGAGEMENT, "Engagement"),
        (CLARITY, "Clarity"),
        (SEO, "SEO"),
    ]
