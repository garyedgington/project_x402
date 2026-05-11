# SchemaCheck Agent

A machine-native paid API for validating JSON payloads against JSON Schema.

**Live endpoint:** `https://projectx402-production.up.railway.app`

---

## What it does

Send a JSON Schema and a JSON payload. Get back a structured validation result: whether the payload is valid, a list of errors with JSON Pointer paths, a plain-English summary, and optionally a suggested corrected payload.

Built for autonomous agents, backend pipelines, and developers who need reliable, cheap, per-call JSON validation without managing a library dependency.

---

## Endpoints

| Endpoint | Payment | Repair | Limit |
|---|---|---|---|
| `POST /v1/schema-check` | x402 USDC required ($0.005) | Yes | None |
| `POST /v1/schema-check/trial` | Free | No | 32KB request body |
| `GET /health` | Free | — | — |

---

## Quickstart — trial (no payment)

```bash
curl -X POST https://projectx402-production.up.railway.app/v1/schema-check/trial \
  -H "Content-Type: application/json" \
  -d '{
    "json_schema": {
      "type": "object",
      "required": ["name", "email"],
      "properties": {
        "name": {"type": "string"},
        "email": {"type": "string", "format": "email"}
      },
      "additionalProperties": false
    },
    "payload": {
      "name": "Ada Lovelace",
      "email": "not-an-email"
    }
  }'
```

Response:

```json
{
  "valid": false,
  "errors": [
    {
      "path": "/email",
      "code": "format",
      "message": "'not-an-email' is not a valid email address.",
      "schema_path": "/properties/email/format"
    }
  ],
  "summary": "The payload failed validation. 1 error found.",
  "suggested_payload": null,
  "confidence": 0.9,
  "meta": {
    "strictness": "normal",
    "repair_attempted": false,
    "engine": "jsonschema",
    "schema_draft": "auto"
  }
}
```

---

## Quickstart — paid endpoint (x402)

The paid endpoint requires an x402 v2 USDC micropayment of **$0.005** per call on Base Sepolia (testnet) or Base mainnet.

Payment flow:

1. Send request to `POST /v1/schema-check` without payment headers.
2. Receive `402 Payment Required` with `x402Version=2` and payment details.
3. Sign and send payment via `PAYMENT-SIGNATURE` header.
4. Receive `200` with validation result.

See [docs/agent_quickstart.md](docs/agent_quickstart.md) for a full Python example with x402 payment handling.

---

## Request fields

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `json_schema` | object | yes | — | JSON Schema document |
| `payload` | any | yes | — | The JSON value to validate |
| `strictness` | string | no | `"normal"` | `"strict"`, `"normal"`, or `"lenient"` |
| `repair` | boolean | no | `false` | Return a suggested corrected payload if possible |
| `explain` | boolean | no | `true` | Include plain-English summary |

---

## Response fields

| Field | Type | Description |
|---|---|---|
| `valid` | boolean | `true` if payload passes schema validation |
| `errors` | array | Structured validation errors; empty when valid |
| `summary` | string | Plain-English summary (null if `explain=false`) |
| `suggested_payload` | any / null | Corrected payload suggestion (paid endpoint + `repair=true` only) |
| `confidence` | float | Confidence score 0–1 |
| `meta` | object | Engine, strictness, and repair metadata |

---

## Error codes

`required` · `type` · `format` · `enum` · `additionalProperties` · `minimum` · `maximum` · `minLength` · `maxLength` · `pattern` · `items` · `oneOf` · `anyOf` · `allOf` · `unknown`

---

## Pricing

| Mode | Price |
|---|---|
| Trial (`/v1/schema-check/trial`) | Free |
| Paid (`/v1/schema-check`) | $0.005 USDC per call |

Payment is handled via the [x402 protocol](https://x402.org) — an HTTP-native micropayment standard using USDC on Base.

---

## Health check

```bash
curl https://projectx402-production.up.railway.app/health
```

```json
{"status": "ok", "service": "schemacheck-agent", "version": "0.3.0"}
```

---

## Reporting issues

If you encounter unexpected responses, payment errors, or validation bugs, please [open a GitHub issue](https://github.com/garyedgington/project_x402/issues).

Include:
- The endpoint called (`/v1/schema-check` or `/v1/schema-check/trial`)
- The request body (redact any sensitive data)
- The response received
- The `X-Request-ID` header value from the response if available

---

## Further reading

- [docs/agent_quickstart.md](docs/agent_quickstart.md) — Full agent integration guide with x402 payment examples
- [api_contract.md](api_contract.md) — Full API contract and error shape reference
- [docs/x402_real_flow.md](docs/x402_real_flow.md) — x402 v2 payment flow details
