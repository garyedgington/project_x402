# Monitoring Plan

## Current human monitoring

Project x402 is currently monitored locally by the developer/product manager through:

- PowerShell server logs while Uvicorn is running
- pytest results
- GitHub commit history
- manual API checks against `/health` and `/v1/schema-check`

## Next deployment monitoring

After public deployment, monitoring should show:

- service online/offline state
- request count
- HTTP error count
- average latency
- restart/crash history
- deployment version

## Payment monitoring

After real x402 payment is enabled, monitoring should show:

- unpaid requests
- paid requests
- failed payment verification
- settled payment count
- wallet deposits
- estimated revenue

## Minimal first dashboard

The first human-readable dashboard only needs:

- calls today
- paid calls today
- errors today
- average response time
- revenue estimate
- latest app version
