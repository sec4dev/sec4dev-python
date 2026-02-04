"""Sec4Dev API client."""

from typing import Any, Callable, Optional

from sec4dev.email import EmailService
from sec4dev.exceptions import ValidationError
from sec4dev.http import DEFAULT_BASE_URL
from sec4dev.ip import IPService


class Sec4DevClient:
    """Main client for the Sec4Dev Security Checks API."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = 30000,
        retries: int = 3,
        retry_delay: int = 1000,
        on_rate_limit: Optional[Callable[[Any], None]] = None,
    ) -> None:
        if not api_key or not str(api_key).strip().startswith("sec4_"):
            raise ValidationError("API key must start with sec4_", status_code=422)
        self._api_key = api_key.strip()
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._retries = retries
        self._retry_delay = retry_delay
        self._on_rate_limit = on_rate_limit
        self._rate_limit: dict = {"limit": 0, "remaining": 0, "reset_seconds": 0}

        def _capture_rate_limit(info: dict) -> None:
            self._rate_limit = info
            if on_rate_limit:
                on_rate_limit(info)

        self._email = EmailService(
            self._base_url,
            self._api_key,
            timeout_ms=self._timeout,
            retries=self._retries,
            retry_delay_ms=self._retry_delay,
            on_rate_limit=_capture_rate_limit,
        )
        self._ip = IPService(
            self._base_url,
            self._api_key,
            timeout_ms=self._timeout,
            retries=self._retries,
            retry_delay_ms=self._retry_delay,
            on_rate_limit=_capture_rate_limit,
        )

    @property
    def email(self) -> EmailService:
        """Email check service."""
        return self._email

    @property
    def ip(self) -> IPService:
        """IP check service."""
        return self._ip

    @property
    def rate_limit(self) -> dict:
        """Last rate limit info (limit, remaining, reset_seconds)."""
        return dict(self._rate_limit)
