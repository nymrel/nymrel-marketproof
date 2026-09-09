# MarketProof Agent Rules

This repository is an in-window Build with CMC 2026 project.

- Preserve the originality record in `BUILD_KICKOFF.md` and `docs/ORIGINALITY.md`.
- Keep market-data access read-only.
- Prefer CoinMarketCap keyless endpoints until authenticated access is separately authorized and evidenced.
- Never read, print, commit, or invent API keys.
- No trading, order placement, exchange mutation, wallet signing, token transfer, payment, or x402 execution.
- Validate external payloads strictly and fail closed on stale, malformed, partial, mismatched, or error responses.
- Every live proof must record endpoint, request shape, source timestamp, capture timestamp, and deterministic digest.
- Synthetic fixtures must be explicitly synthetic.
- Do not claim DoraHacks registration, Startup-tier access, public publication, deployment, social posting, or final submission without current external evidence.
- Local code, tests, docs, commits, and reversible implementation are the default safe lane.

Run `python -m unittest discover -s tests -v` before committing code changes.
