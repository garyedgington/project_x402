# Distribution Post Drafts

_Created: 2026-05-11_

---

## 1. Show HN Submission

**Title (60 chars max):**
> Show HN: A paid JSON Schema validation API using x402 micropayments

**URL to submit:**
> https://github.com/garyedgington/project_x402

**Text body (optional on HN, but worth including):**

---

I built a small paid API endpoint that validates JSON payloads against JSON Schema and returns structured errors with plain-English explanations.

What makes it different: it uses x402 — an HTTP-native micropayment standard — so each call costs $0.005 USDC on Base. No signup, no API key, no subscription. You pay per request automatically using the x402 protocol.

The idea came from wanting to build services where AI agents are the intended customers. An agent can call this endpoint to validate its own structured output before emitting it downstream, without any human checkout flow.

**Try it free (no wallet needed):**

```bash
curl -X POST https://projectx402-production.up.railway.app/v1/schema-check/trial \
  -H "Content-Type: application/json" \
  -d '{"json_schema": {"type": "object", "required": ["name"], "properties": {"name": {"type": "string"}}}, "payload": {"name": 123}}'
```

Returns: `valid: false`, error code `TYPE_MISMATCH`, path `$.name`, summary in plain English.

Stack: FastAPI + jsonschema + x402 Python SDK, deployed on Railway.

Feedback welcome — especially on whether the x402 payment UX is actually usable for agents or if there's too much friction.

---

**Timing:** Post Tuesday–Thursday, 9–11am US Eastern for best visibility.
**HN submission URL:** https://news.ycombinator.com/submit

---

## 2. Dev.to Article

**Title:**
> I built a machine-native paid API with x402 micropayments — here's how the payment flow works

**Tags:** `python`, `api`, `webdev`, `blockchain`

**Cover image:** optional — a simple terminal screenshot of the 402 → 200 flow

---

**Article body:**

---

Most APIs are built for humans: API keys, dashboards, monthly billing, rate limits. But what if your primary customer is an AI agent?

I've been experimenting with building services where autonomous agents are the *intended* users — not an edge case to be managed, but the main caller. This is the story of how I built SchemaCheck Agent, a tiny paid JSON Schema validation endpoint, and wired it up to x402 so agents can pay per request in USDC without any human in the loop.

### What is x402?

x402 is an HTTP payment protocol built on stablecoins. The flow is:

1. Client sends a request to a paid resource
2. Server returns `402 Payment Required` with a payment specification (amount, asset, receiving address)
3. Client signs and sends a USDC transfer on-chain
4. Server verifies the payment via a facilitator
5. Server returns the result

It works naturally with agents because there's no checkout page, no OAuth flow, no human approval step. An agent with a funded wallet can pay for API calls in the same request cycle.

### The service: SchemaCheck Agent

`POST /v1/schema-check` accepts a JSON Schema and a payload, and returns:

- `valid: true/false`
- A list of structured errors with error codes and JSONPath locations
- A plain-English summary
- Optionally, a suggested corrected payload

Price: **$0.005 USDC per call** on Base mainnet.

### Building it

The stack is straightforward: **FastAPI** for the API, **jsonschema** for deterministic validation, and the **x402 Python SDK** for the payment middleware.

The x402 integration is a dependency injected into the FastAPI route:

```python
@app.post("/v1/schema-check", dependencies=[Depends(enforce_payment)])
def schema_check(request: SchemaCheckRequest) -> SchemaCheckResponse:
    errors = validate_payload(request.json_schema, request.payload)
    ...
```

`enforce_payment` handles the 402/verify/settle cycle. If payment fails or isn't present, the request is blocked before the validation logic runs.

The x402 v2 protocol uses EIP-3009 `TransferWithAuthorization` — the client signs a USDC transfer off-chain, and the facilitator at x402.org verifies and settles it on-chain before the server proceeds.

### The hard parts

A few things that burned time:

