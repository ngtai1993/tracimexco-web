class ScheduleStatus:
    PENDING = "pending"
    PROCESSING = "processing"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"

    CHOICES = [
        (PENDING, "Chờ Đăng"),
        (PROCESSING, "Đang Xử Lý"),
        (PUBLISHED, "Đã Đăng"),
        (FAILED, "Thất Bại"),
        (CANCELLED, "Đã Hủy"),
    ]


class AttemptStatus:
    SUCCESS = "success"
    FAILED = "failed"

    CHOICES = [
        (SUCCESS, "Success"),
        (FAILED, "Failed"),
    ]


DEFAULT_TIMEZONE = "Asia/Ho_Chi_Minh"
# Exponential backoff delays (seconds): attempt 1=5min, 2=15min, 3=60min
RETRY_DELAYS = [300, 900, 3600]
MAX_RETRY_ATTEMPTS = 3
