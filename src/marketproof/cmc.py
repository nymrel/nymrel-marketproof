"""Bounded, keyless CoinMarketCap client for MarketProof."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

KEYLESS_BASE = "https://pro-api.coinmarketcap.com/public-api"
LISTINGS_PATH = "/v3/cryptocurrency/listings/latest"
_ALLOWED_PATHS = {LISTINGS_PATH}


class CMCRequestError(RuntimeError):
    """Raised when a keyless CMC request cannot be trusted."""


def build_url(path: str, params: dict[str, str | int]) -> str:
    if path not in _ALLOWED_PATHS:
        raise CMCRequestError(f"unsupported keyless path: {path}")
    query = urllib.parse.urlencode(params)
    return f"{KEYLESS_BASE}{path}?{query}"


def fetch_keyless_json(
    path: str,
    params: dict[str, str | int],
    *,
    timeout_seconds: float = 10.0,
) -> tuple[str, dict[str, Any]]:
    url = build_url(path, params)
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "Nymrel-MarketProof/0.1",
        },
        method="GET",
    )
    if "X-CMC_PRO_API_KEY" in request.headers:
        raise CMCRequestError("authenticated header is forbidden in keyless mode")

    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            if response.status != 200:
                raise CMCRequestError(f"unexpected HTTP status: {response.status}")
            raw = response.read()
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
        raise CMCRequestError(f"CMC keyless request failed: {exc}") from exc

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise CMCRequestError("CMC response was not valid JSON") from exc
    if not isinstance(payload, dict):
        raise CMCRequestError("CMC response root must be an object")
    return url, payload
