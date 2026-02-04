"""Email check service."""

from typing import Callable, Optional

from sec4dev.http import request
from sec4dev.models.email import EmailCheckResult
from sec4dev.validation import validate_email


class EmailService:
    """Service for checking email (disposable domain)."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout_ms: int = 30000,
        retries: int = 3,
        retry_delay_ms: int = 1000,
        on_rate_limit: Optional[Callable[[dict], None]] = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout_ms = timeout_ms
        self._retries = retries
        self._retry_delay_ms = retry_delay_ms
        self._on_rate_limit = on_rate_limit

    def check(self, email: str) -> EmailCheckResult:
        """Check if an email uses a disposable domain."""
        validate_email(email)
        url = f"{self._base_url}/email/check"
        resp, _ = request(
            "POST",
            url,
            self._api_key,
            json={"email": email.strip()},
            timeout_ms=self._timeout_ms,
            retries=self._retries,
            retry_delay_ms=self._retry_delay_ms,
            on_rate_limit=self._on_rate_limit,
        )
        data = resp.json()
        return EmailCheckResult(
            email=data.get("email", email),
            domain=data.get("domain", ""),
            is_disposable=data.get("is_disposable", False),
        )

    def is_disposable(self, email: str) -> bool:
        """Return True if the email domain is disposable."""
        return self.check(email).is_disposable
