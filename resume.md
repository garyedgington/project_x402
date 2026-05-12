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
| Payment | x402 v2, USDC on Base mainnet (`eip155:8453`) |
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

**Completed this session:**
- [x] GitHub repo topics set: `json`, `jsonschema`, `x402`, `fastapi`, `micropayments`, `validation`, `usdc`, `base`
- [x] UptimeRobot monitor set up for `/health` (HEAD fix pushed to master)
- [x] Switched to Base mainnet: network `eip155:8453`, USDC asset, CDP facilitator
- [x] EIP-712 domain updated: `"USD Coin"` for mainnet
- [x] Bazaar extension confirmed present in 402 responses

**Outstanding (user-side actions):**
- [ ] Fund test wallet `0x272DDa1C5caC775752ab8432A50dfD8ed2d4001B` with USDC on Base mainnet (need >$0.01)
- [ ] Run `test_payment.py` updated for mainnet to trigger first payment and Bazaar indexing
- [ ] Post in Coinbase/Base CDP Discord — `discord.gg/cdp`
- [ ] Submit Show HN (best: Tuesday–Thursday 9–11am Eastern)
- [ ] Publish Dev.to article
- [ ] Post in r/Python and r/webdev
- [ ] Post trial link in AI agent Discord servers
- [ ] Record first week call counts in `docs/distribution_plan.md`

**Pending code change before mainnet payment test:**
- Update `test_payment.py`: change `NETWORK` to `eip155:8453` and confirm wallet has Base mainnet USDC

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
- Base mainnet (USDC payments, real money)
- x402 facilitator: `https://api.cdp.coinbase.com/platform/v2/x402` (CDP mainnet)

---

## Next session starting point

1. Fund test wallet with Base mainnet USDC and run `test_payment.py` (updated for mainnet) to trigger first real payment and Bazaar indexing.
2. Check Railway logs for any external calls — look for `POST /v1/schema-check status=200`.
3. Check Bazaar indexing: `Invoke-RestMethod -Uri "https://api.cdp.coinbase.com/platform/v2/x402/discovery/resources"` — look for `projectx402-production.up.railway.app`.
4. Execute remaining distribution posts from `docs/posts_draft.md`.
5. After one week, record call counts in `docs/distribution_plan.md` tracking table.
