# Railway Deployment Runbook

## Purpose

Deploy SchemaCheck Agent as a public FastAPI service on Railway.

## Current deployment mode

Initial Railway deployment should run with payment disabled so `/health` and `/v1/schema-check` can be tested publicly before enabling x402 behavior.

Recommended first Railway variables:

```text
SCHEMACHECK_PAYMENT_MODE=disabled
SCHEMACHECK_LOG_REQUESTS=true
SCHEMACHECK_APP_VERSION=0.3.0
```

Keep these x402 values documented but do not enable live verification yet:

```text
SCHEMACHECK_X402_PAY_TO=0x8fC4006534801c17A3368075A1Fb3b3C511EdB1F
SCHEMACHECK_X402_NETWORK=eip155:84532
SCHEMACHECK_X402_SCHEME=exact
SCHEMACHECK_X402_PRICE=$0.005
SCHEMACHECK_X402_FACILITATOR_URL=https://x402.org/facilitator
SCHEMACHECK_X402_REAL_VERIFICATION_ENABLED=false
```

## Files added for Railway

- `railway.toml` — Railway build/deploy settings.
- `Procfile` — fallback process command.

The app starts with:

```text
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Railway supplies `$PORT` at runtime.

## Deployment steps

1. Push the latest project to GitHub.
2. In Railway, create a new project.
3. Choose deploy from GitHub repo.
4. Select `garyedgington/project_x402`.
5. Add the environment variables listed above.
6. Deploy.
7. Open the generated Railway public URL.
8. Test:

```text
GET /health
```

Expected response:

```json
{"status":"ok","service":"schemacheck-agent","version":"0.3.0"}
```

## First public test order

1. `/health` returns 200.
2. `/v1/schema-check` works with `examples/valid_payload.json` while payment mode is disabled.
3. Switch `SCHEMACHECK_PAYMENT_MODE=x402`.
4. Confirm unpaid request returns `402 Payment Required`.
5. Keep real verification disabled until testnet payment client flow is ready.

## Human monitoring

Use Railway dashboard logs for:

- app startup
- request logs
- errors
- restarts
- deployment history

Use GitHub for source history and deployment source of truth.
