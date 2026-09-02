from email.message import EmailMessage
from email.utils import formataddr
import smtplib

from app.core.config import get_settings


settings = get_settings()


def send_transactional_email(to_email: str, subject: str, text_body: str) -> None:
    """Send a plain-text transactional message.

    In development, when SMTP is intentionally unset, the message is printed so
    the complete verification/reset flow can be exercised locally. Production
    startup rejects missing SMTP configuration.
    """
    if not settings.smtp_host:
        if settings.app_env.lower() == "production":
            raise RuntimeError("SMTP não configurado em produção.")
        print(f"[DEV EMAIL] para={to_email} assunto={subject}\n{text_body}")
        return

    message = EmailMessage()
    message["From"] = formataddr((settings.smtp_from_name, settings.smtp_from_email))
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(text_body)

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as client:
        if settings.smtp_use_tls:
            client.starttls()
        if settings.smtp_username:
            client.login(settings.smtp_username, settings.smtp_password)
        client.send_message(message)
