"""Email check models."""

from pydantic import BaseModel


class EmailCheckResult(BaseModel):
    """Result of an email check."""

    email: str
    domain: str
    is_disposable: bool
