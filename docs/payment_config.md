# Phase 3.5 Payment Configuration

## Current decision

Project x402 will use a testnet-first payment configuration before any mainnet USDC flow is attempted.

## Test configuration

| Setting | Value |
|---|---|
| Payment mode | `x402` when testing payment behavior |
| Network | `eip155:84532` |
| Network name | Base Sepolia |
| Facilitator | `https://x402.org/facilitator` |
| Scheme | `exact` |
| Price | `$0.005` per request |
| Receiving wallet / `payTo` | `0x8fC4006534801c17A3368075A1Fb3b3C511EdB1F` |
| Real verification | disabled until explicit live-payment test |

## Safety rule

Only the public receiving address is stored in project config. Never store a private key, seed phrase, wallet password, or recovery phrase in this repository.

## Current implementation state

The app can now expose x402-shaped payment-required behavior using the configured wallet, price, network, scheme, and facilitator. Real verification remains guarded by:

```text
SCHEMACHECK_X402_REAL_VERIFICATION_ENABLED=false
```

Phase 3.6 should either:

1. integrate the official x402 FastAPI middleware path, or
2. implement a small adapter around `x402ResourceServer` after confirming request/response mechanics.
