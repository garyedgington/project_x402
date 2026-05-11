# SchemaCheck Agent — Phase 6 Distribution Plan

_Created: 2026-05-11_  
_Owner: Gary_

---

## Objective

Find out whether agents or developers will actually call the endpoint. Publish the service in relevant communities and registries, then track which channels produce real calls.

**Exit criteria:** At least one external caller has used the endpoint, OR there is clear evidence that the current distribution path is ineffective and needs adjustment.

---

## Target audiences

| Audience | Why they'd use it | Where to reach them |
|---|---|---|
| AI agent developers | Need to validate structured outputs from LLMs | GitHub, HuggingFace forums, AI Discord servers |
| Backend developers | Need per-call validation without a library dependency | Dev.to, Hacker News, Reddit r/webdev |
| x402 / crypto developer community | Already understand x402 payment rails | x402.org, Coinbase Developer Platform forums, Base ecosystem channels |
| LLM tool / function-calling users | Need to validate tool call results | OpenAI community, Anthropic community forums |

---

## Distribution channels — priority order

### Tier 1 — highest signal, lowest effort

These channels are most likely to reach people who would actually call the endpoint.

- [ ] **GitHub README** — Already updated. Make sure the repo is public and searchable.
  - Repo: `github.com/garyedgington/project_x402`
  - Ensure repo description and topics are set: `json-schema`, `validation`, `x402`, `micropayments`, `agent`, `api`

- [ ] **x402.org ecosystem** — The x402.org site and community are directly aligned with the payment model.
  - Check if x402.org has a registry, showcase, or list of live x402 services
  - Submit SchemaCheck Agent as an example live x402 endpoint

- [ ] **Coinbase Developer Platform / Base ecosystem**
  - Base has an active developer community; x402 is a Coinbase-adjacent standard
  - Post in CDP Discord or developer forum: "Built a live x402 v2 endpoint — here's how the payment flow works"

### Tier 2 — broader developer reach

- [ ] **Hacker News Show HN** — Post as "Show HN: A paid JSON Schema validation API using x402 micropayments"
  - Best day/time: Tuesday–Thursday, 9–11am US Eastern
  - Keep it short: what it is, how to try it, why x402 is interesting for agents

- [ ] **Dev.to post** — Write a short technical article: "How I built a machine-native paid API with x402 micropayments"
  - Include the trial endpoint curl example so readers can try it immediately
  - Tag: `python`, `api`, `json`, `web3`, `agents`

- [ ] **Reddit**
  - r/Python — focus on the FastAPI + jsonschema implementation
  - r/webdev — focus on the x402 payment concept
  - r/LLMAgents or r/LocalLLaMA — focus on agent-native use cases

### Tier 3 — targeted agent/AI community outreach

- [ ] **AI agent Discord servers** — Many active communities (e.g. AutoGPT, CrewAI, LangChain Discord)
  - Post in `#tools` or `#resources` channels: "Free trial endpoint for validating JSON agent outputs"
  - Emphasise the trial endpoint — no wallet needed to try

- [ ] **OpenAI / Anthropic developer communities**
  - OpenAI community forum: post as a tool for validating function-calling outputs
  - Anthropic Discord: post as a tool for validating structured Claude outputs

---

## Tracking — how to know which channel works

### Request headers to watch

Every caller is logged with `request_id`, `method`, `path`, `status`, and `duration_ms` via the telemetry middleware.

For distribution tracking, ask callers (in docs and post copy) to include a `Referer` or `X-Source` header identifying where they found the service:

```
X-Source: hn          # Hacker News
X-Source: devto       # Dev.to
X-Source: x402        # x402.org
X-Source: github      # GitHub README
X-Source: discord     # Discord
```

### What to log per channel

| Metric | How to measure |
|---|---|
| Trial calls | Count of `POST /v1/schema-check/trial` in Railway logs |
| Paid calls | Count of `POST /v1/schema-check` returning 200 in Railway logs |
| Payment failures | Count of 402s that never followed up with a paid call |
| Source channel | `X-Source` header value in logs |
| Repeat callers | Same IP or same wallet address appearing more than once |

### Weekly review cadence

Check Railway logs once per week and record:

| Week | Trial calls | Paid calls | Payment failures | Top source channel | Notes |
|---|---|---|---|---|---|
| 2026-W20 | — | — | — | — | Distribution started |
| 2026-W21 | | | | | |
| 2026-W22 | | | | | |

---

## Messaging — what to say

### One-liner
> A tiny paid API that validates JSON payloads against JSON Schema, using x402 USDC micropayments. Try it free, pay $0.005/call for full access.

### Trial-first pitch (for non-crypto audiences)
> No wallet needed to try. POST your JSON Schema and payload to our trial endpoint, get back structured errors and a plain-English summary. No signup, no API key.

### x402-native pitch (for crypto/agent audiences)
> SchemaCheck Agent is a live x402 v2 endpoint. Send a payload validation request, get a 402 back, sign an EIP-3009 USDC transfer on Base Sepolia, and receive your result. $0.005 per call, no subscription.

---

## Action checklist

- [ ] Confirm GitHub repo is public and has correct topics set
- [ ] Check x402.org for a live services registry or showcase — submit if available
- [ ] Post in Coinbase / Base developer Discord
- [ ] Write and schedule Dev.to post
- [ ] Submit Show HN
- [ ] Post in 1–2 relevant Reddit threads
- [ ] Post trial endpoint link in 1–2 AI agent Discord servers
- [ ] Add `X-Source` header guidance to agent_quickstart.md
- [ ] Record first week's call counts in the tracking table above
