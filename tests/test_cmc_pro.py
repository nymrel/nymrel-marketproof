from __future__ import annotations

import json
import sys
import unittest
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from marketproof.cmc_pro import CMCProError, QUOTES_PATH, build_request, fetch_pro_json

FIXTURE_KEY = "fixture-key-never-sent-live"


class FakeResponse:
    status = 200

    def __init__(self, payload: object) -> None:
        self._raw = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self) -> bytes:
        return self._raw


class CMCProTests(unittest.TestCase):
    def request(self):
        return build_request(
            QUOTES_PATH, cmc_id="1", currency="USD", api_key=FIXTURE_KEY
        )

    def test_exact_url_and_header(self):
        request = self.request()
        self.assertEqual(
            request.full_url,
            "https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest?id=1&convert=USD",
        )
        self.assertEqual(
            {key.lower(): value for key, value in request.header_items()}[
                "x-cmc_pro_api_key"
            ],
            FIXTURE_KEY,
        )
        self.assertNotIn(FIXTURE_KEY, request.full_url)

    def test_payload_is_returned(self):
        payload = {"status": {"error_code": 0}, "data": {"1": []}}
        seen = {}

        def opener(request, timeout):
            seen.update(request=request, timeout=timeout)
            return FakeResponse(payload)

        self.assertEqual(fetch_pro_json(self.request(), opener=opener), payload)
        self.assertEqual(seen["timeout"], 10.0)

    def test_fixed_error_does_not_echo_secret_or_provider_detail(self):
        def opener(_request, timeout):
            del timeout
            raise urllib.error.URLError(f"private:{FIXTURE_KEY}")

        with self.assertRaises(CMCProError) as raised:
            fetch_pro_json(self.request(), opener=opener)
        self.assertEqual(str(raised.exception), "authenticated request failed")
        self.assertNotIn(FIXTURE_KEY, str(raised.exception))

    def test_rejects_invalid_asset_ids(self):
        for value in ("", "0", "-1", "1.0", "abc", "00000000001", "2147483648"):
            with self.subTest(value=value), self.assertRaises(CMCProError):
                build_request(QUOTES_PATH, cmc_id=value, currency="USD", api_key=FIXTURE_KEY)

    def test_rejects_invalid_currencies(self):
        for value in ("usd", "US", "USD1", "U/S/D", "TOO-LONG-CODE"):
            with self.subTest(value=value), self.assertRaises(CMCProError):
                build_request(QUOTES_PATH, cmc_id="1", currency=value, api_key=FIXTURE_KEY)

    def test_rejects_invalid_keys_without_echo(self):
        for value in ("", "short", 123):
            with self.subTest(value=value), self.assertRaisesRegex(CMCProError, "invalid API key"):
                build_request(QUOTES_PATH, cmc_id="1", currency="USD", api_key=value)

    def test_rejects_unapproved_path(self):
        with self.assertRaisesRegex(CMCProError, "unsupported authenticated path"):
            build_request("/v1/account", cmc_id="1", currency="USD", api_key=FIXTURE_KEY)

    def test_rejects_unapproved_url(self):
        request = self.request()
        request.full_url = "https://example.com/"
        with self.assertRaisesRegex(CMCProError, "unsupported authenticated URL"):
            fetch_pro_json(request, opener=lambda *_args, **_kwargs: None)

    def test_timeout_is_bounded(self):
        for value in (True, 0, 31, "10"):
            with self.subTest(value=value), self.assertRaisesRegex(CMCProError, "invalid timeout"):
                fetch_pro_json(self.request(), opener=lambda *_args, **_kwargs: None, timeout_seconds=value)

    def test_non_object_payload_rejected(self):
        with self.assertRaisesRegex(CMCProError, "root must be an object"):
            fetch_pro_json(self.request(), opener=lambda *_args, **_kwargs: FakeResponse([]))


if __name__ == "__main__":
    unittest.main()
