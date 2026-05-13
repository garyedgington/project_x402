# SchemaCheck Agent — Agent & Developer Quickstart

**Base URL:** `https://projectx402-production.up.railway.app`  
**Version:** 1.12.4  
**Payment options:** x402 v2 USDC micropayments ($0.005/call) · MCP via MCP-Hive (fiat)  
**Trial endpoint:** Free, no payment, no repair, 32KB limit

---

## Access methods

SchemaCheck Agent supports two payment rails:

| Method | Transport | Billing | Best for |
|---|---|---|---|
| MCP tools | Streamable HTTP (`/mcp`) | Fiat via MCP-Hive | MCP-enabled agents and clients |
| HTTP REST | HTTPS + x402 USDC | $0.005 USDC / call | x402-native agents, direct API callers |
| Trial REST | HTTPS, free | None | Testing, dev, lightweight checks |

---

## 0. MCP access (recommended for AI agents)

The `/mcp` endpoint exposes SchemaCheck Agent as a native MCP tool. Any MCP-compatible client (Claude, Cursor, Continue, custom agents) can use it without managing x402 payment flows.

**MCP endpoint:** `https://projectx402-production.up.railway.app/mcp`  
**Transport:** Streamable HTTP (MCP spec 2025-03-26)  
**Tools:** `validate_schema` (full, with repair) · `validate_schema_trial` (free, no repair)

### Connect in Claude Desktop (claude_desktop_config.json)

```json
{
  "mcpServers": {
    "schemacheck": {
      "url": "https://projectx402-production.up.railway.app/mcp"
    }
  }
}
```

### Connect via MCP client (Python)

```python
# pip install mcp
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def main():
    async with streamablehttp_client(
        "https://projectx402-production.up.railway.app/mcp"
    ) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Free trial — no repair
            result = await session.call_tool(
                "validate_schema_trial",
                {
                    "json_schema": {
                        "type": "object",
                        "required": ["name", "email"],
                        "properties": {
                            "name": {"type": "string"},
                            "email": {"type": "string", "format": "email"},
                        },
                    },
                    "payload": {"name": "Ada", "email": "not-an-email"},
                    "explain": True,
                },
            )
            print(result.content[0].text)

asyncio.run(main())
```

### MCP tool reference

**`validate_schema`** — Full validation with optional repair. Billed via MCP-Hive.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `json_schema` | object | required | JSON Schema document (Draft 2020-12 or Draft-07) |
| `payload` | any | required | JSON value to validate |
| `strictness` | string | `"normal"` | `"strict"` · `"normal"` · `"lenient"` |
| `repair` | boolean | `false` | Return suggested corrected payload when invalid |
| `explain` | boolean | `true` | Include plain-English summary |

**`validate_schema_trial`** — Validation only, no repair, always free.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `json_schema` | object | required | JSON Schema document |
| `payload` | any | required | JSON value to validate |
| `explain` | boolean | `true` | Include plain-English summary |

---

## 1. Try it instantly (no payment setup)

The trial endpoint requires no x402 configuration and no wallet. It runs full JSON Schema validation and returns structured errors, but does not return repair suggestions.

### curl

```bash
curl -X POST https://projectx402-production.up.railway.app/v1/schema-check/trial \
  -H "Content-Type: application/json" \
  -d '{
    "json_schema": {
      "type": "object",
      "required": ["user_id", "action"],
      "properties": {
        "user_id": {"type": "string"},
        "action": {"type": "string", "enum": ["read", "write", "delete"]},
        "timestamp": {"type": "string", "format": "date-time"}
      },
      "additionalProperties": false
    },
    "payload": {
      "user_id": 12345,
      "action": "execute"
    },
    "explain": true
  }'
```

### Python

