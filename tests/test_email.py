"""Tests for EmailService (mocked HTTP)."""

import pytest

from sec4dev import Sec4DevClient
from sec4dev.exceptions import ValidationError, AuthenticationError


def test_email_check_returns_result():
    from unittest.mock import patch, MagicMock

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "email": "user@tempmail.com",
        "domain": "tempmail.com",
        "is_disposable": True,
    }
    mock_resp.headers = {}

    with patch("sec4dev.email.request", return_value=(mock_resp, {})):
        client = Sec4DevClient("sec4_test")
        result = client.email.check("user@tempmail.com")

    assert result.email == "user@tempmail.com"
    assert result.domain == "tempmail.com"
    assert result.is_disposable is True


def test_email_is_disposable_true():
    from unittest.mock import patch, MagicMock

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "email": "x@disposable.com",
        "domain": "disposable.com",
        "is_disposable": True,
    }
    mock_resp.headers = {}

    with patch("sec4dev.email.request", return_value=(mock_resp, {})):
        client = Sec4DevClient("sec4_test")
        assert client.email.is_disposable("x@disposable.com") is True


def test_email_is_disposable_false():
    from unittest.mock import patch, MagicMock

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "email": "user@gmail.com",
        "domain": "gmail.com",
        "is_disposable": False,
    }
    mock_resp.headers = {}

    with patch("sec4dev.email.request", return_value=(mock_resp, {})):
        client = Sec4DevClient("sec4_test")
        assert client.email.is_disposable("user@gmail.com") is False


def test_email_check_invalid_email_raises():
    client = Sec4DevClient("sec4_test")
    with pytest.raises(ValidationError):
        client.email.check("not-an-email")
    with pytest.raises(ValidationError):
        client.email.check("")
    with pytest.raises(ValidationError):
        client.email.check("missing-at.com")


def test_email_check_401_raises_authentication_error():
    from unittest.mock import patch

    with patch("sec4dev.email.request") as mock_request:
        mock_request.side_effect = AuthenticationError("Invalid API key", 401, None)
        client = Sec4DevClient("sec4_test")
        with pytest.raises(AuthenticationError):
            client.email.check("user@gmail.com")
