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

---

_Updated: 2026-05-11 — Phase 4–5 deployment and first live x402 payment_

## Lesson 9 — Windows UTF-16 BOM encoding silently breaks Linux deployments

When a file like `requirements.txt` is created or edited on Windows, it may be saved with a UTF-16 BOM (byte-order mark). Linux pip cannot parse UTF-16 files and fails with cryptic errors. Always write deployment files with `Out-File -Encoding utf8NoBOM` in PowerShell or use a Linux-side editor. This was the root cause of 15+ Railway build failures.

## Lesson 10 — Railway branch tracking must be set explicitly

Railway defaults to tracking the `main` branch. If your repo uses `master` or any other branch, deployments will silently use old builds. Verify Railway Settings → Source → Branch matches the branch you are actually pushing to.

## Lesson 11 — x402 v2 protocol differs significantly from v1

The x402 SDK v2 PaymentRequired schema uses an `accepts` array with `asset`/`amount`/`payTo`/`maxTimeoutSeconds` fields — not the v1 `price`/`facilitator` flat fields. The payment header sent by v2 clients is `PAYMENT-SIGNATURE`, not `X-PAYMENT`. Server code must accept both for backward compatibility.

## Lesson 12 — EIP-712 domain must match exactly for USDC on Base Sepolia

The x402 exact EVM scheme requires an EIP-712 domain in the `extra` field of PaymentRequirements: `{"name": "USDC", "version": "2"}`. The name must be exactly `"USDC"` (not `"USD Coin"` or anything else). This value must appear identically in both the 402 response sent to the client and the PaymentRequirements object used for server-side verification. A mismatch causes `invalid_exact_evm_token_name_mismatch` from the facilitator.

## Lesson 13 — Use sync facilitator client inside sync FastAPI endpoints

FastAPI sync route handlers (no `async def`) must use `HTTPFacilitatorClientSync` and `x402ResourceServerSync` from the x402 SDK. Using the async variants inside a sync context raises a `requires a sync facilitator client` error at runtime.

## Lesson 14 — Circle faucet reports success but often delivers nothing

The Circle USDC testnet faucet at faucet.circle.com frequently confirms delivery but sends no tokens. The Coinbase Developer Platform faucet at portal.cdp.coinbase.com/products/faucet is more reliable for Base Sepolia ETH. For USDC specifically, CDP also has a faucet option that actually delivers. Always verify with an on-chain balance check after any faucet claim, not just the faucet's confirmation message.

## Lesson 15 — First live x402 testnet payment: full flow confirmed

On 2026-05-11, the first real x402 v2 USDC micropayment on Base Sepolia testnet completed successfully end-to-end:
- Server deployed on Railway returned 402 with v2 PaymentRequired
- Client parsed x402Version=2, accepted USDC on eip155:84532
- EIP-3009 TransferWithAuthorization signed with test wallet
- Facilitator at x402.org verified and settled the payment
- Server returned 200 with valid SchemaCheck result
- Payment amount: 5000 atomic units = $0.005 USDC

---

_Updated: 2026-05-13 — Phase 4b MCP adapter layer complete and submitted to directories_

## Lesson 24 — FastMCP requires live type objects; do not use `from __future__ import annotations` in MCP server files

FastMCP's tool registration calls `inspect.signature()` at decoration time and then does `issubclass(param.annotation, Context)` to check whether a parameter is an MCP Context. With `from __future__ import annotations`, all annotations are stored as lazy strings rather than live type objects, causing `issubclass` to raise `TypeError`. Remove the future import from any file that registers FastMCP tools.

## Lesson 25 — Use a Union type alias instead of bare `Any` for JSON payload parameters in FastMCP

FastMCP's guard at `base.py` checks `get_origin(annotation) is None` and then calls `issubclass`. Bare `typing.Any` has `get_origin() == None`, which causes it to fall into the `issubclass` branch and raise `TypeError`. Use a Union alias instead:

```python
_JSON = Union[Dict[str, Any], List[Any], str, int, float, bool, None]
```

This has `get_origin() != None` (it is `Union`), so FastMCP skips the `issubclass` check entirely.

## Lesson 26 — FastMCP's streamable HTTP sub-app must be built once and shared between lifespan and mount

`mcp.streamable_http_app()` returns an ASGI sub-app that holds a reference to the same `StreamableHTTPSessionManager` instance. Call it once at module level, assign it to `_mcp_asgi`, then use that variable in both the FastAPI lifespan and the `app.mount()` call. Calling it twice creates two separate session managers — one started, one not — causing 500 "Task group is not initialized" errors on some requests.

## Lesson 27 — Mount the FastMCP sub-app at `"/"` not `"/mcp"`, placed after all FastAPI routes

