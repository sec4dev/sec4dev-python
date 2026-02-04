"""Tests for Sec4DevClient and API key validation."""

import pytest

from sec4dev import Sec4DevClient
from sec4dev.exceptions import ValidationError


def test_client_accepts_valid_api_key():
    client = Sec4DevClient("sec4_test_key_123")
    assert client._api_key == "sec4_test_key_123"
    assert client.email is not None
    assert client.ip is not None


def test_client_strips_api_key():
    client = Sec4DevClient("  sec4_abc  ")
    assert client._api_key == "sec4_abc"


def test_client_rejects_empty_api_key():
    with pytest.raises(ValidationError) as exc_info:
        Sec4DevClient("")
    assert "sec4_" in str(exc_info.value)


def test_client_rejects_api_key_without_prefix():
    with pytest.raises(ValidationError) as exc_info:
        Sec4DevClient("invalid_key")
    assert "sec4_" in str(exc_info.value)


def test_client_rejects_whitespace_only_api_key():
    with pytest.raises(ValidationError):
        Sec4DevClient("   ")


def test_client_uses_custom_base_url():
    client = Sec4DevClient("sec4_k", base_url="https://custom.example.com/v1")
    assert client._base_url == "https://custom.example.com/v1"


def test_client_rate_limit_property():
    client = Sec4DevClient("sec4_k")
    rl = client.rate_limit
    assert "limit" in rl
    assert "remaining" in rl
    assert "reset_seconds" in rl
