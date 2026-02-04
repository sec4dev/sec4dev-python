"""HTTP client with retry, rate limit handling, and exception mapping."""

import random
import time
from typing import Any, Dict, Optional

import httpx

from sec4dev.exceptions import (
    AuthenticationError,
    ForbiddenError,
    NotFoundError,
    PaymentRequiredError,
    RateLimitError,
    Sec4DevError,
    ServerError,
    ValidationError,
)

DEFAULT_BASE_URL = "https://api.sec4.dev/api/v1"
SDK_VERSION = "1.0.0"
CONNECT_TIMEOUT = 10.0
READ_TIMEOUT = 30.0


def _parse_rate_limit_headers(headers: httpx.Headers) -> Dict[str, int]:
    """Parse X-RateLimit-* headers."""
    def get_int(name: str, default: int = 0) -> int:
        val = headers.get(name)
        if val is None:
            return default
        try:
            return int(val)
        except (ValueError, TypeError):
            return default

    return {
        "limit": get_int("x-ratelimit-limit"),
        "remaining": get_int("x-ratelimit-remaining"),
        "reset_seconds": get_int("x-ratelimit-reset"),
    }


def _error_from_response(
    status_code: int,
    body: Any,
    headers: Optional[httpx.Headers] = None,
) -> Sec4DevError:
    """Map HTTP status to Sec4Dev exception."""
    message = "Unknown error"
    if isinstance(body, dict) and "detail" in body:
        detail = body["detail"]
        message = detail if isinstance(detail, str) else str(detail)

    if status_code == 401:
        return AuthenticationError(message, status_code, body)
    if status_code == 402:
        return PaymentRequiredError(message, status_code, body)
    if status_code == 403:
        return ForbiddenError(message, status_code, body)
    if status_code == 404:
        return NotFoundError(message, status_code, body)
    if status_code == 422:
        return ValidationError(message, status_code, body)
    if status_code == 429:
        rate = _parse_rate_limit_headers(headers or httpx.Headers())
        retry_after = 0
        if headers:
            ra = headers.get("retry-after")
            if ra is not None:
                try:
                    retry_after = int(ra)
                except (ValueError, TypeError):
                    pass
        return RateLimitError(
            message,
            status_code=429,
            response_body=body,
            retry_after=retry_after,
            limit=rate.get("limit", 0),
            remaining=rate.get("remaining", 0),
        )
    if status_code >= 500:
        return ServerError(message, status_code, body)
    return Sec4DevError(message, status_code, body)


def _is_retryable(status_code: Optional[int], error: Optional[Exception]) -> bool:
    """True if request should be retried."""
    if error is not None:
        return True
    if status_code is None:
        return True
    if status_code == 429:
        return True
    if status_code in (500, 502, 503, 504):
        return True
    return False


def request(
    method: str,
    url: str,
    api_key: str,
    json: Optional[Dict[str, Any]] = None,
    timeout_ms: int = 30000,
    retries: int = 3,
    retry_delay_ms: int = 1000,
    on_rate_limit: Optional[Any] = None,
) -> tuple[httpx.Response, Dict[str, int]]:
    """
    Perform HTTP request with retries and rate limit handling.
    Returns (response, rate_limit_info).
    """
    timeout = httpx.Timeout(
        connect=CONNECT_TIMEOUT,
        read=READ_TIMEOUT if timeout_ms >= 1000 else timeout_ms / 1000.0,
    )
    rate_limit_info: Dict[str, int] = {"limit": 0, "remaining": 0, "reset_seconds": 0}
    last_error: Optional[Exception] = None
    last_status: Optional[int] = None
    last_response: Optional[httpx.Response] = None

    for attempt in range(retries + 1):
        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.request(
                    method,
                    url,
                    json=json,
                    headers={
                        "X-API-Key": api_key,
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                        "User-Agent": f"sec4dev-python/{SDK_VERSION}",
                    },
                )
        except Exception as e:
            last_error = e
            last_status = None
            last_response = None
            if attempt < retries and _is_retryable(None, e):
                delay_ms = retry_delay_ms * (2 ** attempt) + random.randint(0, 100)
                time.sleep(delay_ms / 1000.0)
                continue
            raise

        rate_limit_info = _parse_rate_limit_headers(response.headers)
        if on_rate_limit and callable(on_rate_limit):
            on_rate_limit(rate_limit_info)

        if response.status_code == 429:
            retry_after = 0
            ra = response.headers.get("retry-after")
            if ra is not None:
                try:
                    retry_after = int(ra)
                except (ValueError, TypeError):
                    retry_after = 60
            else:
                retry_after = 60
            if attempt < retries:
                time.sleep(retry_after)
                continue
            body: Any = None
            try:
                body = response.json()
            except Exception:
                body = response.text
            raise _error_from_response(429, body or {"detail": "Rate limit exceeded"}, response.headers)

        if response.status_code >= 400:
            last_status = response.status_code
            last_response = response
            body = None
            try:
                body = response.json()
            except Exception:
                body = response.text
            err = _error_from_response(response.status_code, body or {}, response.headers)
            if not _is_retryable(response.status_code, None):
                raise err
            last_error = err
            if attempt < retries:
                delay_ms = retry_delay_ms * (2 ** attempt) + random.randint(0, 100)
                time.sleep(delay_ms / 1000.0)
                continue
            raise err

        return response, rate_limit_info

    if last_response is not None and last_status is not None:
        body = None
        try:
            body = last_response.json()
        except Exception:
            body = last_response.text
        raise _error_from_response(last_status, body or {}, last_response.headers)
    if last_error is not None:
        raise last_error
    raise Sec4DevError("Request failed after retries", status_code=0)
