import logging
from celery import shared_task
from common.utils.email import send_email

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_welcome_email(self, user_email: str, user_name: str):
    """Gửi email chào mừng sau khi user đăng ký."""
    try:
        send_email(
            subject="Chào mừng bạn đến với hệ thống!",
            message=f"Xin chào {user_name}, tài khoản của bạn đã được tạo thành công.",
            recipient_list=[user_email],
        )
        logger.info("Welcome email sent to %s", user_email)
    except Exception as exc:
        logger.error("Failed to send welcome email to %s: %s", user_email, exc)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_password_reset_email(self, user_email: str, reset_link: str):
    """Gửi email reset mật khẩu."""
    try:
        send_email(
            subject="Yêu cầu đặt lại mật khẩu",
            message=f"Nhấn vào link sau để đặt lại mật khẩu: {reset_link}\nLink có hiệu lực trong 24 giờ.",
            recipient_list=[user_email],
        )
        logger.info("Password reset email sent to %s", user_email)
    except Exception as exc:
        logger.error("Failed to send password reset email to %s: %s", user_email, exc)
        raise self.retry(exc=exc)
