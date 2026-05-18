# Project x402 — Session Resume

_Last updated: 2026-05-18_

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
| Deployment | Railway, auto-deploys from `main` branch |
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

**Completed in prior sessions:**
- [x] GitHub repo topics set: `json`, `jsonschema`, `x402`, `fastapi`, `micropayments`, `validation`, `usdc`, `base`
- [x] UptimeRobot monitor set up for `/health` (HEAD fix pushed to main)
- [x] Switched to Base mainnet: network `eip155:8453`, USDC asset, CDP facilitator
- [x] EIP-712 domain updated: `"USD Coin"` for mainnet
- [x] Bazaar extension present in 402 responses (initial non-conformant version)

**Completed 2026-05-18 session — Bazaar indexing achieved:**
- [x] Funded test wallet `0x272DDa1C5caC775752ab8432A50dfD8ed2d4001B` with 1 USDC on Base mainnet (sent directly from Coinbase exchange)
- [x] Added CDP authentication to facilitator client in `app/payment.py` — `_build_facilitator_config()` wraps `FacilitatorConfig` with `CreateHeadersAuthProvider` calling `cdp.auth.get_auth_headers` per request
- [x] Added `cdp-sdk>=1.45.0` to requirements.txt
- [x] Set Railway env vars `CDP_API_KEY_ID` and `CDP_API_KEY_SECRET` (multi-line PEM)
- [x] Replaced hand-written bazaar extension with canonical structure via `declare_discovery_extension` (with `method="POST"` injected manually)
- [x] First three mainnet $0.005 USDC payments settled successfully via CDP facilitator
- [x] SchemaCheck Agent indexed in CDP Bazaar discovery (verified at 2026-05-18T21:21:07Z, queryable within ~35 min of canonical-format payment)

**Outstanding (user-side actions for Phase 6 completion):**
- [ ] Post in Coinbase/Base CDP Discord — `discord.gg/cdp`
- [ ] Submit Show HN (best: Tuesday–Thursday 9–11am Eastern)
- [ ] Publish Dev.to article
- [ ] Post in r/Python and r/webdev
- [ ] Post trial link in AI agent Discord servers
- [ ] Record first-week call counts in `docs/distribution_plan.md`
- [ ] Monitor `quality.l30DaysTotalCalls` and `quality.l30DaysUniquePayers` on the Bazaar entry to track external traction

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
- Railway (hosting, auto-deploy from main)
- Base mainnet (USDC payments, real money)
- x402 facilitator: `https://api.cdp.coinbase.com/platform/v2/x402` (CDP mainnet)

---

## Next session starting point

1. Re-verify the Bazaar entry is still indexed and inspect its `quality` field for any external calls:
   ```powershell
   $found = @()
   for ($offset = 0; $offset -lt 50000; $offset += 100) {
       $page = Invoke-RestMethod -Uri "https://api.cdp.coinbase.com/platform/v2/x402/discovery/resources?limit=100&offset=$offset"
       $hits = $page.items | Where-Object { $_.resource -like "*projectx402-production*" }
       if ($hits) { $found += $hits; break }
       if ($page.items.Count -lt 100) { break }
   }
   $found | ConvertTo-Json -Depth 8
   ```
   Look at `quality.l30DaysTotalCalls`, `quality.l30DaysUniquePayers`, and `quality.lastCalledAt` to see if any external traffic has hit the endpoint.
2. Check Railway logs for external calls — look for `POST /v1/schema-check status=200` from IPs other than your test wallet's flow.
3. Execute remaining distribution posts from `docs/posts_draft.md` (Show HN, Dev.to, Reddit, Coinbase/Base Discord, AI agent Discords).
4. After one week of distribution, record call counts in `docs/distribution_plan.md` tracking table.
5. Consider setting up a recurring scheduled task (daily 9am local) to pull Bazaar entry quality stats and post a summary to chat so growth is visible at a glance.

---

## Wallet state at end of 2026-05-18 session

| Wallet | Address | Balance | Notes |
|---|---|---|---|
| Test/payer (key in `test_payment.py`) | `0x272DDa1C5caC775752ab8432A50dfD8ed2d4001B` | ~$0.985 USDC | Down from $1.00 after three settled $0.005 calls |
| Receiver / `payTo` (Coinbase Smart Wallet) | `0x8fC4006534801c17A3368075A1Fb3b3C511EdB1F` | $0.015 from x402 payments | Smart Wallet; gas sponsored via paymaster |
| Coinbase Wallet EOA (mrgedgy.cb.id, linked to exchange) | `0x9F40C27c7C502eDaD710a0D733c1a51a802892A6` | 1.00 USDC | Has no ETH, can't move USDC without funding ETH or sending via Coinbase exchange |
