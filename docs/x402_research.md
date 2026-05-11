# Project x402 — Phase 3.1 Research: Integration Path

Status: Phase 3.1 complete  
Owner: Developer  
Product owner: Gary  
Last updated: 2026-05-09

## Goal

Identify the current practical integration path for adding real x402 payment gating to the existing FastAPI SchemaCheck Agent.

## High-level finding

The preferred path is to use the official `x402` Python SDK with its FastAPI/server support, not the older third-party FastAPI-only packages.

## Why

- The official x402 docs describe x402 as an open HTTP payment standard built around `402 Payment Required`.
- The standard flow matches our product: client requests a paid endpoint, server returns payment requirements, client submits payment, server verifies/settles, then returns the protected resource.
- The current `x402` Python SDK supports FastAPI as an install extra and includes server-side resource/payment verification components.
- Older libraries such as `fastapi-x402` and `fast-x402` exist, but they appear to be third-party wrappers and/or older packages. They may still be useful for reference, but they should not be the first implementation choice.

## Current preferred package

```bash
pip install "x402[fastapi,evm]"
```

Likely additional client/test extras later:

```bash
pip install "x402[fastapi,httpx,evm]"
```

## Likely payment model

- Network: Base or Base Sepolia for test mode.
- Asset: USDC.
- Price: start with `$0.005` per request unless product manager changes pricing.
- Protected endpoint: `POST /v1/schema-check`.
- Free endpoint: `GET /health`.

## Expected request behavior

1. Client calls `POST /v1/schema-check` without payment.
2. API returns `402 Payment Required` with payment requirements.
3. Client creates/signs payment payload.
4. Client retries request with payment headers.
5. Server verifies and settles payment.
6. If valid, server runs schema validation and returns the result.

## Integration design direction

Keep payment logic isolated from validation logic:

- `app/validator.py` remains unchanged.
- `app/models.py` remains mostly unchanged.
- `app/payment.py` becomes the x402 integration layer.
- `app/config.py` gains real x402 settings.
- `app/main.py` wires the payment dependency or middleware to `/v1/schema-check` only.

## Product manager inputs needed before implementation

- Receiving wallet address.
- Whether to use Base Sepolia first or go directly to Base mainnet.
- Whether we will use the public x402 facilitator or another facilitator.
- Whether the first paid test should be real USDC or testnet-only.

## Phase 3.1 conclusion

Proceed to Phase 3.2: confirm account, wallet, network, facilitator, and environment variable requirements before writing the real payment adapter.
