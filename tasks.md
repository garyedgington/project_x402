# Project x402 — Phase 1 Task List

Status: Phase 6 in progress  
Owner: Developer  
Product owner: Gary  
Last updated: 2026-05-11

## Phase 1 Goal

Define the first product endpoint clearly enough that implementation can begin without ambiguity.

Endpoint: `POST /v1/schema-check`  
Product: SchemaCheck Agent  
MVP value: Validate JSON payloads against JSON Schema, return structured errors, explain failures, optionally suggest safe repairs.

## 1. Product Definition Tasks

- [x] Select first endpoint: SchemaCheck Agent.
- [x] Define endpoint path: `POST /v1/schema-check`.
- [x] Define required inputs: `json_schema`, `payload`.
- [x] Define optional inputs: `strictness`, `repair`, `explain`.
- [x] Define allowed strictness values: `strict`, `normal`, `lenient`.
- [x] Define response fields: `valid`, `errors`, `summary`, `suggested_payload`, `confidence`, `meta`.
- [x] Define normalized validation error codes.
- [x] Define API-level error response shape.
- [x] Define local MVP non-goals.

## 2. Documentation Tasks

- [x] Create `api_contract.md`.
- [x] Create `implementation_plan.md`.
- [x] Create `tasks.md`.
- [ ] Move API docs into `/docs` when a code repo is initialized.
- [ ] Add curl examples after local server exists.
- [ ] Add README quickstart after local server exists.

## 3. Engineering Setup Tasks — Next Phase

- [ ] Create Python project structure.
- [ ] Add `requirements.txt`.
- [ ] Add FastAPI app skeleton.
- [ ] Add Pydantic request/response models.
- [ ] Add deterministic schema validation module.
- [ ] Add error normalization module.
- [ ] Add deterministic explanation templates.
- [ ] Add conservative repair module.
- [ ] Add payment gate placeholder module.
- [ ] Add `.env.example`.
- [ ] Add local test suite.

## 4. MVP Test Tasks — Next Phase

- [ ] Test valid object payload.
- [ ] Test missing required field.
- [ ] Test wrong type.
- [ ] Test invalid enum.
- [ ] Test additional property.
- [ ] Test invalid strictness.
- [ ] Test missing `json_schema`.
- [ ] Test missing `payload`.
- [ ] Test `repair=false` behavior.
- [ ] Test safe deterministic repair behavior.

## 5. Payment Preparation Tasks — Later Phase

- [ ] Confirm x402 package/library/server middleware choice.
- [ ] Confirm supported network and receiving wallet.
- [ ] Confirm USDC settlement details.
- [ ] Add `402 Payment Required` behavior.
- [ ] Add payment verification middleware.
- [ ] Add pricing config, default target `$0.005` per request.
- [ ] Add request logging for paid calls.
- [ ] Add payment success/failure metrics.

## 6. Product Manager Inputs Needed Later

These are not blockers for Phase 1, but they will be needed before public deployment:

- [ ] Confirm preferred local development environment: Windows native, WSL, or cloud IDE.
- [ ] Confirm repository location when ready.
- [ ] Provide deployment target preference: Railway, Render, Fly.io, VPS, or other.
- [ ] Provide wallet/payment destination once payment integration begins.
- [ ] Decide whether first release is public, private test, or developer-preview only.

## Phase 1 Exit Checklist

- [x] API contract exists.
- [x] Implementation plan exists.
- [x] Build task list exists.
- [x] MVP scope is constrained to one endpoint.
- [x] Payment gating is treated as a wrapper, not core validator logic.
- [x] Phase 2 can begin.

## Developer Recommendation

Proceed to Phase 2: local MVP implementation.

Start with deterministic validation only. Do not add AI repair or payment gating until the base endpoint is stable and tested.

## Phase 3.6 — Guarded Real x402 Flow

Status: COMPLETE ✓ (2026-05-11)

