# Payment Configuration

## Current configuration (Base mainnet)

| Setting | Value |
|---|---|
| Payment mode | `x402` |
| Network | `eip155:8453` |
| Network name | Base mainnet |
| Facilitator | `https://api.cdp.coinbase.com/platform/v2/x402` |
| Scheme | `exact` |
| Price | `$0.005` per request |
| USDC contract | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` |
| EIP-712 domain | `{"name": "USD Coin", "version": "2"}` |
| Receiving wallet / `payTo` | `0x8fC4006534801c17A3368075A1Fb3b3C511EdB1F` |
| Real verification | enabled on Railway (`SCHEMACHECK_X402_REAL_VERIFICATION_ENABLED=true`) |

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
