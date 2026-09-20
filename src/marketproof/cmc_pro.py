"""Secret-safe request builder for the authenticated CoinMarketCap API.

This module prepares the campaign-issued-key path but does not read environment
variables, persist credentials, or perform network I/O by itself.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Callable

PRO_BASE = "https://pro-api.coinmarketcap.com"
QUOTES_PATH = "/v2/cryptocurrency/quotes/latest"
_ALLOWED_PATHS = {QUOTES_PATH}


class CMCProError(RuntimeError):
    """Fixed public failures that never include provider bodies or secrets."""


Opener = Callable[..., Any]


def build_request(
    path: str,
    *,
    cmc_id: str,
    currency: str,
    api_key: str,
) -> urllib.request.Request:
    if path not in _ALLOWED_PATHS:
        raise CMCProError("unsupported authenticated path")
    if not isinstance(cmc_id, str) or not cmc_id.isascii() or not cmc_id.isdigit():
        raise CMCProError("invalid CMC asset identifier")
    if not 1 <= int(cmc_id) <= 2_147_483_647 or len(cmc_id) > 10:
        raise CMCProError("invalid CMC asset identifier")
    if (
        not isinstance(currency, str)
        or not currency.isascii()
        or not currency.isalpha()
        or not 3 <= len(currency) <= 10
        or currency != currency.upper()
    ):
        raise CMCProError("invalid quote currency")
    if not isinstance(api_key, str) or not 8 <= len(api_key) <= 256:
        raise CMCProError("invalid API key")

    query = urllib.parse.urlencode({"id": cmc_id, "convert": currency})
    return urllib.request.Request(
        f"{PRO_BASE}{path}?{query}",
        headers={"Accept": "application/json", "X-CMC_PRO_API_KEY": api_key},
        method="GET",
    )


def fetch_pro_json(
    request: urllib.request.Request,
    *,
    opener: Opener | None = None,
    timeout_seconds: float = 10.0,
) -> dict[str, Any]:
    if not isinstance(request, urllib.request.Request):
        raise CMCProError("invalid request")
    if request.full_url.split("?", 1)[0] != f"{PRO_BASE}{QUOTES_PATH}":
        raise CMCProError("unsupported authenticated URL")
    if not isinstance(timeout_seconds, (int, float)) or isinstance(timeout_seconds, bool):
        raise CMCProError("invalid timeout")
    if not 1 <= float(timeout_seconds) <= 30:
        raise CMCProError("invalid timeout")

    open_request = opener or urllib.request.urlopen
    try:
        with open_request(request, timeout=float(timeout_seconds)) as response:
            if response.status != 200:
                raise CMCProError("authenticated request failed")
            raw = response.read()
    except CMCProError:
        raise
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError):
        raise CMCProError("authenticated request failed") from None

    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise CMCProError("authenticated response was not valid JSON") from None
    if not isinstance(payload, dict):
        raise CMCProError("authenticated response root must be an object")
    return payload
