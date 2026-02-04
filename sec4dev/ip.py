"""IP check service."""

from typing import Callable, Optional

from sec4dev.http import request
from sec4dev.models.ip import (
    IPCheckResult,
    IPGeo,
    IPNetwork,
    IPSignals,
)
from sec4dev.validation import validate_ip


class IPService:
    """Service for classifying IP addresses."""

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

    def check(self, ip: str) -> IPCheckResult:
        """Classify an IP address."""
        validate_ip(ip)
        url = f"{self._base_url}/ip/check"
        resp, _ = request(
            "POST",
            url,
            self._api_key,
            json={"ip": ip.strip()},
            timeout_ms=self._timeout_ms,
            retries=self._retries,
            retry_delay_ms=self._retry_delay_ms,
            on_rate_limit=self._on_rate_limit,
        )
        data = resp.json()
        signals = data.get("signals") or {}
        network = data.get("network") or {}
        geo = data.get("geo") or {}
        return IPCheckResult(
            ip=data.get("ip", ip),
            classification=data.get("classification", "unknown"),
            confidence=float(data.get("confidence", 0.0)),
            signals=IPSignals(
                is_hosting=signals.get("is_hosting", False),
                is_residential=signals.get("is_residential", False),
                is_mobile=signals.get("is_mobile", False),
                is_vpn=signals.get("is_vpn", False),
                is_tor=signals.get("is_tor", False),
                is_proxy=signals.get("is_proxy", False),
            ),
            network=IPNetwork(
                asn=network.get("asn"),
                org=network.get("org"),
                provider=network.get("provider"),
            ),
            geo=IPGeo(
                country=geo.get("country"),
                region=geo.get("region"),
            ),
        )

    def is_hosting(self, ip: str) -> bool:
        """Return True if the IP is classified as hosting."""
        return self.check(ip).signals.is_hosting

    def is_vpn(self, ip: str) -> bool:
        """Return True if the IP is classified as VPN."""
        return self.check(ip).signals.is_vpn

    def is_tor(self, ip: str) -> bool:
        """Return True if the IP is classified as TOR."""
        return self.check(ip).signals.is_tor

    def is_residential(self, ip: str) -> bool:
        """Return True if the IP is classified as residential."""
        return self.check(ip).signals.is_residential

    def is_mobile(self, ip: str) -> bool:
        """Return True if the IP is classified as mobile."""
        return self.check(ip).signals.is_mobile
