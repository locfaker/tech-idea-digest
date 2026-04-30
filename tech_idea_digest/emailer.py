from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from typing import Mapping

from tech_idea_digest.models import Digest

REQUIRED_ENV = (
    "SMTP_HOST",
    "SMTP_PORT",
    "SMTP_USERNAME",
    "SMTP_PASSWORD",
    "EMAIL_FROM",
    "EMAIL_TO",
)


def send_digest_email(digest: Digest, *, env: Mapping[str, str] | None = None) -> None:
    settings = env or os.environ
    missing = tuple(key for key in REQUIRED_ENV if not settings.get(key))
    if missing:
        raise ValueError(f"Missing email environment variables: {', '.join(missing)}")

    message = EmailMessage()
    message["Subject"] = digest.subject
    message["From"] = settings["EMAIL_FROM"]
    message["To"] = settings["EMAIL_TO"]
    message.set_content(digest.body)

    host = settings["SMTP_HOST"]
    port = int(settings["SMTP_PORT"])
    use_tls = settings.get("SMTP_USE_TLS", "true").lower() != "false"

    with smtplib.SMTP(host, port, timeout=30) as smtp:
        if use_tls:
            smtp.starttls()
        smtp.login(settings["SMTP_USERNAME"], settings["SMTP_PASSWORD"])
        smtp.send_message(message)
