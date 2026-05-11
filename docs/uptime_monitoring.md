# Uptime Monitoring — SchemaCheck Agent

_Created: 2026-05-11_

---

## Overview

SchemaCheck Agent exposes a `/health` endpoint that returns `200 OK` when the service is running. UptimeRobot (free tier) polls this endpoint every 5 minutes and sends an email alert if it stops responding.

This covers the most important gap: **knowing when the service is down without having to check manually.**

---

## Setup: UptimeRobot (free, takes ~5 minutes)

### 1. Create an account

Go to [https://uptimerobot.com](https://uptimerobot.com) and sign up for a free account. The free tier supports up to 50 monitors at 5-minute polling intervals.

### 2. Add a new monitor

From the dashboard, click **+ Add New Monitor**.

| Field | Value |
|---|---|
| Monitor Type | `HTTP(s)` |
| Friendly Name | `SchemaCheck Agent - Health` |
| URL | `https://projectx402-production.up.railway.app/health` |
| Monitoring Interval | `Every 5 minutes` |
| Monitor Timeout | `30 seconds` |

### 3. Configure alert contacts

Under **Alert Contacts**, make sure your email address is added and confirmed. UptimeRobot will send:

- An **alert email** when the service goes down
- A **recovery email** when it comes back up

### 4. Expected healthy response

UptimeRobot checks for HTTP `200 OK`. The `/health` endpoint returns:

```json
{"status": "ok", "service": "schemacheck-agent", "version": "0.3.0"}
```

No additional keyword matching is needed — the `200` status is sufficient.

### 5. Verify the monitor is working

After saving, UptimeRobot will run an immediate check. The monitor status should show **Up** within 30 seconds. If it shows **Down**, verify the Railway deployment is running by visiting the health URL in a browser.

---

## What UptimeRobot does NOT cover

| Scenario | Covered? | Alternative |
|---|---|---|
| Service crashed / restarted | ✓ Detected within 5 minutes | — |
| Slow responses (latency spike) | ✗ | Railway logs |
| Payment verification failures | ✗ | Railway logs |
| Validation errors in responses | ✗ | GitHub Issues from callers |
| Partial outage (some requests fail) | ✗ | Railway logs |

---

## Railway crash alerts

In addition to UptimeRobot, enable Railway's own notifications:

1. Open the Railway dashboard for the `project_x402` service
2. Go to **Settings → Notifications**
3. Enable email alerts for **deployment failures** and **crash/restart loops**

This gives early warning before UptimeRobot's 5-minute polling window catches the downtime.

---

## When an alert fires

If UptimeRobot reports the service is down:

1. Check [Railway dashboard](https://railway.app) → project_x402 → **Deployments** tab for crash logs
2. Check **Logs** tab for the last error before the crash
3. If a bad deploy caused it, use Railway's **Rollback** button to revert to the previous deployment
4. If the service restarts itself, check whether Railway's health check is configured — Railway can restart crashed processes automatically if a health check path is set

---

## Status page (optional, future)

UptimeRobot's free tier also generates a public status page at a URL like `https://stats.uptimerobot.com/xxxx`. This can be linked from the README to give external callers visibility into uptime history without needing to contact you.
