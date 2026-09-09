from __future__ import annotations

import copy
import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from marketproof.evidence import EvidenceError, build_evidence_packet, build_receipt


class EvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        fixture = ROOT / "tests" / "fixtures" / "listings.synthetic.json"
        self.payload = json.loads(fixture.read_text(encoding="utf-8"))
        self.now = datetime(2026, 9, 9, 5, 40, 10, tzinfo=timezone.utc)
        self.query = {"start": 1, "limit": 3, "convert": "USD"}

    def build(self, payload=None, **kwargs):
        return build_evidence_packet(
            payload or self.payload,
            endpoint="https://pro-api.coinmarketcap.com/public-api/v3/cryptocurrency/listings/latest",
            query=self.query,
            captured_at=self.now,
            expected_count=3,
            **kwargs,
        )

    def test_valid_fixture_normalizes(self) -> None:
        evidence = self.build(expected_symbols={"BTC", "ETH", "SOL"})
        self.assertEqual(evidence["schema_version"], "marketproof.v1")
        self.assertEqual(len(evidence["observations"]), 3)
        self.assertEqual(evidence["observations"][0]["symbol"], "BTC")
        self.assertEqual(evidence["freshness_seconds"], 10.0)

    def test_receipt_is_deterministic(self) -> None:
        evidence = self.build()
        first = build_receipt(self.payload, evidence)
        second = build_receipt(copy.deepcopy(self.payload), copy.deepcopy(evidence))
        self.assertEqual(first, second)
        self.assertEqual(len(first["source_response_sha256"]), 64)
        self.assertEqual(len(first["evidence_sha256"]), 64)

    def test_rejects_stale_response(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["status"]["timestamp"] = "2026-09-09T05:00:00Z"
        with self.assertRaisesRegex(EvidenceError, "stale"):
            self.build(payload)

    def test_rejects_api_error(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["status"]["error_code"] = 1008
        payload["status"]["error_message"] = "rate limit"
        with self.assertRaisesRegex(EvidenceError, "CMC status error"):
            self.build(payload)

    def test_rejects_partial_observation(self) -> None:
        payload = copy.deepcopy(self.payload)
        del payload["data"][1]["quote"][0]["price"]
        with self.assertRaisesRegex(EvidenceError, "price"):
            self.build(payload)

    def test_rejects_count_mismatch(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["data"] = payload["data"][:2]
        with self.assertRaisesRegex(EvidenceError, "count mismatch"):
            self.build(payload)

    def test_rejects_symbol_mismatch(self) -> None:
        with self.assertRaisesRegex(EvidenceError, "symbol mismatch"):
            self.build(expected_symbols={"BTC", "ETH", "XRP"})


if __name__ == "__main__":
    unittest.main()
