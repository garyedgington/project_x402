# Project x402 — Lessons Learned

_Last updated: 2026-05-09_

## Lesson 1 — Do not automate prohibited human microtask systems

The project must avoid surveys, ad clicks, CAPTCHA solving, referral farming, fake engagement, or platforms that prohibit bots. That path creates compliance risk and weak strategic footing.

The safe path is to build services where software agents and automated callers are expected and allowed.

## Lesson 2 — Own the task supply

Rather than chasing microtasks created by someone else, create the microtask as a paid API endpoint.

Owning the endpoint means owning:

- Pricing
- Terms
- Quality standard
- Logging
- Distribution
- Improvement loop
- Adjacent product expansion

## Lesson 3 — Start with validation, not intelligence

The first service should be easy to judge. Schema validation, payload correction, and API response validation are better first experiments than broad reasoning services because success or failure can be measured.

## Lesson 4 — Micropayment products need unit economics from day one

At $0.001 to $0.01 per request, the project cannot tolerate expensive inference, high retries, or vague work. Every call should be measured for revenue, cost, latency, and failure.

## Lesson 5 — Agents need machine-readable docs

Human-oriented marketing pages are secondary. Agent-readable documentation, examples, schemas, and predictable error formats are essential.

## Lesson 6 — Expansion should be usage-led

The long-term goal is a portfolio of paid microservices, but premature expansion creates maintenance burden. Build one endpoint, observe real usage, then add only the adjacent services that users or agents actually need.

## Lesson 7 — Keep the task narrow enough to be trusted

A tiny service that always validates payloads correctly is more useful than a broad agent that sometimes gives impressive but unreliable answers.

## Lesson 8 — The strategic advantage is the feedback loop

The agent service is the engine, but the durable advantage comes from logs, failure cases, improvements, documentation, and increasingly reliable endpoint behavior.