- Added `X-PAYMENT` and `PAYMENT-SIGNATURE` handling for x402 v2 mode.
- Added x402 v2 PaymentRequired response (accepts array with asset/amount/payTo).
- Added EIP-712 domain extra: `{"name": "USDC", "version": "2"}` for Base Sepolia USDC.
- Added `HTTPFacilitatorClientSync` + `x402ResourceServerSync` for sync FastAPI endpoints.
- Live verification enabled via `SCHEMACHECK_X402_REAL_VERIFICATION_ENABLED=true` on Railway.

## Phase 4 — Railway Deployment

Status: COMPLETE ✓ (2026-05-11)

- `railway.toml`, `Procfile` committed and deployed.
- Fixed UTF-16 BOM encoding on `requirements.txt` (root cause of 15+ build failures).
- Fixed Railway branch tracking: set to `master`.
- Pushed full codebase (app/, tests/, docs/) to GitHub.
- Changed `x402==2.9.0` → `x402[evm]==2.9.0` to enable EVM verification on Railway.
- Public URL: https://projectx402-production.up.railway.app
- Health check: `/health` returns version 0.3.0.
- Payment mode: `SCHEMACHECK_PAYMENT_MODE=x402` (live on Railway).

## Phase 5 — First Live x402 Testnet Payment

Status: COMPLETE ✓ (2026-05-11)

- Test wallet: `0x272DDa1C5caC775752ab8432A50dfD8ed2d4001B`
- Funded via Coinbase Developer Platform faucet (Circle faucet unreliable).
- Ran `test_payment.py` — full x402 v2 flow end-to-end:
  - 402 received with PAYMENT-REQUIRED header and x402Version=2
  - EIP-3009 payment signed and sent as PAYMENT-SIGNATURE
  - Facilitator verified and settled on Base Sepolia
  - 200 returned: `"valid": true, "summary": "Payload is valid against the supplied JSON Schema."`
- Payment amount: 5000 atomic units = $0.005 USDC on Base Sepolia testnet.

Next phase: Phase 6 — Distribution and external caller measurement.

## Phase 6 — Distribution Test

Status: IN PROGRESS (started 2026-05-11)

Completed so far:
- Added `POST /v1/schema-check/trial` — free endpoint, no payment, 32KB limit, no repair suggestions.
- Rewrote `README.md` as public-facing doc with live URL, curl quickstart, trial vs paid endpoints.
- Created `docs/agent_quickstart.md` — full agent integration guide with x402 payment examples, Python snippets, use cases.
- Created `docs/distribution_plan.md` — target audiences, channel priority list, tracking table, messaging guide.

Remaining (user-side outreach actions):
- [x] GitHub repo made public
- [x] Trial endpoint deployed to Railway (pushed to master)
- [x] Set GitHub repo topics: json, jsonschema, x402, fastapi, micropayments, validation, usdc, base
- [x] Set up UptimeRobot monitor for /health endpoint (HEAD fix pushed 2026-05-11)
- [x] Switched to Base mainnet — network, USDC asset, CDP facilitator, EIP-712 domain
- [ ] Fund test wallet with Base mainnet USDC and run mainnet payment test
- [ ] Verify Bazaar indexing at CDP discovery endpoint after first mainnet payment
- [ ] Post in Coinbase/Base CDP Discord (discord.gg/cdp)
- [ ] Submit Show HN (Tuesday–Thursday 9–11am Eastern)
- [ ] Publish Dev.to article
- [ ] Post in r/Python and r/webdev Reddit
- [ ] Post trial link in AI agent Discord servers
- [ ] Record first week call counts in distribution_plan.md tracking table

## Phase 5 — Measurement and Economics

Status: COMPLETE ✓ (2026-05-11)

- Measurement report written: `phase5_measurement_report.md`
- Unit economics confirmed: $0.005 revenue/call, ~$0.000 marginal compute cost, break-even at ~1,000 calls/month on ~$5/month Railway hosting.
- Payment flow confirmed end-to-end: 1/1 testnet payments succeeded.
- Validation behavior confirmed correct across all test cases.
- Decision recorded: Continue to Phase 6. Economics are not the constraint — distribution is.

