# Nymrel MarketProof

MarketProof is a read-only evidence layer for CoinMarketCap market data. It turns a bounded API response into a deterministic receipt containing source, endpoint, request shape, capture time, freshness, normalized observations, and a SHA-256 digest.

This repository was created after the official Build with CMC 2026 window opened. See `BUILD_KICKOFF.md` and `docs/ORIGINALITY.md`.

## Current boundary

The current implementation uses only CoinMarketCap's Keyless Public API. It does not require or read an API key and never sends an `X-CMC_PRO_API_KEY` header.

Permanent product boundary:

- read market evidence only
- no trading or order placement
- no brokerage or exchange mutation
- no wallet signing or token transfer
- no payment or x402 execution
- fail closed on malformed, stale, partial, mismatched, or API-error responses

## First proof

The initial proof uses `GET /public-api/v3/cryptocurrency/listings/latest` with a small bounded result set. Synthetic fixtures and schema tests are established before the first live capture.

## Run locally

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
python -m marketproof.cli capture --limit 3
```

The capture command writes a normalized evidence packet and receipt under `artifacts/live/`. It refuses authenticated URLs and never consumes local secrets.

## External gates still separate

The build does not imply hackathon registration or Startup-tier entitlement. Those require a CMC API account plus DoraHacks registration with the matching CMC account email. Publication and submission artifacts remain separate release actions.

## Intended hackathon track

**AI Agents & Automation.** The useful primitive is not another price table; it is provenance-aware market evidence an agent can inspect, cite, compare, and reject when the source is stale or structurally invalid.

## Live demo

- Public demo: https://nymrel.github.io/nymrel-marketproof/
- Public repository: https://github.com/nymrel/nymrel-marketproof
- Hosted CI: passing on current main
- Demo video: https://nymrel.github.io/nymrel-marketproof/assets/marketproof-demo.mp4
