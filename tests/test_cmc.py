from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from marketproof.cmc import CMCRequestError, LISTINGS_PATH, build_url, fetch_keyless_json


class FakeResponse:
    status = 200

    def __init__(self, payload: dict) -> None:
        self._raw = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self) -> bytes:
        return self._raw


class CMCTests(unittest.TestCase):
    def test_build_url_stays_keyless(self) -> None:
        url = build_url(LISTINGS_PATH, {"start": 1, "limit": 3, "convert": "USD"})
        self.assertIn("/public-api/v3/cryptocurrency/listings/latest", url)
        self.assertIn("limit=3", url)

    def test_rejects_unapproved_path(self) -> None:
        with self.assertRaisesRegex(CMCRequestError, "unsupported"):
            build_url("/v1/account", {})

    def test_fetch_sends_no_api_key_header(self) -> None:
        payload = {"status": {"error_code": 0}, "data": []}
        with patch(
            "marketproof.cmc.urllib.request.urlopen",
            return_value=FakeResponse(payload),
        ) as mocked:
            _, received = fetch_keyless_json(LISTINGS_PATH, {"limit": 1})
        request = mocked.call_args.args[0]
        lowered = {key.lower() for key in request.headers}
        self.assertNotIn("x-cmc_pro_api_key", lowered)
        self.assertEqual(received, payload)


if __name__ == "__main__":
    unittest.main()
