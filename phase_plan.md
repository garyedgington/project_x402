# Project x402 — Phase Plan

_Last updated: 2026-05-11 — Phase 6 in progress_

## Project Goal

Build a machine-native paid API service that performs one narrow, useful task and receives micropayments through x402 or similar payment rails. Use the first endpoint to prove demand, economics, reliability, and agent/developer usability before expanding into a portfolio of paid microservices.

## Phase 0 — Scope and Compliance Gate [LIGHT]

**Objective:** Make sure the project is aimed at allowed, agent-native services rather than prohibited platform automation.

**Tasks:**

- Define the service as an owned paid API endpoint.
- Exclude surveys, ad clicks, CAPTCHA solving, fake engagement, referral farming, and ToS-violating automation.
- Write basic acceptable-use rules for the endpoint.
- Confirm the initial service is intended for software agents, developers, and automated systems.

**Exit criteria:**

- Written project scope exists.
- Prohibited uses are explicitly excluded.
- First endpoint candidate is selected.

## Phase 1 — First Endpoint Definition: SchemaCheck Agent [LIGHT]

**Objective:** Specify the smallest useful version of SchemaCheck Agent.

**Tasks:**

- Define request schema: JSON schema, payload, strictness setting.
- Define response schema: valid boolean, errors, optional fixed payload, confidence score.
- Decide which features are deterministic and which require AI.
- Define pricing target: approximately $0.001 to $0.01 per call.
- Define success metrics: validation accuracy, latency, cost per call, payment success, repeat calls.

**Exit criteria:**

- API contract is written.
- Example requests and responses are written.
- MVP feature list is frozen.

## Phase 2 — Build Local MVP [COMPLETE ✓]

**Objective:** Build a local API that validates payloads and returns useful, predictable responses.

**Tasks:**

- Create project repository and folder structure.
- Build API server.
- Implement JSON schema validation.
- Implement structured error reporting.
- Add optional payload repair or suggested correction.
- Add basic logging for each request.
- Add test cases for valid, invalid, malformed, and edge-case payloads.

**Exit criteria:**

- Local endpoint works.
- Test suite passes.
- Validation behavior is deterministic enough to trust.

## Phase 3 — Payment Gate Integration [COMPLETE ✓]

**Objective:** Add x402-style payment gating so each call requires payment before access.

**Tasks:**

- Integrate the x402 or equivalent payment middleware.
- Configure USDC or selected stablecoin payment flow.
- Return proper `402 Payment Required` behavior for unpaid requests.
- Confirm paid requests complete and return service output.
- Log payment status alongside service output.

**Exit criteria:**

- Unpaid request is blocked.
- Paid request succeeds.
- Payment, request, and response are correlated in logs.

## Phase 4 — Deploy Public Test Endpoint [COMPLETE ✓]

**Objective:** Make SchemaCheck Agent callable by external agents and developers.

**Tasks:**

- Deploy API to a low-cost host.
- Configure environment variables and secrets.
- Add health check endpoint.
- Add rate limits and basic abuse protection.
- Publish simple documentation.
- Publish machine-readable examples.

**Exit criteria:**

- Public endpoint is reachable.
- Health check works.
- Docs are sufficient for an external caller to use the service.

## Phase 5 — Measurement and Economics [COMPLETE ✓]

**Objective:** Determine whether the endpoint can be economically positive.

**Tasks:**

- Track calls, revenue, cost, latency, errors, and payment failures.
- Calculate net margin per call.
- Identify top validation failure types.
- Identify whether callers repeat usage.
- Compare deterministic-only mode vs. AI-assisted mode if applicable.

**Exit criteria:**

- At least one full measurement report exists.
- Unit economics are known.
- Clear decision exists: continue, revise, or stop.

## Phase 6 — Distribution Test [IN PROGRESS]

**Objective:** Find out whether agents or developers will actually call the endpoint.

**Tasks:**

- Publish the service in relevant developer/agent communities or registries.
- Create concise docs aimed at autonomous callers.
- Create examples for common use cases.
- Offer test credits or very low-cost usage if needed.
- Track which distribution channels produce calls.

**Exit criteria:**

- At least one external caller has used the endpoint, or the project has evidence that the current distribution path is ineffective.
- Documentation gaps are identified and corrected.

## Phase 7 — Improve or Adjacent Expansion Gate [HEAVY]

**Objective:** Decide whether to deepen SchemaCheck Agent or add one adjacent endpoint.

**Decision criteria:**

Continue improving SchemaCheck Agent if:

- There is repeat usage.
- Errors show fixable quality gaps.
- Unit economics are neutral or positive.
- Users need stronger validation, correction, or API-contract support.

Add an adjacent endpoint only if usage points to it, such as:

- API response validator
- JSON repair endpoint
- OpenAPI contract checker
- Payload normalizer
- Test-case generator

Stop or pivot if:

- No external usage appears after distribution attempts.
- Payment friction is too high.
- Cost per call exceeds realistic pricing.
- The endpoint is too generic to attract repeat callers.

**Exit criteria:**

- One of three decisions is made: improve, expand, or pivot.

## Phase 8 — Portfolio Loop [HEAVY]

**Objective:** Turn the working pattern into a small portfolio of paid machine-native endpoints.

**Tasks:**

- Reuse payment, logging, docs, and deployment infrastructure.
- Add only narrow services with measurable output quality.
- Maintain separate metrics per endpoint.
- Kill endpoints that do not show usage or positive economics.
- Compound revenue into better monitoring, reliability, and new endpoint experiments.

**Exit criteria:**

- At least two endpoints are live and measured separately.
- The project has a repeatable build → gate → deploy → measure → improve loop.

