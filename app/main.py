from __future__ import annotations

import json
from dataclasses import dataclass, field
from threading import Lock

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from jsonschema import exceptions

from app.config import get_settings
from app.mcp_server import mcp
from app.models import HealthResponse, ResponseMeta, SchemaCheckRequest, SchemaCheckResponse
from app.payment import enforce_payment
from app.telemetry import request_logging_middleware
from app.validator import suggest_repair, summarize, validate_payload

settings = get_settings()
APP_VERSION = settings.app_version

TRIAL_MAX_BYTES = 32_768  # 32KB limit for trial endpoint


@dataclass
class _CallCounters:
    paid: int = 0
    trial: int = 0
    _lock: Lock = field(default_factory=Lock, compare=False, repr=False)

    def inc_paid(self) -> None:
        with self._lock:
            self.paid += 1

    def inc_trial(self) -> None:
        with self._lock:
            self.trial += 1

    def snapshot(self) -> dict:
        with self._lock:
            return {"paid": self.paid, "trial": self.trial}


_counters = _CallCounters()

app = FastAPI(
    title="Project x402 SchemaCheck Agent",
    version=APP_VERSION,
    description=(
        "Validate JSON payloads against JSON Schema. "
        "POST /v1/schema-check requires x402 USDC micropayment ($0.005). "
        "POST /v1/schema-check/trial is free, no repair suggestions, 32KB limit."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "HEAD"],
    allow_headers=["*"],
)

if settings.log_requests:
    app.middleware("http")(request_logging_middleware)

# MCP adapter -- exposes validate_schema tools via streamable HTTP transport.
# Mounted after middleware so CORS and logging apply to /mcp as well.
# Remote MCP URL: https://projectx402-production.up.railway.app/mcp
app.mount("/mcp", mcp.streamable_http_app())


@app.api_route("/health", methods=["GET", "HEAD"], response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="schemacheck-agent", version=APP_VERSION)


@app.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
def dashboard() -> HTMLResponse:
    return HTMLResponse(content=_DASHBOARD_HTML)


_DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>SchemaCheck Monitor</title>
<style>
  :root { color-scheme: light; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
         background: #f8f9fa; color: #111; padding: 28px 24px; max-width: 520px; }
  h1  { font-size: 16px; font-weight: 700; margin-bottom: 3px; }
  .sub { font-size: 12px; color: #888; margin-bottom: 22px; }
  .grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-bottom: 22px; }
  .card { background: #fff; border: 1px solid #e5e7eb; border-radius: 10px; padding: 14px; }
  .card-label { font-size: 10px; font-weight: 700; color: #999; text-transform: uppercase;
                letter-spacing: 0.06em; margin-bottom: 6px; }
  .card-value { font-size: 28px; font-weight: 700; color: #111; line-height: 1; }
  .card-sub   { font-size: 11px; color: #888; margin-top: 4px; }
  .status-row { display: flex; align-items: center; gap: 7px; margin-bottom: 20px; }
  .dot { width: 9px; height: 9px; border-radius: 50%; background: #d1d5db; flex-shrink: 0; }
  .dot.live { background: #22c55e; box-shadow: 0 0 0 3px rgba(34,197,94,.2); }
  .dot.down { background: #ef4444; }
  #status-text { font-size: 13px; font-weight: 600; }
  #version     { font-size: 12px; color: #888; margin-left: 4px; }
  .footer { font-size: 11px; color: #bbb; margin-top: 20px; }
  a { color: #6b7280; }
</style>
</head>
<body>
<h1>SchemaCheck Agent</h1>
<p class="sub">Base mainnet &middot; $0.005 USDC / call &middot; x402 v2</p>

<div class="status-row">
  <div class="dot" id="dot"></div>
  <span id="status-text">Checking&hellip;</span>
  <span id="version"></span>
</div>

<div class="grid">
  <div class="card">
    <div class="card-label">Paid calls</div>
    <div class="card-value" id="paid">&mdash;</div>
    <div class="card-sub">this session</div>
  </div>
  <div class="card">
    <div class="card-label">Trial calls</div>
    <div class="card-value" id="trial">&mdash;</div>
    <div class="card-sub">this session</div>
  </div>
  <div class="card">
    <div class="card-label">Total</div>
    <div class="card-value" id="total">&mdash;</div>
    <div class="card-sub">this session</div>
  </div>
</div>

<div class="footer">
  Auto-refreshes every 30s &middot; counts reset on restart<br>
  Wallet: <a href="https://basescan.org/address/0x8fC4006534801c17A3368075A1Fb3b3C511EdB1F#tokentxns"
             target="_blank">0x8fC4...001B on Basescan</a> (permanent paid-call record)<br>
  <span id="last-updated"></span>
</div>

<script>
async function refresh() {
  try {
    const [h, s] = await Promise.all([
      fetch('/health').then(r => r.json()),
      fetch('/v1/stats').then(r => r.json())
    ]);
    document.getElementById('dot').className = h.status === 'ok' ? 'dot live' : 'dot down';
    document.getElementById('status-text').textContent = h.status === 'ok' ? 'Live' : 'Down';
    document.getElementById('version').textContent = 'v' + h.version;
    document.getElementById('paid').textContent  = s.paid_calls_this_session;
    document.getElementById('trial').textContent = s.trial_calls_this_session;
    document.getElementById('total').textContent = s.total_this_session;
  } catch(e) {
    document.getElementById('dot').className = 'dot down';
    document.getElementById('status-text').textContent = 'Unreachable';
  }
  document.getElementById('last-updated').textContent =
    'Last updated: ' + new Date().toLocaleTimeString();
}
refresh();
setInterval(refresh, 30000);
</script>
</body>
</html>"""


@app.get("/v1/stats", summary="Call counts for this session")
def stats() -> dict:
    counts = _counters.snapshot()
    return {
        "paid_calls_this_session": counts["paid"],
        "trial_calls_this_session": counts["trial"],
        "total_this_session": counts["paid"] + counts["trial"],
        "note": "Counts reset when the service restarts. Check Railway logs for full history.",
        "railway_logs": "https://railway.com/project/7c8b7de8-53e1-476f-88c3-d964022f3092/logs",
    }


@app.post("/v1/schema-check", response_model=SchemaCheckResponse, dependencies=[Depends(enforce_payment)])
def schema_check(request: SchemaCheckRequest) -> SchemaCheckResponse:
    try:
        errors = validate_payload(request.json_schema, request.payload)
    except exceptions.SchemaError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_JSON_SCHEMA",
                "message": exc.message,
                "path": list(exc.absolute_path),
                "schema_path": list(exc.absolute_schema_path),
            },
        ) from exc

    valid = len(errors) == 0
    suggested_payload = None
    if request.repair and not valid:
        suggested_payload = suggest_repair(request.json_schema, request.payload, errors, request.strictness)

    confidence = 1.0 if valid else 0.9
    if suggested_payload is not None:
        confidence = 0.75

    _counters.inc_paid()

    return SchemaCheckResponse(
        valid=valid,
        errors=errors,
        summary=summarize(valid, errors, request.explain),
        suggested_payload=suggested_payload,
        confidence=confidence,
        meta=ResponseMeta(
            strictness=request.strictness,
            repair_attempted=request.repair,
        ),
    )


@app.post(
    "/v1/schema-check/trial",
    response_model=SchemaCheckResponse,
    summary="Trial - no payment required",
    description=(
        "Free trial endpoint. No x402 payment required. "
        "Repair suggestions are disabled. Request body must not exceed 32KB. "
        "Use POST /v1/schema-check for full access including repair suggestions."
    ),
)
async def schema_check_trial(raw_request: Request, request: SchemaCheckRequest) -> SchemaCheckResponse:
    body = await raw_request.body()
    if len(body) > TRIAL_MAX_BYTES:
        raise HTTPException(
            status_code=413,
            detail={
                "code": "TRIAL_PAYLOAD_TOO_LARGE",
                "message": f"Trial endpoint request body must not exceed {TRIAL_MAX_BYTES // 1024}KB. "
                           "Use the paid endpoint POST /v1/schema-check for larger requests.",
            },
        )

    try:
        errors = validate_payload(request.json_schema, request.payload)
    except exceptions.SchemaError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_JSON_SCHEMA",
                "message": exc.message,
                "path": list(exc.absolute_path),
                "schema_path": list(exc.absolute_schema_path),
            },
        ) from exc

    valid = len(errors) == 0
    confidence = 1.0 if valid else 0.9

    _counters.inc_trial()

    return SchemaCheckResponse(
        valid=valid,
        errors=errors,
        summary=summarize(valid, errors, request.explain),
        suggested_payload=None,
        confidence=confidence,
        meta=ResponseMeta(
            strictness=request.strictness,
            repair_attempted=False,
        ),
    )
