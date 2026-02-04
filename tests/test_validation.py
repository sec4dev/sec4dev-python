"""Tests for validation helpers."""

import pytest

from sec4dev.validation import validate_email, validate_ip
from sec4dev.exceptions import ValidationError


def test_validate_email_accepts_valid():
    validate_email("user@example.com")
    validate_email("a@b.co")
    validate_email("  user@domain.org  ")


def test_validate_email_rejects_empty():
    with pytest.raises(ValidationError):
        validate_email("")
    with pytest.raises(ValidationError):
        validate_email("   ")


def test_validate_email_rejects_invalid_format():
    with pytest.raises(ValidationError):
        validate_email("no-at-sign")
    with pytest.raises(ValidationError):
        validate_email("@nodomain.com")
    with pytest.raises(ValidationError):
        validate_email("nobody@")
    with pytest.raises(ValidationError):
        validate_email("a@b")  # no TLD


def test_validate_email_rejects_non_string():
    with pytest.raises(ValidationError):
        validate_email(None)
    with pytest.raises(ValidationError):
        validate_email(123)


def test_validate_ip_accepts_ipv4():
    validate_ip("192.168.1.1")
    validate_ip("0.0.0.0")
    validate_ip("255.255.255.255")
    validate_ip("  203.0.113.42  ")


def test_validate_ip_accepts_ipv6():
    validate_ip("::1")
    validate_ip("2001:db8::1")
    validate_ip("fe80::1")


def test_validate_ip_rejects_empty():
    with pytest.raises(ValidationError):
        validate_ip("")
    with pytest.raises(ValidationError):
        validate_ip("   ")


def test_validate_ip_rejects_invalid():
    with pytest.raises(ValidationError):
        validate_ip("256.1.1.1")
    with pytest.raises(ValidationError):
        validate_ip("not.an.ip")
    with pytest.raises(ValidationError):
        validate_ip("1.2.3.4.5")


def test_validate_ip_rejects_non_string():
    with pytest.raises(ValidationError):
        validate_ip(None)
    with pytest.raises(ValidationError):
        validate_ip(123)
