from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException
from jsonschema import exceptions

from app.config import get_settings
from app.models import HealthResponse, ResponseMeta, SchemaCheckRequest, SchemaCheckResponse
from app.payment import enforce_payment
from app.telemetry import request_logging_middleware
from app.validator import suggest_repair, summarize, validate_payload

settings = get_settings()
APP_VERSION = settings.app_version

app = FastAPI(
    title="Project x402 SchemaCheck Agent",
    version=APP_VERSION,
    description="MVP endpoint for validating JSON payloads against JSON Schema.",
)

app.middleware("http")(request_logging_middleware)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="schemacheck-agent", version=APP_VERSION)


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