```python
import httpx

schema = {
    "type": "object",
    "required": ["user_id", "action"],
    "properties": {
        "user_id": {"type": "string"},
        "action": {"type": "string", "enum": ["read", "write", "delete"]},
    },
    "additionalProperties": False,
}

payload = {"user_id": 12345, "action": "execute"}

response = httpx.post(
    "https://projectx402-production.up.railway.app/v1/schema-check/trial",
    json={"json_schema": schema, "payload": payload, "explain": True},
)
result = response.json()
print(result["valid"])       # False
print(result["errors"])      # list of ValidationErrorDetail objects
print(result["summary"])     # plain-English explanation
```

---

## 2. Full paid endpoint with x402

The paid endpoint at `POST /v1/schema-check` includes repair suggestions and has no size limit. Each call costs $0.005 USDC, paid automatically via the x402 protocol.

### x402 payment flow (v2)

```
Client                          Server                        Facilitator
  |                               |                               |
  |-- POST /v1/schema-check ----->|                               |
  |<-- 402 Payment Required ------|                               |
  |   (x402Version=2, accepts[])  |                               |
  |                               |                               |
  |-- Sign EIP-3009 payment       |                               |
  |-- POST /v1/schema-check ----->|                               |
  |   (PAYMENT-SIGNATURE header)  |-- verify payment ------------>|
  |                               |<-- verified ------------------|
  |<-- 200 OK (result) -----------|                               |
```

### Python with x402 SDK (async — recommended)

```python
# pip install "x402[httpx]" eth_account
import asyncio
import os
from eth_account import Account
from x402 import x402Client
from x402.http.clients import x402HttpxClient
from x402.mechanisms.evm import EthAccountSigner
from x402.mechanisms.evm.exact.register import register_exact_evm_client

BASE_URL = "https://projectx402-production.up.railway.app"

async def main():
    account = Account.from_key(os.getenv("EVM_PRIVATE_KEY"))
    client = x402Client()
    register_exact_evm_client(client, EthAccountSigner(account))

    schema = {
        "type": "object",
        "required": ["name", "email"],
        "properties": {
            "name": {"type": "string"},
            "email": {"type": "string", "format": "email"},
        },
        "additionalProperties": False,
    }

    async with x402HttpxClient(client) as http:
        response = await http.post(
            f"{BASE_URL}/v1/schema-check",
            json={
                "json_schema": schema,
                "payload": {"name": "Ada Lovelace", "email": "ada@example.com"},
                "repair": False,
                "explain": True,
            },
        )
        await response.aread()
        result = response.json()
        print(result["valid"])    # True

asyncio.run(main())
```

### Python with x402 SDK (sync)

```python
# pip install "x402[requests]" eth_account
import os
from eth_account import Account
from x402 import x402ClientSync
from x402.http.clients import x402_requests
from x402.mechanisms.evm import EthAccountSigner
from x402.mechanisms.evm.exact.register import register_exact_evm_client

BASE_URL = "https://projectx402-production.up.railway.app"

account = Account.from_key(os.getenv("EVM_PRIVATE_KEY"))
client = x402ClientSync()
register_exact_evm_client(client, EthAccountSigner(account))

schema = {
    "type": "object",
    "required": ["name", "email"],
    "properties": {
        "name": {"type": "string"},
        "email": {"type": "string", "format": "email"},
    },
    "additionalProperties": False,
}

with x402_requests(client) as session:
    response = session.post(
        f"{BASE_URL}/v1/schema-check",
        json={
            "json_schema": schema,
            "payload": {"name": "Ada Lovelace", "email": "ada@example.com"},
            "repair": False,
            "explain": True,
        },
    )
    result = response.json()
    print(result["valid"])    # True
```

The x402 SDK handles the 402 → sign → retry flow automatically.

---

## 3. Request schema

```json
{
  "json_schema": { },        // required — JSON Schema document
  "payload": { },            // required — any JSON value
  "strictness": "normal",    // optional: "strict" | "normal" | "lenient"
  "repair": false,           // optional: boolean (paid endpoint only)
  "explain": true            // optional: boolean
}
```

### Strictness modes

