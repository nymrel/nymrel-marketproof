# Nymrel MarketProof

MarketProof is a read-only evidence layer for CoinMarketCap market data. It turns a bounded API response into a deterministic receipt containing source, endpoint, request shape, capture time, freshness, normalized observations, and a SHA-256 digest.

This repository was created after the official Build with CMC 2026 window opened. See `BUILD_KICKOFF.md` and `docs/ORIGINALITY.md`.

## Current boundary

MarketProof has two intentionally separate read-only paths:

- The shipped capture CLI uses CoinMarketCap's Keyless Public API. It does not require or read an API key and never sends an `X-CMC_PRO_API_KEY` header.
- The authenticated client in `src/marketproof/cmc_pro.py` is opt-in preparation for the organizer-required campaign proof. It accepts a caller-supplied key only at the explicit call boundary, sends it only in the `X-CMC_PRO_API_KEY` header, and does not read accounts, environment variables, files, logs, or persistent storage.

No authenticated live call or campaign entitlement is claimed until a sanitized receipt is committed.

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

The capture command writes a normalized evidence packet and receipt under `artifacts/live/`. It refuses authenticated URLs and never consumes local secrets. The authenticated client is a tested library boundary only; it is not invoked by this command and performs no autonomous network action.

## External gates still separate

The public repository, Pages demo, and demo video are live. They do not imply hackathon registration, Startup-tier entitlement, or authenticated-key compliance. Those still require the existing CMC API account plus DoraHacks registration with the matching CMC account email, mandatory human verification, and one bounded campaign-key proof. Final DoraHacks submission and the required X post remain separate release actions.

## Intended hackathon track

**AI Agents & Automation.** The useful primitive is not another price table; it is provenance-aware market evidence an agent can inspect, cite, compare, and reject when the source is stale or structurally invalid.

## Live demo

- Public demo: https://nymrel.github.io/nymrel-marketproof/
- Public repository: https://github.com/nymrel/nymrel-marketproof
- Hosted CI: passing on current main
- Demo video: https://nymrel.github.io/nymrel-marketproof/assets/marketproof-demo.mp4
