"""Command-line entry point for bounded MarketProof captures."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from .cmc import LISTINGS_PATH, fetch_keyless_json
from .evidence import build_evidence_packet, build_receipt


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def capture(limit: int, output_dir: Path) -> dict[str, Path]:
    if limit < 1 or limit > 10:
        raise ValueError("limit must be between 1 and 10")
    params: dict[str, str | int] = {"start": 1, "limit": limit, "convert": "USD"}
    url, payload = fetch_keyless_json(LISTINGS_PATH, params)
    captured_at = datetime.now(timezone.utc)
    evidence = build_evidence_packet(
        payload,
        endpoint=url.split("?", 1)[0],
        query=params,
        captured_at=captured_at,
        expected_count=limit,
    )
    receipt = build_receipt(payload, evidence)

    paths = {
        "response": output_dir / "cmc-listings-latest.response.json",
        "evidence": output_dir / "cmc-listings-latest.evidence.json",
        "receipt": output_dir / "cmc-listings-latest.receipt.json",
    }
    _write_json(paths["response"], payload)
    _write_json(paths["evidence"], evidence)
    _write_json(paths["receipt"], receipt)
    print(f"Captured {len(evidence['observations'])} observations from {url}")
    print(f"Evidence SHA-256: {receipt['evidence_sha256']}")
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description="Create read-only CMC evidence receipts")
    subparsers = parser.add_subparsers(dest="command", required=True)
    capture_parser = subparsers.add_parser("capture", help="capture bounded live CMC evidence")
    capture_parser.add_argument("--limit", type=int, default=3)
    capture_parser.add_argument(
        "--output-dir", type=Path, default=Path("artifacts/live")
    )
    args = parser.parse_args()

    if args.command == "capture":
        capture(args.limit, args.output_dir)
        return 0
    parser.error("unsupported command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
