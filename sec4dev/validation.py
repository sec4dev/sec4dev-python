"""Input validation for email and IP."""

import ipaddress
import re

from sec4dev.exceptions import ValidationError

EMAIL_REGEX = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def validate_email(email: str) -> None:
    """Validate email format. Raises ValidationError if invalid."""
    if not email or not isinstance(email, str):
        raise ValidationError("Email is required", status_code=422)
    email = email.strip()
    if not email:
        raise ValidationError("Email cannot be empty", status_code=422)
    if not EMAIL_REGEX.match(email):
        raise ValidationError("Invalid email format", status_code=422)


def validate_ip(ip: str) -> None:
    """Validate IP address (IPv4 or IPv6). Raises ValidationError if invalid."""
    if not ip or not isinstance(ip, str):
        raise ValidationError("IP address is required", status_code=422)
    ip = ip.strip()
    if not ip:
        raise ValidationError("IP address cannot be empty", status_code=422)
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        raise ValidationError("Invalid IP address format", status_code=422)
