# Project x402 — Local Runbook

## Purpose

Run the SchemaCheck Agent MVP locally, test the deterministic JSON Schema validator, and exercise the disabled or placeholder payment gate.

## Setup

```bash
cd project_x402
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
```

## Run API

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok","service":"schemacheck-agent","version":"0.2.0"}
```

## Call SchemaCheck

Valid payload:

```bash
curl -X POST http://127.0.0.1:8000/v1/schema-check \
  -H "Content-Type: application/json" \
  --data @examples/valid_payload.json
```

Invalid payload:

```bash
curl -X POST http://127.0.0.1:8000/v1/schema-check \
  -H "Content-Type: application/json" \
  --data @examples/invalid_payload.json
```

Repair example:

```bash
curl -X POST http://127.0.0.1:8000/v1/schema-check \
  -H "Content-Type: application/json" \
  --data @examples/repair_payload.json
```

## Placeholder Payment Gate

Enable placeholder mode:

```bash
export SCHEMACHECK_PAYMENT_MODE=placeholder
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Without token, `POST /v1/schema-check` should return `402 Payment Required`.

With token:

```bash
curl -X POST http://127.0.0.1:8000/v1/schema-check \
  -H "Content-Type: application/json" \
  -H "X-Payment-Token: test-payment-token" \
  --data @examples/valid_payload.json
```

## Test Suite

```bash
pytest
```

Expected current baseline:

```text
11 passed
```

## Notes

- Real x402 payment verification is not implemented yet.
- The placeholder token is only a development shim.
- AI repair is intentionally out of scope until deterministic validation is stable.
