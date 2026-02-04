"""IP check models."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel


class IPClassification(str, Enum):
    """IP classification type."""

    HOSTING = "hosting"
    RESIDENTIAL = "residential"
    MOBILE = "mobile"
    VPN = "vpn"
    TOR = "tor"
    PROXY = "proxy"
    UNKNOWN = "unknown"


class IPSignals(BaseModel):
    """Signals from IP check."""

    is_hosting: bool = False
    is_residential: bool = False
    is_mobile: bool = False
    is_vpn: bool = False
    is_tor: bool = False
    is_proxy: bool = False


class IPNetwork(BaseModel):
    """Network info from IP check."""

    asn: Optional[int] = None
    org: Optional[str] = None
    provider: Optional[str] = None


class IPGeo(BaseModel):
    """Geo info from IP check."""

    country: Optional[str] = None
    region: Optional[str] = None


class IPCheckResult(BaseModel):
    """Result of an IP check."""

    ip: str
    classification: str
    confidence: float
    signals: IPSignals
    network: IPNetwork
    geo: IPGeo
