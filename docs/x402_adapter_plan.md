# x402 Adapter Skeleton Plan

## Purpose

Add x402-shaped payment behavior without enabling real settlement until wallet, network, facilitator, and price decisions are confirmed.

## Current modes

- `disabled`: endpoint is free for local development.
- `placeholder`: endpoint requires `X-Payment-Token: test-payment-token`.
- `x402`: endpoint returns x402-shaped `402 Payment Required` behavior, but real verification is guarded.

## Required x402 settings

- `SCHEMACHECK_PAYMENT_MODE=x402`
- `SCHEMACHECK_X402_PAY_TO=<wallet address>`
- `SCHEMACHECK_X402_PRICE=$0.005`
- `SCHEMACHECK_X402_NETWORK=eip155:8453`
- `SCHEMACHECK_X402_SCHEME=exact`
- `SCHEMACHECK_X402_FACILITATOR_URL=https://x402.org/facilitator`
- `SCHEMACHECK_X402_REAL_VERIFICATION_ENABLED=false`

## HTTP headers

- Incoming payment header: `X-PAYMENT`
- Payment-required indicator/header: `PAYMENT-REQUIRED`
- Payment response header: `PAYMENT-RESPONSE`
- Payment signature header: `PAYMENT-SIGNATURE`

## Guardrail

Real payment verification must remain disabled until the product manager confirms the receiving wallet, network, facilitator, and first price.
