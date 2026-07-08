from __future__ import annotations

import asyncio
import logging
import smtplib
from email.message import EmailMessage

from app.shared.config.settings import settings


logger = logging.getLogger(__name__)


class EmailClient:
	def __init__(
		self,
		*,
		smtp_host: str | None = None,
		smtp_port: int | None = None,
		username: str | None = None,
		password: str | None = None,
		from_email: str | None = None,
		use_tls: bool | None = None,
	) -> None:
		self._smtp_host = smtp_host if smtp_host is not None else settings.SMTP_HOST
		self._smtp_port = smtp_port if smtp_port is not None else settings.SMTP_PORT
		self._username = username if username is not None else settings.SMTP_USERNAME
		self._password = password if password is not None else settings.SMTP_PASSWORD
		self._from_email = from_email if from_email is not None else settings.EMAIL_FROM
		self._use_tls = use_tls if use_tls is not None else settings.SMTP_USE_TLS

	async def send_email(self, *, to_email: str | None, subject: str, body: str) -> bool:
		if not to_email or not self._smtp_host:
			return False

		message = EmailMessage()
		message["From"] = self._from_email
		message["To"] = to_email
		message["Subject"] = subject
		message.set_content(body)

		return await asyncio.to_thread(self._send, message)

	def _send(self, message: EmailMessage) -> bool:
		try:
			with smtplib.SMTP(self._smtp_host, self._smtp_port, timeout=10) as smtp:
				if self._use_tls:
					smtp.starttls()
				if self._username and self._password:
					smtp.login(self._username, self._password)
				smtp.send_message(message)
		except Exception:
			logger.info("Email delivery failed", exc_info=True)
			return False
		return True


__all__ = ["EmailClient"]
