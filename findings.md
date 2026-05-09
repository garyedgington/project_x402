# Project x402 — Findings

_Last updated: 2026-05-09_

## Finding 1 — The strongest path is owned infrastructure, not platform farming

The project should not rely on agents performing tasks on third-party human microtask platforms. That path risks terms-of-service violations and tends to depend on platforms that do not want bots.

The better path is to create services where automated agents are the intended customers.

## Finding 2 — x402-style payments fit machine-native services

The x402-style flow is useful because it makes payment part of the API interaction:

1. Request resource.
2. Receive `402 Payment Required`.
3. Pay automatically, likely in USDC.
4. Receive the response.

That structure fits autonomous agents better than checkout pages, subscriptions, manual invoicing, or ad-supported monetization.

## Finding 3 — The task must be small, specific, useful, cheap, and easy to validate

Project x402 should not begin with a broad AI product. It should begin with a narrow function that has objective success criteria.

Good candidates:

- JSON validation
- API response validation
- Data normalization
- Entity resolution
- URL classification
- Prompt compression
- Diff summarization

Poor candidates:

- Vague research agents
- Human-like browsing agents
- Anything requiring subjective judgment with no measurable quality target
- Anything dependent on prohibited automation or fake engagement

## Finding 4 — SchemaCheck Agent is the best first experiment

SchemaCheck Agent has the strongest combination of low implementation cost, obvious utility, objective validation, backend-native usage, and expandable surface area.

It can start as a deterministic validator plus optional AI repair/explanation layer. That keeps cost low while still making the endpoint useful to agents and developers.

## Finding 5 — The first version should prove demand before expanding service count

The long-term idea is a portfolio of paid micro-endpoints, but expansion should wait for usage signal.

The immediate objective is not to build many agents. It is to build one narrow endpoint and measure:

- Calls
- Paid conversions
- Cost per call
- Latency
- Error rate
- Validation accuracy
- Repeat usage

## Finding 6 — Monitoring is a core feature, not an afterthought

Because revenue per request is tiny, small leaks matter. The system must track whether each endpoint is economically positive.

Minimum metrics:

- Gross revenue per call
- Payment success rate
- Compute/API cost per call
- Net margin per call
- Latency
- Error rate
- Retry rate
- Top failure modes
- Returning clients or repeat callers

## Finding 7 — The service should be documented for agents and developers

Project x402 services should expose simple docs with:

- Endpoint URL
- Request schema
- Response schema
- Example request
- Example response
- Error format
- Pricing
- x402 payment behavior

The documentation itself is part of distribution because other agents need to understand how to call the service.

## Finding 8 — Adjacent endpoint expansion should follow usage, not imagination

After SchemaCheck Agent, likely adjacent endpoints include:

- API response validator
- JSON repair endpoint
- OpenAPI contract checker
- Payload normalizer
- Test-case generator

But these should be created only after real usage or repeated failure patterns reveal demand.

