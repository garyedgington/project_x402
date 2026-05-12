# Phase 3.6 — Guarded Real x402 Flow

SchemaCheck Agent now has a real x402-shaped FastAPI payment path behind configuration guards.

## Current behavior

Payment modes:

- `disabled` — local development, no payment required.
- `placeholder` — requires `X-Payment-Token: test-payment-token`.
- `x402` — requires the `X-PAYMENT` header.

When `SCHEMACHECK_PAYMENT_MODE=x402` and no `X-PAYMENT` header is supplied, the API returns HTTP `402` with payment requirements for:

- scheme: `exact`
- network: `eip155:8453` / Base mainnet
- payTo: `0x8fC4006534801c17A3368075A1Fb3b3C511EdB1F`
- price: `$0.005`
- facilitator: `https://api.cdp.coinbase.com/platform/v2/x402`

When an `X-PAYMENT` header is supplied while live verification is disabled, the API returns HTTP `501` with `X402_REAL_VERIFICATION_DISABLED`.

## Safety guard

Live settlement is not enabled by default.

To attempt real SDK verification later, both must be true:

```text
SCHEMACHECK_PAYMENT_MODE=x402
SCHEMACHECK_X402_REAL_VERIFICATION_ENABLED=true
```

Do not enable this until the first live/testnet payment run is intentionally scheduled.