FastMCP's `streamable_http_app()` creates its own internal route at `/mcp`. If you mount it at `/mcp`, Starlette strips that prefix and the sub-app sees `/` — which doesn't match `/mcp`, so all requests 404. Mount at `"/"` instead, and place the mount call at the very end of `main.py` after all FastAPI routes are registered. FastAPI routes take precedence over the catch-all mount.

## Lesson 28 — FastAPI lifespan is required to start the FastMCP session manager

`StreamableHTTPSessionManager.run()` is an asynccontextmanager that must be entered before any MCP request arrives. Without it, the first request fails with "Task group is not initialized." Wire it into the FastAPI lifespan:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with mcp.session_manager.run():
        yield

app = FastAPI(..., lifespan=lifespan)
```

## Lesson 29 — MCP Streamable HTTP requires a three-step handshake before tools/list

The MCP spec (2025-03-26) requires: (1) `initialize` request → server responds with capabilities; (2) `notifications/initialized` notification → no response expected; (3) `tools/list` → server returns tool list. Skipping step 2 causes the server to reject step 3 with `-32602 Invalid request parameters`. Most directory crawlers (Smithery, mcp.so) do not complete this handshake and will show "0 tools" — this is a crawler limitation, not a server bug.

## Lesson 30 — `smithery.yaml` static tool declarations only work for local (npm/uvx) servers on Smithery

Smithery reads `smithery.yaml` to auto-configure local server startup. For remote HTTP servers, it does live introspection only. If the introspection fails (e.g. due to handshake requirements), tools show as "0 capabilities" in the directory even if the server is fully functional. The server is still usable by any MCP client that completes the proper handshake.

## Lesson 31 — OneDrive sync lag causes stale `.pyc` caches in the Linux sandbox

Files written via Claude's Edit/Write tools (Windows path) take time to sync to the Linux mount used by the bash sandbox. During the sync window, the sandbox may read a truncated or previous version of the file and compile a stale `.pyc`. Fix: after writing files through Edit/Write, either wait for OneDrive sync to complete or rewrite the file directly through bash using a Python heredoc script to bypass the cache.

## Lesson 32 — `git add` with `GIT_INDEX_FILE` pointing to a temp path stages only files added in that session

When a stale `index.lock` prevents normal `git add`, using `GIT_INDEX_FILE=/tmp/git-index-tmp git add` creates a fresh temporary index. That temporary index contains only the files explicitly added in that shell call — not the full working tree tracked files. A subsequent `git commit` using that temp index will appear to delete all other tracked files. Always resolve the lock file first (delete via Windows Explorer) rather than using a temp index for commits.

---

_Updated: 2026-05-12 — GitHub repo reconciliation and Formatter + A2A project setup_

## Lesson 16 — EIP-712 domain name differs between testnet and mainnet

Base Sepolia USDC uses `{"name": "USDC", "version": "2"}` as the EIP-712 domain. Base mainnet USDC uses `{"name": "USD Coin", "version": "2"}`. This value must be correct in both the 402 response `extra` field and the server-side `PaymentRequirements` object. A mismatch will cause the CDP facilitator to reject the payment.

## Lesson 17 — The x402 Bazaar only indexes after a payment is processed

The CDP Bazaar discovery layer does not crawl endpoints or accept manual submissions. It indexes a service automatically when the CDP facilitator processes a completed payment that includes the `bazaar` extension in the 402 response. No payment through the endpoint = not in the Bazaar. The first real mainnet payment is what triggers indexing.

## Lesson 18 — UptimeRobot sends HEAD requests by default; FastAPI @app.get does not accept HEAD

UptimeRobot's HTTP(s) monitor sends HEAD requests, not GET. FastAPI's `@app.get` decorator only accepts GET, returning 405 Method Not Allowed for HEAD. This causes UptimeRobot to report the service as down even when it is healthy. Fix: use `@app.api_route("/health", methods=["GET", "HEAD"])` instead of `@app.get`.

## Lesson 19 — USDC exists separately on each network; specify Base when sending

USDC on Ethereum mainnet and USDC on Base mainnet are separate assets. Coinbase.com allows sending USDC on multiple networks — you must explicitly select Base as the network when sending, otherwise it defaults to Ethereum. Also, Coinbase may restrict recently purchased USDC from transfer until it fully settles, even if it appears in your balance.

## Lesson 20 — Keep GitHub as the authoritative source; commit and push after every session

Local files diverged significantly from GitHub over multiple sessions, creating a gap between what GitHub showed (early MVP, one commit) and what Railway was actually deploying (full live code from local master). Always commit and push at the end of every session. GitHub should reflect the live state at all times — it is the primary location to validate workability.

## Lesson 21 — Never commit scripts containing private keys; add them to .gitignore immediately

Test and utility scripts (`test_payment.py`, `swap_eth_for_usdc.py`, `check_balance.py`) contained the test wallet private key hardcoded. These were never committed, but they also were not in `.gitignore`, leaving them at risk of accidental staging. Add any file containing wallet private keys, seed phrases, or credentials to `.gitignore` the moment it is created — not after.

## Lesson 22 — Consolidate to one branch (`main`) from day one

Working on a `master` branch while GitHub's default was `main` created a persistent stale split: GitHub showed old code, Railway had to be pointed at `master` explicitly, and cloning the repo fetched the wrong branch by default. For all new projects, use `main` exclusively from the first commit. Rename `master` to `main` immediately if the split already exists: `git branch -m master main && git push origin main --force`.

---

_Updated: 2026-05-14 — Smithery 100/100 achieved_

## Lesson 33 — Smithery quality score is driven by server-card.json, not live MCP scan

Smithery's quality score (Capability Quality, Server Metadata, Configuration UX) reads exclusively from `/.well-known/mcp/server-card.json`. Live MCP tool introspection only affects the connectivity/uptime badge. The score for output schemas and annotations comes from whether those fields are present in the static server-card.json endpoint — not from what FastMCP auto-generates for live tools. Always update server-card.json when adding tool metadata.

## Lesson 34 — `outputSchema` and `annotations` must be explicitly added to server-card.json

Smithery's quality score deducts ~10pt for missing `outputSchema` and ~6pt for missing `annotations` per tool. These fields must be added manually to each tool entry in the `/.well-known/mcp/server-card.json` endpoint. FastMCP will auto-generate these for live MCP introspection, but Smithery does not read them from there — it reads the static card.

`annotations` format:
```json
{
  "readOnlyHint": true,
  "destructiveHint": false,
  "idempotentHint": true,
  "openWorldHint": false
}
```

`outputSchema` format: standard JSON Schema object describing the tool's return structure.

## Lesson 35 — Use `typing_extensions.TypedDict` not `typing.TypedDict` with FastMCP on Python < 3.12

FastMCP uses Pydantic to auto-generate `outputSchema` from a tool's return type annotation. On Python < 3.12, Pydantic's `create_model()` raises `PydanticUserError` when given `typing.TypedDict`. The fix is to import from `typing_extensions` instead:

```python
from typing_extensions import TypedDict  # not: from typing import TypedDict
```

This applies to all TypedDict classes used as return types in FastMCP tools, including nested ones.

## Lesson 36 — A later commit can silently revert an earlier fix in the same file

When a commit modifies a file that was previously changed in a different commit, it can accidentally re-introduce old code if the author copies from an older version. In this project, commit `4c28084` (adding inputSchema to server-card.json) re-reverted `app.mount("/", mcp.sse_app())` back to `app.mount("/mcp", mcp.sse_app())` while editing main.py. Always diff the full file against HEAD before committing, especially when the change is "add something to an existing block."

## Lesson 37 — Git index.lock on Windows-mounted repos blocks all git operations from Linux sandbox

When git operations run through a Windows-mounted filesystem in the Linux bash sandbox, a stale `.git/index.lock` can be left behind (e.g. after a failed command). The Linux sandbox cannot remove it (`Operation not permitted`). It must be deleted from Windows:

```powershell
Remove-Item "D:\path\to\project\.git\index.lock" -Force
```

Until the lock is removed, all `git add`, `git commit`, and `git status` calls will fail with "Another git process seems to be running."

## Lesson 38 — Verify full MCP handshake with PowerShell before blaming Smithery

To manually verify the full SSE → initialize flow:
1. `curl.exe -N -H "Accept: text/event-stream" https://host/sse` — watch for `data: /messages/?session_id=xxx`
2. In a new window: `Invoke-RestMethod -Uri "https://host/messages/?session_id=xxx" -Method POST -ContentType "application/json" -Body '{"jsonrpc":"2.0","id":1,"method":"initialize",...}'`
3. Expected: `"Accepted"` response. The actual JSON-RPC response appears in the SSE stream in window 1.

Use `Invoke-RestMethod` not `curl.exe` for JSON POST in PowerShell — curl.exe mangles multi-line JSON with backtick continuation.

## Lesson 39 — Smithery "No config schema provided" warning cannot be suppressed server-side

Smithery shows "Warning: No config schema provided" in scan logs for any server that has no configurable parameters. This warning persists regardless of what is in `smithery.yaml` or `server-card.json`. It is an automated informational check, does not affect the quality score, and is not user-facing. It can be safely ignored for services that genuinely require no configuration.

## Lesson 23 — Every new Railway service needs a Procfile and railway.toml at scaffold time

Railpack cannot auto-detect a start command when the FastAPI entry point is at `app/main.py` instead of `main.py` in the project root. Without a `Procfile` and `railway.toml`, the build fails with "No start command detected." Both files must be included when scaffolding any new service — not added retroactively after a failed deploy.

`Procfile`:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

`railway.toml`:
```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 100
```

