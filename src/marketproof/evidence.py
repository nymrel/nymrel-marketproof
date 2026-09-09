"""Strict normalization and deterministic receipts for MarketProof."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any


class EvidenceError(ValueError):
    """Raised when source evidence is incomplete, stale, or inconsistent."""


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _parse_utc(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise EvidenceError(f"{field} must be a non-empty ISO timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise EvidenceError(f"{field} is not a valid ISO timestamp") from exc
    if parsed.tzinfo is None:
        raise EvidenceError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc)


def _require_mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise EvidenceError(f"{field} must be an object")
    return value


def _require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise EvidenceError(f"{field} must be non-empty text")
    return value.strip()


def _require_number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise EvidenceError(f"{field} must be numeric")
    number = float(value)
    if number < 0:
        raise EvidenceError(f"{field} cannot be negative")
    return number


def _normalize_row(row: Any, index: int) -> dict[str, Any]:
    item = _require_mapping(row, f"data[{index}]")
    asset_id = item.get("id")
    if isinstance(asset_id, bool) or not isinstance(asset_id, int) or asset_id <= 0:
        raise EvidenceError(f"data[{index}].id must be a positive integer")
    name = _require_text(item.get("name"), f"data[{index}].name")
    symbol = _require_text(item.get("symbol"), f"data[{index}].symbol").upper()
    quotes = item.get("quote")
    if not isinstance(quotes, list) or not quotes:
        raise EvidenceError(f"data[{index}].quote must be a non-empty list")
    usd = next(
        (
            _require_mapping(value, f"data[{index}].quote[]")
            for value in quotes
            if isinstance(value, dict) and str(value.get("symbol", "")).upper() == "USD"
        ),
        None,
    )
    if usd is None:
        raise EvidenceError(f"data[{index}].quote must contain a USD quote")
    price = _require_number(usd.get("price"), f"data[{index}].quote[USD].price")
    last_updated = _require_text(
        usd.get("last_updated"), f"data[{index}].quote[USD].last_updated"
    )
    _parse_utc(last_updated, f"data[{index}].quote[USD].last_updated")

    observation = {
        "cmc_id": asset_id,
        "name": name,
        "symbol": symbol,
        "price_usd": price,
        "last_updated": last_updated,
    }
    if usd.get("market_cap") is not None:
        observation["market_cap_usd"] = _require_number(
            usd.get("market_cap"), f"data[{index}].quote.USD.market_cap"
        )
    return observation


def build_evidence_packet(
    payload: dict[str, Any],
    *,
    endpoint: str,
    query: dict[str, str | int],
    captured_at: datetime | None = None,
    max_age_seconds: int = 300,
    expected_count: int | None = None,
    expected_symbols: set[str] | None = None,
) -> dict[str, Any]:
    root = _require_mapping(payload, "response")
    status = _require_mapping(root.get("status"), "status")
    if str(status.get("error_code")) != "0":
        raise EvidenceError(
            f"CMC status error: {status.get('error_code')} {status.get('error_message')}"
        )
    source_time = _parse_utc(status.get("timestamp"), "status.timestamp")
    observed_at = (captured_at or datetime.now(timezone.utc)).astimezone(timezone.utc)
    age_seconds = (observed_at - source_time).total_seconds()
    if age_seconds < -30:
        raise EvidenceError("CMC source timestamp is implausibly in the future")
    if age_seconds > max_age_seconds:
        raise EvidenceError(
            f"CMC response is stale: {age_seconds:.1f}s > {max_age_seconds}s"
        )

    rows = root.get("data")
    if not isinstance(rows, list) or not rows:
        raise EvidenceError("data must be a non-empty list")
    observations = [_normalize_row(row, index) for index, row in enumerate(rows)]
    if expected_count is not None and len(observations) != expected_count:
        raise EvidenceError(
            f"observation count mismatch: expected {expected_count}, got {len(observations)}"
        )
    if expected_symbols is not None:
        actual_symbols = {item["symbol"] for item in observations}
        normalized_expected = {symbol.upper() for symbol in expected_symbols}
        if actual_symbols != normalized_expected:
            raise EvidenceError(
                f"symbol mismatch: expected {sorted(normalized_expected)}, "
                f"got {sorted(actual_symbols)}"
            )

    return {
        "schema_version": "marketproof.v1",
        "source": "CoinMarketCap Keyless Public API",
        "endpoint": endpoint,
        "query": dict(sorted(query.items())),
        "captured_at": observed_at.isoformat().replace("+00:00", "Z"),
        "source_timestamp": source_time.isoformat().replace("+00:00", "Z"),
        "freshness_seconds": round(max(age_seconds, 0.0), 3),
        "observations": observations,
    }


def build_receipt(raw_payload: dict[str, Any], evidence_packet: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "marketproof.receipt.v1",
        "source_response_sha256": _sha256(raw_payload),
        "evidence_sha256": _sha256(evidence_packet),
        "captured_at": evidence_packet["captured_at"],
        "endpoint": evidence_packet["endpoint"],
        "query": evidence_packet["query"],
    }
