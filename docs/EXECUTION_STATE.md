# Execution State — 2026-09-20

## Verified complete

- Official build window remains open through September 30, 2026 at 23:59 UTC.
- Public MIT repository: https://github.com/nymrel/nymrel-marketproof
- Public Pages demo: https://nymrel.github.io/nymrel-marketproof/
- Public demo video: https://nymrel.github.io/nymrel-marketproof/assets/marketproof-demo.mp4
- First bounded credential-free CoinMarketCap capture succeeded and its source response, normalized evidence, hashes, and deterministic receipt are committed.
- The authenticated client for `/v2/cryptocurrency/quotes/latest` is merged on `main`. It is disabled by default, accepts a key only at an explicit call boundary, and has no environment/account reads, persistence, logging, or autonomous live call.
- Exact-head hosted CI for the authenticated client passed the full suite and compilation on Python 3.11 and 3.13.

## Still externally gated

- Existing DoraHacks account: original login method and identity must be verified; login presents a mandatory human-verification challenge that automation will not bypass.
- Existing CoinMarketCap API account: matching account email and campaign-issued access are not verified.
- Event registration and Startup-tier/campaign entitlement: not verified.
- Authenticated live proof: not run. A sanitized receipt must not be claimed until one bounded call succeeds with the verified campaign key.
- Final DoraHacks submission URL and required X post: pending.

## Current safe lane

Maintain the public code, tests, evidence schema, deterministic receipts, fail-closed validation, demo, and submission documentation. Do not create duplicate accounts, expose a key, claim registration or entitlement, or publish the final X post before the real DoraHacks submission URL exists.

After human verification and matching-account confirmation:

1. Complete event registration.
2. Confirm campaign-issued access on the existing CMC key.
3. Run one bounded authenticated proof.
4. Commit only sanitized response evidence, hashes, and receipt metadata.
5. Refresh the public demo and submission packet.
6. Submit on DoraHacks and record the receipt.
7. Publish the prepared X post with the real submission and demo links.

## Durable receipts

- Keyless evidence SHA-256: `82346b3688674e24fe54f8ca38f4c8ed4183d6198cabe6263deeebda9d1bb371`
- Keyless source-response SHA-256: `74daaccd1a2d1d6cc6d412109d03f2e2804871b821cf7d5f97bda9d75ce622c2`
- Authenticated-client PR: https://github.com/nymrel/nymrel-marketproof/pull/1
- Authenticated-client merge: `67136ceabfce4ea1edd7e4a5a21b6355050dbb56`
- Exact-head CI: https://github.com/nymrel/nymrel-marketproof/actions/runs/35503053538
