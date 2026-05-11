# Project x402 — Phase 1 Task List

Status: Phase 1 baseline  
Owner: Developer  
Product owner: Gary  
Last updated: 2026-05-09

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

Status: complete in sandbox.

- Added `X-PAYMENT` handling for x402 mode.
- Added x402-shaped `402 Payment Required` response.
- Added payment requirements for Base Sepolia testnet.
- Added guarded SDK verification path.
- Kept live verification disabled by default.
- Added tests for missing payTo, unpaid x402 request, and guarded payment payload.

## Phase 4.1 — Railway Deployment Prep

Status: complete in sandbox.

Build:
- Added `railway.toml`.
- Added `Procfile`.
- Added `docs/railway_deployment.md`.

Test:
- Local automated tests still pass.

Next human action:
- Replace local folder with the Phase 4.1 package.
- Run tests locally.
- Commit and push deployment files.
- Connect GitHub repo to Railway.

