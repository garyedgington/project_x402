# Project x402 — Phase 1 Implementation Plan

Status: Phase 1 baseline  
Owner: Developer  
Product owner: Gary  
Last updated: 2026-05-09

## 1. Objective

Build the first working version of SchemaCheck Agent: a narrow API service that validates JSON payloads against JSON Schema and returns structured errors, explanations, and optional suggested repairs.

Phase 1 is definition and build preparation. Phase 2 should produce the local MVP.

## 2. Recommended Stack

### Backend

- Python 3.12+
- FastAPI
- Pydantic for request/response modeling
- `jsonschema` for deterministic validation
- Uvicorn for local serving
- Pytest for tests

### Optional AI Layer

For MVP, AI should be optional and isolated behind an interface.

Initial implementation can use deterministic explanations only. Add LLM-assisted repair later once the deterministic path is reliable.

Suggested interface:

```python
class RepairProvider:
    def suggest_repair(self, schema: dict, payload: object, errors: list[dict]) -> RepairResult:
        ...
```

### Payment Layer

Payment gating is a wrapper concern, not core validation logic.

Initial local MVP should use a placeholder middleware/interface:

```python
class PaymentGate:
    def verify(self, request) -> PaymentResult:
        ...
```

During local MVP, the payment gate can be disabled by environment variable:

```env
PAYMENT_GATE_ENABLED=false
```

## 3. Proposed Project Structure

```text
project_x402/
  app/
    __init__.py
    main.py
    models.py
    validator.py
    errors.py
    repair.py
    payment.py
  tests/
    test_schema_check_valid.py
    test_schema_check_invalid.py
    test_schema_check_api_errors.py
    test_repair.py
  docs/
    api_contract.md
  .env.example
  requirements.txt
  README.md
```

Note: The current sandbox workspace is `/mnt/data/project_x402/`. If this becomes a local repo later, use the structure above inside the repo root.

## 4. Core Components

### 4.1 FastAPI App

Responsibilities:

- Expose `POST /v1/schema-check`
- Validate request shape
- Call deterministic validator
- Optionally call repair provider
- Return contract-compliant response

### 4.2 Request/Response Models

Define Pydantic models for:

- `SchemaCheckRequest`
- `SchemaCheckResponse`
- `ValidationErrorItem`
- `ResponseMeta`
- `ApiErrorResponse`

Important: `payload` must allow any JSON value, not just objects.

### 4.3 Deterministic Validator

Responsibilities:

- Validate JSON Schema document if possible
- Validate payload against schema
- Normalize `jsonschema` errors into stable internal error codes
- Generate JSON Pointer paths such as `/email` or `/user/age`
- Return errors sorted deterministically

### 4.4 Explanation Layer

MVP should start with deterministic templates:

- required: `The payload is missing required field X.`
- type: `Field X expected type Y but received Z.`
- format: `Field X does not match required format Y.`
- additionalProperties: `Field X is not allowed by the schema.`

This avoids early LLM cost and makes tests stable.

### 4.5 Repair Layer

MVP repair should be conservative.

Allowed deterministic repair candidates:

- Remove additional properties when `additionalProperties=false`.
- Coerce string numbers to numbers only in `lenient` mode.
- Coerce string booleans `"true"`/`"false"` to booleans only in `lenient` mode.
- Add no fake required values unless a safe default is specified in schema.

For email, dates, names, companies, or semantic fields, return explanation but avoid fabricating values unless AI repair is explicitly enabled in a later phase.

## 5. Local Development Flow

1. Create virtual environment.
2. Install requirements.
3. Run tests.
4. Start local API.
5. Send example requests with curl or HTTP client.

Suggested commands once code exists:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
uvicorn app.main:app --reload
```

## 6. Test Plan

### Required Test Cases

1. Valid object payload returns `valid=true` and no errors.
2. Missing required field returns `required` error.
3. Wrong type returns `type` error.
4. Invalid enum returns `enum` error.
5. Additional property returns `additionalProperties` error.
6. Invalid strictness returns API error.
7. Missing `json_schema` returns API error.
8. Missing `payload` returns API error.
9. `repair=false` never returns suggested payload.
10. `repair=true` returns safe deterministic repair only when available.

### Useful Later Tests

- Format validation for email/date-time.
- Nested object path normalization.
- Array item validation.
- `oneOf`/`anyOf` behavior.
- Large payload limits.
- Payment required path.

## 7. Environment Variables

```env
APP_ENV=local
PAYMENT_GATE_ENABLED=false
DEFAULT_STRICTNESS=normal
MAX_REQUEST_BYTES=262144
ENABLE_AI_REPAIR=false
```

Later:

```env
ANTHROPIC_API_KEY=
X402_NETWORK=
X402_RECEIVING_ADDRESS=
X402_PRICE_USDC=0.005
```

## 8. MVP Pricing Placeholder

Recommended launch test price: `$0.005` per request.

Reasoning:

- High enough to measure payment behavior.
- Low enough for agent/developer experimentation.
- Compatible with the original target range of `$0.001–$0.01`.

Pricing remains inactive until payment gating phase.

## 9. Risks

| Risk | Mitigation |
|---|---|
| Scope creep into generic data cleaning | Keep one endpoint only. |
| LLM repair fabricates values | Deterministic repair first; AI repair off by default. |
| Payment layer changes API design | Keep payment as middleware/wrapper. |
| JSON Schema edge cases expand complexity | Support common cases first; document non-goals. |
| No clear buyer/user | Ship docs/examples for agents and developers early. |

## 10. Phase 1 Exit Criteria

Phase 1 is complete when:

- API contract is written.
- Implementation plan is written.
- Task list is written.
- MVP scope is frozen around `POST /v1/schema-check`.
- Phase 2 can begin without another product definition pass.
