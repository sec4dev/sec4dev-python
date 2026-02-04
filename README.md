# Sec4Dev Python SDK

Python client for the [Sec4Dev Security Checks API](https://api.sec4.dev): disposable email detection and IP classification.

## Documentation

Full API documentation: [https://docs.sec4.dev/](https://docs.sec4.dev/)

## Install

```bash
pip install -e .
```

## Usage

```python
from sec4dev import Sec4DevClient
from sec4dev.exceptions import RateLimitError, ValidationError

client = Sec4DevClient("sec4_your_api_key")

# Email check
try:
    result = client.email.check("user@tempmail.com")
    if result.is_disposable:
        print(f"Blocked: {result.domain} is a disposable domain")
except ValidationError as e:
    print(f"Invalid email: {e.message}")

# IP check
try:
    result = client.ip.check("203.0.113.42")
    print(f"IP Type: {result.classification}")
    print(f"Confidence: {result.confidence:.0%}")
    if result.signals.is_hosting:
        print(f"Hosting provider: {result.network.provider}")
except RateLimitError as e:
    print(f"Rate limited. Retry in {e.retry_after}s")
```

## Options

- `base_url` — API base URL (default: `https://api.sec4.dev/api/v1`)
- `timeout` — Request timeout in ms (default: 30000)
- `retries` — Retry attempts (default: 3)
- `retry_delay` — Base retry delay in ms (default: 1000)
- `on_rate_limit` — Optional callback for rate limit updates after each request
