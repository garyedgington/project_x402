# Project x402 — Session Resume

_Last updated: 2026-05-11_

---

## What this project is

Project x402 builds machine-native paid API endpoints monetized via x402 USDC micropayments. The first endpoint is **SchemaCheck Agent**: a JSON Schema validation service. Each call costs $0.005 USDC, paid automatically via the x402 protocol (HTTP 402 → EIP-3009 USDC → facilitator verify → 200).

The goal is a small portfolio of narrow, reliable paid microservices for AI agents and backend systems.

---

## Current status

**Phase 6 — Distribution Test: IN PROGRESS**

All phases through Phase 5 are complete. The service is live, the trial endpoint is deployed, docs are written, and posts are drafted. The only thing left is executing the outreach.

---

## Live service

| | |
|---|---|
| Base URL | `https://projectx402-production.up.railway.app` |
| Paid endpoint | `POST /v1/schema-check` — $0.005 USDC per call |
| Trial endpoint | `POST /v1/schema-check/trial` — free, 32KB limit, no repair |
| Health check | `GET /health` |
| GitHub | `https://github.com/garyedgington/project_x402` (public) |
| Deployment | Railway, auto-deploys from `master` branch |
| Payment | x402 v2, USDC on Base Sepolia testnet (`eip155:84532`) |
| Version | 0.3.0 |

---

## Phase history

| Phase | Status | Summary |
|---|---|---|
| 0 — Scope & compliance | COMPLETE ✓ | Project scope defined, prohibited uses excluded |
| 1 — Endpoint definition | COMPLETE ✓ | API contract written, MVP scope frozen |
| 2 — Local MVP | COMPLETE ✓ | FastAPI + jsonschema + Pydantic, test suite passing |
| 3 — Payment gate | COMPLETE ✓ | x402 v2 live verification via facilitator |
| 4 — Public deployment | COMPLETE ✓ | Railway deploy, health check, public docs |
| 5 — Measurement & economics | COMPLETE ✓ | First testnet payment confirmed, unit economics documented |
| 6 — Distribution test | IN PROGRESS | Prep complete, outreach not yet executed |

---

## Phase 6 — what's done and what's outstanding

**Done:**
- `POST /v1/schema-check/trial` free endpoint deployed
- `README.md` rewritten as public-facing doc with curl quickstart
- `docs/agent_quickstart.md` — full integration guide, x402 Python SDK examples
- `docs/distribution_plan.md` — channel priority list, tracking table
- `docs/posts_draft.md` — Show HN, Dev.to article, Reddit posts, Discord template
- `docs/uptime_monitoring.md` — UptimeRobot setup guide
- Bazaar discovery extension added to 402 responses
- GitHub repo made public

**Outstanding (user-side actions):**
- [ ] Set GitHub repo topics: `json`, `jsonschema`, `x402`, `fastapi`, `micropayments`, `validation`, `usdc`, `base`
- [ ] Post in Coinbase/Base CDP Discord — `discord.gg/cdp`
- [ ] Submit Show HN
- [ ] Publish Dev.to article
- [ ] Post in r/Python and r/webdev
- [ ] Post trial link in AI agent Discord servers
- [ ] Set up UptimeRobot monitor for `/health` (guide in `docs/uptime_monitoring.md`)
- [ ] Record first week call counts in `docs/distribution_plan.md`

**Phase 6 exit criteria:** at least one external caller, OR evidence the current distribution path is ineffective.

---

## Unit economics

| | |
|---|---|
| Revenue per call | $0.005 USDC |
| Marginal compute cost | ~$0.000 |
| Fixed cost | ~$5/month Railway |
| Break-even | ~1,000 calls/month |

---

## Key files

| File | Purpose |
|---|---|
| `README.md` | Public-facing quickstart |
| `api_contract.md` | Full API contract and error shape reference |
| `phase_plan.md` | Phase definitions and exit criteria |
| `tasks.md` | Phase-by-phase task log |
| `phase5_measurement_report.md` | Economics and measurement report |
| `docs/agent_quickstart.md` | Full integration guide with x402 SDK examples |
| `docs/distribution_plan.md` | Distribution channels, tracking table |
| `docs/posts_draft.md` | Ready-to-send posts for HN, Dev.to, Reddit, Discord |
| `docs/uptime_monitoring.md` | UptimeRobot setup guide |
| `docs/x402_real_flow.md` | x402 v2 payment flow details |
| `app/main.py` | FastAPI app — endpoints including trial |
| `app/payment.py` | x402 payment gate and 402 response builder |
| `app/validator.py` | JSON Schema validation and error normalisation |
| `app/config.py` | Settings loaded from environment |

---

## Stack

- Python, FastAPI, jsonschema, Pydantic
- x402[evm]==2.9.0 (EVM payment verification)
- Railway (hosting, auto-deploy from master)
- Base Sepolia testnet (USDC payments)
- x402 facilitator: `https://x402.org/facilitator`

---

## Next session starting point

1. Check whether any outreach from `docs/posts_draft.md` has been sent.
2. Check Railway logs / health endpoint for any external calls.
3. If outreach is done and calls have come in → mark Phase 6 complete, update `phase_plan.md` and `tasks.md`, proceed to Phase 7 decision.
4. If no calls after reasonable time → record in `docs/distribution_plan.md` as evidence of ineffective channel, try next channel, or escalate to Phase 7 pivot decision.
