"""Sec4Dev API exception hierarchy."""

from typing import Any, Optional


class Sec4DevError(Exception):
    """Base exception for all Sec4Dev API errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 0,
        response_body: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_body = response_body


class AuthenticationError(Sec4DevError):
    """401 - Invalid or missing API key."""

    pass


class PaymentRequiredError(Sec4DevError):
    """402 - Quota exceeded."""

    pass


class ForbiddenError(Sec4DevError):
    """403 - Account deactivated."""

    pass


class NotFoundError(Sec4DevError):
    """404 - Resource not found."""

    pass


class ValidationError(Sec4DevError):
    """422 - Invalid input (or client-side validation failure)."""

    pass


class RateLimitError(Sec4DevError):
    """429 - Rate limit exceeded."""

    def __init__(
        self,
        message: str,
        status_code: int = 429,
        response_body: Optional[Any] = None,
        retry_after: int = 0,
        limit: int = 0,
        remaining: int = 0,
    ) -> None:
        super().__init__(message, status_code, response_body)
        self.retry_after = retry_after
        self.limit = limit
        self.remaining = remaining


class ServerError(Sec4DevError):
    """500+ - Server errors."""

    pass
