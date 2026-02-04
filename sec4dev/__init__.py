"""Sec4Dev SDK for Python - Security Checks API."""

__version__ = "1.0.0"

from sec4dev.client import Sec4DevClient
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
from sec4dev.models import (
    EmailCheckResult,
    IPCheckResult,
    IPClassification,
    IPGeo,
    IPNetwork,
    IPSignals,
)

__all__ = [
    "Sec4DevClient",
    "Sec4DevError",
    "AuthenticationError",
    "PaymentRequiredError",
    "ForbiddenError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "ServerError",
    "EmailCheckResult",
    "IPCheckResult",
    "IPSignals",
    "IPNetwork",
    "IPGeo",
    "IPClassification",
    "__version__",
]