| Mode | Behaviour |
|---|---|
| `strict` | Deterministic errors only. No coercion, no repair. |
| `normal` | Validate deterministically, explain errors. Repair only if `repair=true`. |
| `lenient` | Same as normal, but allows conservative type coercion in repair suggestions. |

---

## 4. Response schema

```json
{
  "valid": true,
  "errors": [],
  "summary": "The payload is valid against the supplied JSON Schema.",
  "suggested_payload": null,
  "confidence": 1.0,
  "meta": {
    "strictness": "normal",
    "repair_attempted": false,
    "engine": "jsonschema",
    "schema_draft": "auto"
  }
}
```

### Error object shape

```json
{
  "path": "$.email",
  "code": "FORMAT_VIOLATION",
  "message": "'not-an-email' is not a 'email'",
  "schema_path": "$/properties/email/format",
  "expected": "email",
  "actual": "not-an-email"
}
```

Paths use JSONPath notation (`$.field`, `$[0].field`). The root object is `$`.

---

## 5. Error codes

| Code | Meaning |
|---|---|
| `REQUIRED_FIELD_MISSING` | A required property is missing |
| `TYPE_MISMATCH` | Wrong JSON type |
| `FORMAT_VIOLATION` | Value does not match the format (e.g. `email`, `date-time`) |
| `ENUM_VIOLATION` | Value not in allowed enum list |
| `ADDITIONAL_PROPERTY` | Extra property not allowed by schema |
| `MINIMUM_VIOLATION` / `MAXIMUM_VIOLATION` | Numeric range violation |
| `MIN_LENGTH_VIOLATION` / `MAX_LENGTH_VIOLATION` | String length violation |
| `PATTERN_VIOLATION` | String does not match regex pattern |
| `SCHEMA_VALIDATION_ERROR` | Any other schema constraint failure |

---

## 6. API-level error responses

These are transport errors, not validation failures.

| HTTP status | Code | When |
|---|---|---|
| 400 | `INVALID_JSON_SCHEMA` | The `json_schema` field is not a valid JSON Schema |
| 402 | — | Payment required (paid endpoint only) |
| 413 | `TRIAL_PAYLOAD_TOO_LARGE` | Trial endpoint body exceeds 32KB |
| 422 | — | Missing required field or invalid field value |

---

## 7. Common use cases

### Validate an API request payload before forwarding

```python
def validate_before_forward(schema, incoming_payload):
    result = httpx.post(
        "https://projectx402-production.up.railway.app/v1/schema-check/trial",
        json={"json_schema": schema, "payload": incoming_payload},
    ).json()
    if not result["valid"]:
        raise ValueError(result["summary"])
    return incoming_payload
```

### Agent self-check before emitting structured output

```python
OUTPUT_SCHEMA = {
    "type": "object",
    "required": ["action", "confidence"],
    "properties": {
        "action": {"type": "string"},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
    },
}

def emit_validated_output(output: dict) -> dict:
    check = httpx.post(
        "https://projectx402-production.up.railway.app/v1/schema-check/trial",
        json={"json_schema": OUTPUT_SCHEMA, "payload": output},
    ).json()
    if not check["valid"]:
        raise RuntimeError(f"Output failed schema check: {check['summary']}")
    return output
```

---

## 8. Payment details

| Field | Value |
|---|---|
| Protocol | x402 v2 |
| Network | Base mainnet (eip155:8453) |
| Asset | USDC (0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913) |
| Price | 5000 atomic units = $0.005 USDC |
| Facilitator | https://api.cdp.coinbase.com/platform/v2/x402 |
| Scheme | exact (EIP-3009 TransferWithAuthorization) |
| SDK install (buyer) | `pip install "x402[httpx]"` (async) or `pip install "x402[requests]"` (sync) |

---

## 9. Health check

```bash
curl https://projectx402-production.up.railway.app/health
# {"status":"ok","service":"schemacheck-agent","version":"1.12.4"}
```
