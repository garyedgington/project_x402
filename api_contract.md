# Project x402 — SchemaCheck Agent API Contract

Status: Phase 1 baseline  
Owner: Developer  
Product owner: Gary  
Last updated: 2026-05-09

## 1. Purpose

SchemaCheck Agent is a narrow, machine-native validation endpoint. It accepts a JSON Schema and a JSON payload, validates the payload, explains failures, and optionally suggests a corrected payload.

The first version should be useful before payment gating is added. x402 payment enforcement will wrap the same endpoint later without changing the core request/response contract unless required by the payment middleware.

## 2. MVP Endpoint

```http
POST /v1/schema-check
Content-Type: application/json
```

## 3. Request Body

```json
{
  "json_schema": {},
  "payload": {},
  "strictness": "normal",
  "repair": false,
  "explain": true
}
```

### Fields

| Field | Type | Required | Description |
|---|---:|---:|---|
| `json_schema` | object | yes | JSON Schema document used to validate the payload. MVP targets common JSON Schema draft behavior, not advanced custom validators. |
| `payload` | any JSON value | yes | The payload to validate. Usually an object, but arrays/scalars are allowed if the schema allows them. |
| `strictness` | string | no | One of `strict`, `normal`, or `lenient`. Default: `normal`. |
| `repair` | boolean | no | Whether to return a suggested corrected payload when possible. Default: `false`. |
| `explain` | boolean | no | Whether to include plain-English explanations. Default: `true`. |

### Strictness Behavior

| Mode | Behavior |
|---|---|
| `strict` | Return deterministic schema errors only. Do not infer, coerce, or repair. |
| `normal` | Validate deterministically and provide explanations. Repair suggestions may be returned only when `repair=true`. |
| `lenient` | Validate deterministically, explain errors, and allow conservative repair suggestions for obvious type coercions or missing optional formatting. |

MVP rule: strictness must not silently change validation truth. `valid` is always based on deterministic schema validation. Repair suggestions are advisory.

## 4. Success Response

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
  "summary": "The payload failed validation because the email field is not formatted as an email address.",
  "suggested_payload": {
    "email": "user@example.com"
  },
  "confidence": 0.82,
  "meta": {
    "strictness": "normal",
    "repair_attempted": true,
    "validator": "jsonschema",
    "schema_draft": "auto"
  }
}
```

### Response Fields

| Field | Type | Description |
|---|---:|---|
| `valid` | boolean | True when the original payload passes schema validation. |
| `errors` | array | Structured validation errors. Empty when valid. |
| `summary` | string/null | Plain-English summary when `explain=true`; otherwise null. |
| `suggested_payload` | any/null | Suggested corrected payload when `repair=true` and a safe suggestion exists. Null otherwise. |
| `confidence` | number | Confidence in the explanation or repair suggestion, from 0 to 1. Deterministic valid results may return 1.0. |
| `meta` | object | Debug/trace metadata safe for API clients. |

## 5. Error Object

```json
{
  "path": "/user/age",
  "code": "type",
  "message": "Expected integer but received string.",
  "schema_path": "/properties/user/properties/age/type"
}
```

### Error Codes

Initial normalized codes:

- `required`
- `type`
- `format`
- `enum`
- `additionalProperties`
- `minimum`
- `maximum`
- `minLength`
- `maxLength`
- `pattern`
- `items`
- `oneOf`
- `anyOf`
- `allOf`
- `unknown`

## 6. API-Level Error Responses

These are transport/request errors, not schema validation failures.

### Invalid Request Body

```http
HTTP/1.1 400 Bad Request
Content-Type: application/json
```

```json
{
  "error": {
    "code": "invalid_request",
    "message": "Request body must be valid JSON.",
    "details": []
  }
}
```

### Missing Required Field

```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json
```

```json
{
  "error": {
    "code": "missing_field",
    "message": "Missing required field: json_schema.",
    "details": [
      {"field": "json_schema"}
    ]
  }
}
```

### Unsupported Strictness

```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json
```

```json
{
  "error": {
    "code": "unsupported_strictness",
    "message": "strictness must be one of: strict, normal, lenient.",
    "details": [
      {"allowed": ["strict", "normal", "lenient"]}
    ]
  }
}
```

### Payment Required Placeholder

This is not required for the local MVP, but the endpoint should be designed so it can be wrapped by x402 payment gating later.

```http
HTTP/1.1 402 Payment Required
Content-Type: application/json
```

```json
{
  "error": {
    "code": "payment_required",
    "message": "Payment is required to access this endpoint.",
    "details": []
  }
}
```

## 7. Example Calls

### 7.1 Valid Payload

Request:

```json
{
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
    "email": "ada@example.com"
  },
  "strictness": "normal",
  "repair": false,
  "explain": true
}
```

Response:

```json
{
  "valid": true,
  "errors": [],
  "summary": "The payload is valid.",
  "suggested_payload": null,
  "confidence": 1.0,
  "meta": {
    "strictness": "normal",
    "repair_attempted": false,
    "validator": "jsonschema",
    "schema_draft": "auto"
  }
}
```

### 7.2 Invalid Payload

Request:

```json
{
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
  },
  "strictness": "normal",
  "repair": true,
  "explain": true
}
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
  "summary": "The email field is present, but it is not formatted as an email address.",
  "suggested_payload": {
    "name": "Ada Lovelace",
    "email": "ada@example.com"
  },
  "confidence": 0.75,
  "meta": {
    "strictness": "normal",
    "repair_attempted": true,
    "validator": "jsonschema",
    "schema_draft": "auto"
  }
}
```

### 7.3 Missing Required Field

Response:

```json
{
  "valid": false,
  "errors": [
    {
      "path": "/",
      "code": "required",
      "message": "Missing required property: email.",
      "schema_path": "/required"
    }
  ],
  "summary": "The payload is missing the required email field.",
  "suggested_payload": null,
  "confidence": 1.0,
  "meta": {
    "strictness": "normal",
    "repair_attempted": false,
    "validator": "jsonschema",
    "schema_draft": "auto"
  }
}
```

## 8. MVP Non-Goals

- No account system.
- No dashboard.
- No multi-endpoint marketplace.
- No long-running jobs.
- No bulk CSV validation.
- No guaranteed semantic repair.
- No direct dependency on payment gating for local MVP.

## 9. Phase 1 Exit Criteria

- This API contract is accepted as the baseline.
- Example requests and responses are sufficient to implement tests.
- MVP scope is frozen around one endpoint: `POST /v1/schema-check`.
