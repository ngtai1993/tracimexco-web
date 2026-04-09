from django.core.mail import send_mail
from django.conf import settings


def send_email(subject: str, message: str, recipient_list: list[str], html_message: str = None):
    """Helper gửi email đơn giản."""
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        html_message=html_message,
        fail_silently=False,
    )
