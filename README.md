# Project x402 Workspace

This folder is the working sandbox workspace for Project x402 in this ChatGPT session.

## Files

- `resume.md` — project restart/resume context
- `findings.md` — recalled and synthesized findings
- `lessons_learned.md` — project lessons and operating rules
- `phase_plan.md` — phased execution plan

## Note

This workspace is stored in the ChatGPT session sandbox, not on the user's local computer. Download or export files you want to preserve outside this session.

## Railway deployment

This project includes Railway deployment files:

- `railway.toml`
- `Procfile`
- `docs/railway_deployment.md`

Initial public deployment should use `SCHEMACHECK_PAYMENT_MODE=disabled`. After `/health` and `/v1/schema-check` pass publicly, switch to `SCHEMACHECK_PAYMENT_MODE=x402` to test unpaid `402 Payment Required` behavior. Real x402 verification remains guarded by `SCHEMACHECK_X402_REAL_VERIFICATION_ENABLED=false` until testnet payment flow is ready.