**EIP-712 domain must match exactly.** The USDC contract on Base mainnet uses `{"name": "USD Coin", "version": "2"}` as its EIP-712 domain. If the domain in your 402 response doesn't match exactly, the facilitator rejects the payment with `invalid_exact_evm_token_name_mismatch`. No partial matches.

**Use sync facilitator client inside sync FastAPI routes.** If your route handler is `def` (not `async def`), you must use `HTTPFacilitatorClientSync` from the x402 SDK, not the async variant.

**Windows UTF-16 BOM breaks Railway deployments.** `requirements.txt` saved on Windows can carry a UTF-16 BOM that Linux pip can't parse. Always write deployment files with `Out-File -Encoding utf8NoBOM` or edit them on Linux. This caused 15+ failed Railway builds before I found the root cause.

### Try it free

There's a trial endpoint that requires no wallet or x402 setup:

```bash
curl -X POST https://projectx402-production.up.railway.app/v1/schema-check/trial \
  -H "Content-Type: application/json" \
  -d '{
    "json_schema": {
      "type": "object",
      "required": ["user_id", "action"],
      "properties": {
        "user_id": {"type": "string"},
        "action": {"type": "string", "enum": ["read", "write", "delete"]}
      }
    },
    "payload": {"user_id": 99, "action": "execute"}
  }'
```

Returns two errors: `TYPE_MISMATCH` on `$.user_id` and `ENUM_VIOLATION` on `$.action`.

### Why this matters for agents

The long-term idea is a portfolio of small machine-native paid endpoints. Each one does one narrow thing reliably, charges a tiny amount per call, and requires no human interaction. The portfolio compounds: better reliability → more repeat callers → usage signal → adjacent endpoints.

x402 makes this possible because the payment is part of the HTTP protocol, not bolted on as a SaaS billing layer.

**Full source and docs:** https://github.com/garyedgington/project_x402

---

**Notes for posting:**
- Create account at dev.to if needed
- Add a cover image (screenshot of terminal showing 402 → 200 flow works well)
- Schedule for Tuesday–Thursday morning for best reach

---

## 3. Reddit posts

### r/Python post

**Title:** Built a FastAPI service that charges $0.005 per call using x402 USDC micropayments

**Body:**
Wanted to share a small side project: SchemaCheck Agent, a FastAPI endpoint that validates JSON payloads against JSON Schema and charges per call via x402 (HTTP-native USDC micropayments).

The interesting engineering part is the x402 integration — when a client hits the endpoint without payment, they get a 402 with a payment spec. They sign an EIP-3009 USDC transfer, send it as a header, and the facilitator verifies on-chain before the server responds.

There's a free trial endpoint if you want to test validation without any crypto setup:

`POST https://projectx402-production.up.railway.app/v1/schema-check/trial`

Source: https://github.com/garyedgington/project_x402

Happy to answer questions about the FastAPI + x402 integration.

---

### r/webdev post

**Title:** I built a pay-per-call API using x402 micropayments — no API key, no subscription, $0.005/call in USDC

**Body:**
Built a JSON Schema validation API that uses x402 instead of traditional API auth. No API key required — you pay $0.005 USDC per call automatically via the x402 HTTP payment protocol.

The idea is to build services where AI agents are the intended customers. An agent with a wallet can call the endpoint without any human approval step.

Free trial (no wallet needed): `POST https://projectx402-production.up.railway.app/v1/schema-check/trial`

Source + docs: https://github.com/garyedgington/project_x402

---

## 4. Discord message template (AI agent communities)

**For: AutoGPT / CrewAI / LangChain Discord, #tools or #resources channel**

> 👋 Built something that might be useful for agent pipelines — a free trial endpoint for validating structured JSON outputs:
>
> `POST https://projectx402-production.up.railway.app/v1/schema-check/trial`
>
> Send it a JSON Schema + payload, get back structured errors with JSONPath locations and a plain-English summary. No API key, no signup.
>
> Useful for agents that need to validate their own structured output before passing it downstream. Full source: https://github.com/garyedgington/project_x402
>
> (There's also a paid version at $0.005/call via x402 USDC if you want to test machine-to-machine micropayments.)
