"""Tests for IPService (mocked HTTP)."""

import pytest

from sec4dev import Sec4DevClient
from sec4dev.exceptions import ValidationError


def _make_ip_response(ip="203.0.113.42", classification="hosting", **kwargs):
    defaults = {
        "ip": ip,
        "classification": classification,
        "confidence": 0.95,
        "signals": {
            "is_hosting": classification == "hosting",
            "is_residential": classification == "residential",
            "is_mobile": False,
            "is_vpn": classification == "vpn",
            "is_tor": False,
            "is_proxy": False,
        },
        "network": {"asn": 16509, "org": "Amazon.com, Inc.", "provider": "AWS"},
        "geo": {"country": "US", "region": None},
    }
    signals = defaults["signals"].copy()
    signals.update(kwargs.get("signals") or {})
    defaults["signals"] = signals
    defaults.update(kwargs)
    return defaults


def test_ip_check_returns_result():
    from unittest.mock import patch, MagicMock

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = _make_ip_response()
    mock_resp.headers = {}

    with patch("sec4dev.ip.request", return_value=(mock_resp, {})):
        client = Sec4DevClient("sec4_test")
        result = client.ip.check("203.0.113.42")

    assert result.ip == "203.0.113.42"
    assert result.classification == "hosting"
    assert result.confidence == 0.95
    assert result.signals.is_hosting is True
    assert result.signals.is_vpn is False
    assert result.network.provider == "AWS"
    assert result.geo.country == "US"


def test_ip_is_hosting():
    from unittest.mock import patch, MagicMock

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = _make_ip_response(classification="hosting")
    mock_resp.headers = {}

    with patch("sec4dev.ip.request", return_value=(mock_resp, {})):
        client = Sec4DevClient("sec4_test")
        assert client.ip.is_hosting("203.0.113.42") is True


def test_ip_is_vpn():
    from unittest.mock import patch, MagicMock

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = _make_ip_response(
        classification="vpn", signals={"is_vpn": True}
    )
    mock_resp.headers = {}

    with patch("sec4dev.ip.request", return_value=(mock_resp, {})):
        client = Sec4DevClient("sec4_test")
        assert client.ip.is_vpn("203.0.113.42") is True


def test_ip_is_residential():
    from unittest.mock import patch, MagicMock

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = _make_ip_response(
        classification="residential", signals={"is_residential": True}
    )
    mock_resp.headers = {}

    with patch("sec4dev.ip.request", return_value=(mock_resp, {})):
        client = Sec4DevClient("sec4_test")
        assert client.ip.is_residential("203.0.113.42") is True


def test_ip_check_invalid_ip_raises():
    client = Sec4DevClient("sec4_test")
    with pytest.raises(ValidationError):
        client.ip.check("not-an-ip")
    with pytest.raises(ValidationError):
        client.ip.check("")
    with pytest.raises(ValidationError):
        client.ip.check("256.1.1.1")


def test_ip_check_accepts_ipv6():
    from unittest.mock import patch, MagicMock

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = _make_ip_response(ip="::1", classification="unknown")
    mock_resp.headers = {}

    with patch("sec4dev.ip.request", return_value=(mock_resp, {})):
        client = Sec4DevClient("sec4_test")
        result = client.ip.check("::1")
    assert result.ip == "::1"
