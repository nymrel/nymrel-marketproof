# Build with CMC 2026 Submission Packet

## Entry

- Project: **Nymrel MarketProof**
- Track: **AI Agents & Automation**
- Team: solo entry under the existing DoraHacks identity; public project brand is Nymrel
- Repository: https://github.com/nymrel/nymrel-marketproof
- Live demo: https://nymrel.github.io/nymrel-marketproof/
- Demo video: https://nymrel.github.io/nymrel-marketproof/assets/marketproof-demo.mp4
- License: MIT

## Pitch

MarketProof is a read-only evidence boundary for market-sensitive AI agents. It fetches a bounded CoinMarketCap response, normalizes observations, verifies freshness and structure, and emits deterministic SHA-256 receipts so an agent can distinguish observed API facts from downstream interpretation.

It never trades, signs a wallet, transfers tokens, pays an x402 request, or claims predictive certainty.
## CoinMarketCap API proof

Exact route used:

`GET https://pro-api.coinmarketcap.com/public-api/v3/cryptocurrency/listings/latest?start=1&limit=3&convert=USD`

The repository contains the captured source response, normalized evidence packet, deterministic receipt, synthetic fixtures, strict schema validation, and negative tests.

Accepted live evidence SHA-256:

`82346b3688674e24fe54f8ca38f4c8ed4183d6198cabe6263deeebda9d1bb371`

Source-response SHA-256:

`74daaccd1a2d1d6cc6d412109d03f2e2804871b821cf7d5f97bda9d75ce622c2`
## What the API enabled

CoinMarketCap's Keyless Public API made it possible to prove the full API-to-receipt path without creating or exposing credentials. The v3 listings response supplies current asset identity, USD quote, update timestamp, and market-cap fields that MarketProof can bind into a small provenance-aware evidence packet.

## API limitations encountered

The live v3 Keyless response uses a `quote[]` collection rather than the older nested `quote.USD` shape. The first live validation therefore failed closed until the schema was corrected and the full negative-test suite passed again. Keyless access also covers only selected routes and does not prove event Startup-tier entitlement; authenticated capability remains a separate account/registration step.

## Submission/X release gate

DoraHacks submission URL: **PENDING — do not fabricate**

After the real DoraHacks submission URL exists, publish this X copy with that URL inserted:

> Nymrel MarketProof gives AI agents timestamped, source-bound CoinMarketCap evidence before inference. Read-only, fail-closed, and backed by deterministic receipts. Demo: https://nymrel.github.io/nymrel-marketproof/assets/marketproof-demo.mp4 — Submission: <DORAHACKS_SUBMISSION_URL> #BuildwithCMC