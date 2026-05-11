# Project x402 — Phase 5 Measurement Report

_Date: 2026-05-11_  
_Phase: 5 — Measurement and Economics_  
_Status: COMPLETE_

---

## 1. Purpose

This report documents the measurement and economics findings for SchemaCheck Agent following the first live x402 testnet payment. It satisfies the Phase 5 exit criteria and provides a recorded basis for the Phase 6 go/no-go decision.

---

## 2. Payment and Call Data

### Confirmed payments

| Field | Value |
|---|---|
| Date | 2026-05-11 |
| Network | Base Sepolia (eip155:84532) |
| Payment standard | x402 v2 |
| Payment scheme | exact EVM (EIP-3009 TransferWithAuthorization) |
| Facilitator | https://x402.org/facilitator |
| Amount | 5000 atomic units = $0.005 USDC |
| Test wallet (payer) | 0x272DDa1C5caC775752ab8432A50dfD8ed2d4001B |
| Receiving wallet | 0x8fC4006534801c17A3368075A1Fb3b3C511EdB1F |
| Result | 200 OK — `"valid": true` |

**Total confirmed calls:** 1 (testnet)  
**Total confirmed paid calls:** 1 (testnet)  
**Total confirmed revenue:** $0.005 USDC (testnet, not mainnet)  
**Payment failure rate:** 0% (1/1 succeeded)  
**Repeat callers:** 0 external (all calls internal test)

### End-to-end flow confirmed

1. Client sent unpaid request → server returned `402 Payment Required` with x402 v2 `accepts` array
2. Client parsed `x402Version=2`, selected USDC on eip155:84532
3. Client signed EIP-3009 `TransferWithAuthorization` with test wallet
4. Sent signed payment as `PAYMENT-SIGNATURE` header
5. Facilitator at x402.org verified and settled on-chain
6. Server returned `200` with valid SchemaCheck response

---

## 3. Unit Economics

### Revenue per call

| Item | Value |
|---|---|
| Price per call | $0.005 USDC |
| Facilitator fee | Not confirmed; assumed negligible on testnet |
| Net revenue per call (estimate) | ~$0.005 USDC |

### Marginal compute cost per call

SchemaCheck Agent Phase 5 uses deterministic validation only. No LLM or AI inference is invoked per call.

| Component | Cost per call |
|---|---|
| JSON schema validation (jsonschema library) | ~$0.000 — CPU only, sub-millisecond |
| LLM inference | $0.000 — not enabled |
| External API calls | $0.000 — none |
| Facilitator verification | $0.000 — facilitator fee not currently charged to server |
| **Marginal cost per call (estimate)** | **~$0.000** |

### Infrastructure cost model

| Component | Estimated monthly cost |
|---|---|
| Railway hosting (Hobby tier) | ~$5.00/month |
| Domain / DNS | $0 (Railway subdomain) |
| GitHub repo | $0 (free tier) |
| Monitoring tooling | $0 (Railway dashboard logs) |
| **Total fixed monthly cost** | **~$5.00/month** |

### Break-even analysis

At $0.005 revenue per call and $5.00/month fixed cost:

| Call volume (calls/month) | Monthly revenue | Monthly cost | Net margin |
|---|---|---|---|
| 100 | $0.50 | $5.00 | -$4.50 |
| 500 | $2.50 | $5.00 | -$2.50 |
| 1,000 | $5.00 | $5.00 | $0.00 |
| 2,000 | $10.00 | $5.00 | +$5.00 |
| 10,000 | $50.00 | $5.00 | +$45.00 |

**Break-even point: ~1,000 calls/month.**

At current price ($0.005) and zero marginal compute cost, the unit economics are structurally sound. The service is profitable at scale. The constraint is call volume, not margin per call.

---

## 4. Latency

Latency was not formally measured across a sample during Phase 5. The following is an estimate based on the confirmed testnet payment run.

| Stage | Estimated duration |
|---|---|
| FastAPI request handling | < 5ms |
| jsonschema validation | < 5ms |
| x402 facilitator verification (network round-trip) | 500–2000ms |
| Total end-to-end (paid call) | ~0.5–2.5 seconds |

Facilitator network latency dominates total call time. This is acceptable for agent-to-agent calls and batch pipelines, but would be unsuitable for real-time human-facing interactions. This is consistent with the machine-native positioning of the service.

_A formal latency sample across ≥ 10 calls should be collected in Phase 6 once external callers are onboarded._

---

## 5. Validation Behavior

No real external callers have submitted payloads yet. The following is known from local and CI test runs.

| Test category | Result |
|---|---|
| Valid payload | Passes correctly |
| Missing required field | Returns `required` error with JSON Pointer path |
| Wrong type | Returns `type` error |
| Invalid enum | Returns `enum` error |
| Additional properties (strictness=strict) | Returns `additionalProperties` error |
| Invalid strictness value | Returns 422 API error |
| Missing `json_schema` | Returns 422 API error |
| Missing `payload` | Returns 422 API error |
| `repair=false` | Never returns suggested payload |
| `repair=true` (deterministic cases) | Returns safe repair for additional properties |

**Top validation failure types from external callers:** Unknown — no external call data yet. This metric should be populated in Phase 6.

---

## 6. Error Rate

| Error type | Count |
|---|---|
| 5xx server errors | 0 (in confirmed test run) |
| 4xx client errors | 0 (in confirmed test run) |
| Payment verification failures | 0 (1/1 succeeded) |
| Facilitator timeout or rejection | 0 (in confirmed test run) |

_Error rate data from real external callers is not yet available. This section should be updated in Phase 6._

---

## 7. Known Gaps

The following metrics are not yet available due to the absence of external callers:

- Repeat caller rate
- Real-world payload failure distribution
- Facilitator fee charged to server side (if any)
- Latency sample size (only 1 confirmed call)
- Payment failure rate under real-world conditions
- Conversion rate (unpaid requests → paid calls)

These gaps are expected at this stage. Phase 6 (Distribution) is designed to generate the external call volume needed to populate them.

---

## 8. Decision

**Decision: Continue to Phase 6 — Distribution Test.**

Rationale:

- The x402 v2 payment flow is confirmed working end-to-end on testnet.
- Unit economics are favorable: zero marginal compute cost, break-even at ~1,000 calls/month on a $5/month infrastructure base.
- Validation behavior is deterministic and correct across all test cases.
- The endpoint is live and publicly reachable at `https://projectx402-production.up.railway.app`.
- The only missing signal is external caller demand — which is exactly what Phase 6 is designed to test.

There is no evidence to revise or stop at this time. The economics are not the constraint. Distribution is.

---

## 9. Phase 5 Exit Checklist

| Criterion | Status |
|---|---|
| At least one full measurement report exists | ✓ This document |
| Unit economics are known | ✓ Break-even at ~1,000 calls/month; zero marginal cost |
| Clear decision exists: continue, revise, or stop | ✓ Continue to Phase 6 |
