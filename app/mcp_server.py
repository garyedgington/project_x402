"""
MCP adapter for the SchemaCheck Agent.

Exposes the validator logic as MCP tools via SSE transport,
bypassing the x402 payment gate entirely (billing is handled by MCP-Hive
at the protocol layer instead).

Mount point: / (root, so SSE at /sse and messages at /messages/)
Transport:   SSE

Tools:
  validate_schema       - full validation + optional repair
  validate_schema_trial - validation only, no repair (free tier)
"""

# NOTE: intentionally no "from __future__ import annotations" here.
# FastMCP's tool registration uses inspect.signature() at decoration time
# and calls issubclass(param.annotation, Context) -- which requires live
# type objects, not the lazy strings that the future import produces.
from typing import Any, Dict, List, Literal, Optional, Union
from typing_extensions import TypedDict

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

# JSON-safe union used for 'payload' parameters.
# Avoids bare typing.Any which has get_origin()==None and trips
# FastMCP's issubclass(annotation, Context) guard in mcp <1.9.
_JSON = Union[Dict[str, Any], List[Any], str, int, float, bool, None]

from app.models import Strictness
from app.validator import suggest_repair, summarize, validate_payload

# ---------------------------------------------------------------------------
# Output type definitions (used by FastMCP to generate outputSchema)
# ---------------------------------------------------------------------------

class ValidationMeta(TypedDict):
    strictness: str
    repair_attempted: bool
    engine: str
    schema_draft: str


class ValidationResult(TypedDict):
    valid: bool
    errors: List[Dict[str, Any]]
    summary: str
    suggested_payload: Optional[Any]
    confidence: float
    meta: ValidationMeta


# ---------------------------------------------------------------------------
# Shared annotations: both tools are read-only and idempotent
# ---------------------------------------------------------------------------

_READONLY_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=False,
)

# ---------------------------------------------------------------------------
# Server instance
# ---------------------------------------------------------------------------

mcp = FastMCP(
    name="SchemaCheck Agent",
    instructions=(
        "Validates JSON payloads against JSON Schema definitions (Draft 2020-12). "
        "Call validate_schema to check whether a JSON payload conforms to a schema "
        "and optionally receive a corrected payload when validation fails. "
        "Call validate_schema_trial for a free, no-repair validation check."
    ),
)


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool(annotations=_READONLY_ANNOTATIONS)
def validate_schema(
    json_schema: Dict[str, Any],
    payload: _JSON,
    strictness: Literal["strict", "normal", "lenient"] = "normal",
    repair: bool = False,
    explain: bool = True,
) -> ValidationResult:
    """Validate a JSON payload against a JSON Schema.

    Returns whether the payload is valid, a list of structured validation
    errors, a human-readable summary, and -- when repair=True and the payload
    is invalid -- a suggested corrected payload.

    Args:
        json_schema: A valid JSON Schema object (Draft 2020-12 or Draft-07).
        payload: The JSON value to validate (object, array, string, number,
                 boolean, or null).
        strictness: Controls repair aggressiveness.
                    "strict"  -- only fill fields that have explicit defaults.
                    "normal"  -- fill missing required fields with type defaults.
                    "lenient" -- same as normal (future: may coerce types).
        repair: When True and the payload is invalid, attempt to produce a
                suggested_payload that satisfies the schema.
        explain: When True, include a human-readable explanation in summary.

    Returns:
        valid (bool), errors (list), summary (str),
        suggested_payload (any|null), confidence (float), meta (dict).
    """
    from jsonschema import exceptions as js_exceptions

    try:
        errors = validate_payload(json_schema, payload)
    except js_exceptions.SchemaError as exc:
        raise ValueError(
            f"INVALID_JSON_SCHEMA: {exc.message} "
            f"(path: {list(exc.absolute_path)}, schema_path: {list(exc.absolute_schema_path)})"
        ) from exc

    valid = len(errors) == 0
    suggested_payload = None

    if repair and not valid:
        strictness_enum = Strictness(strictness)
        suggested_payload = suggest_repair(json_schema, payload, errors, strictness_enum)

    confidence = 1.0 if valid else 0.9
    if suggested_payload is not None:
        confidence = 0.75

    return ValidationResult(
        valid=valid,
        errors=[e.model_dump() for e in errors],
        summary=summarize(valid, errors, explain),
        suggested_payload=suggested_payload,
        confidence=confidence,
        meta=ValidationMeta(
            strictness=strictness,
            repair_attempted=repair,
            engine="jsonschema",
            schema_draft="auto",
        ),
    )


@mcp.tool(annotations=_READONLY_ANNOTATIONS)
def validate_schema_trial(
    json_schema: Dict[str, Any],
    payload: _JSON,
    explain: bool = True,
) -> ValidationResult:
    """Validate a JSON payload against a JSON Schema (free trial, no repair).

    Identical to validate_schema but repair suggestions are always disabled.
    Use this for lightweight checks where a corrected payload is not needed.

    Args:
        json_schema: A valid JSON Schema object (Draft 2020-12 or Draft-07).
        payload: The JSON value to validate.
        explain: When True, include a human-readable explanation in summary.

    Returns:
        valid (bool), errors (list), summary (str),
        suggested_payload (null), confidence (float), meta (dict).
    """
    from jsonschema import exceptions as js_exceptions

    try:
        errors = validate_payload(json_schema, payload)
    except js_exceptions.SchemaError as exc:
        raise ValueError(
            f"INVALID_JSON_SCHEMA: {exc.message} "
            f"(path: {list(exc.absolute_path)}, schema_path: {list(exc.absolute_schema_path)})"
        ) from exc

    valid = len(errors) == 0
    confidence = 1.0 if valid else 0.9

    return ValidationResult(
        valid=valid,
        errors=[e.model_dump() for e in errors],
        summary=summarize(valid, errors, explain),
        suggested_payload=None,
        confidence=confidence,
        meta=ValidationMeta(
            strictness="normal",
            repair_attempted=False,
            engine="jsonschema",
            schema_draft="auto",
        ),
    )
