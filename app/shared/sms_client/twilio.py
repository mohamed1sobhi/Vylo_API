from __future__ import annotations

import asyncio
import base64
import logging
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.shared.config.settings import settings


logger = logging.getLogger(__name__)


class TwilioSMSClient:
	def __init__(
		self,
		*,
		account_sid: str | None = None,
		auth_token: str | None = None,
		from_phone: str | None = None,
	) -> None:
		self._account_sid = account_sid if account_sid is not None else settings.TWILIO_ACCOUNT_SID
		self._auth_token = auth_token if auth_token is not None else settings.TWILIO_AUTH_TOKEN
		self._from_phone = from_phone if from_phone is not None else settings.TWILIO_FROM_PHONE

	async def send_sms(self, *, to_phone: str | None, body: str) -> bool:
		if not to_phone or not self._account_sid or not self._auth_token or not self._from_phone:
			return False

		return await asyncio.to_thread(self._send, to_phone, body)

	def _send(self, to_phone: str, body: str) -> bool:
		url = f"https://api.twilio.com/2010-04-01/Accounts/{self._account_sid}/Messages.json"
		data = urlencode({"From": self._from_phone, "To": to_phone, "Body": body}).encode()
		token = f"{self._account_sid}:{self._auth_token}".encode()
		auth_header = base64.b64encode(token).decode()
		request = Request(
			url,
			data=data,
			headers={
				"Authorization": f"Basic {auth_header}",
				"Content-Type": "application/x-www-form-urlencoded",
			},
			method="POST",
		)

		try:
			with urlopen(request, timeout=10) as response:
				return 200 <= response.status < 300
		except Exception:
			logger.info("Twilio SMS delivery failed", exc_info=True)
			return False


__all__ = ["TwilioSMSClient"]
