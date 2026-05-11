from __future__ import annotations

from copy import deepcopy
from typing import Any

from jsonschema import Draft202012Validator, exceptions

from app.models import Strictness, ValidationErrorDetail


_ERROR_CODE_MAP = {
    "required": "REQUIRED_FIELD_MISSING",
    "type": "TYPE_MISMATCH",
    "enum": "ENUM_VIOLATION",
    "additionalProperties": "ADDITIONAL_PROPERTY",
    "format": "FORMAT_VIOLATION",
    "minimum": "MINIMUM_VIOLATION",
    "maximum": "MAXIMUM_VIOLATION",
    "minLength": "MIN_LENGTH_VIOLATION",
    "maxLength": "MAX_LENGTH_VIOLATION",
    "pattern": "PATTERN_VIOLATION",
}


def _json_path(parts: list[Any]) -> str:
    if not parts:
        return "$"
    path = "$"
    for part in parts:
        if isinstance(part, int):
            path += f"[{part}]"
        else:
            path += f".{part}"
    return path


def _schema_path(parts: list[Any]) -> str:
    if not parts:
        return "$"
    return "$" + "".join(f"/{part}" for part in parts)


def _actual_value(payload: Any, path: list[Any]) -> Any:
    current = payload
    try:
        for part in path:
            current = current[part]
        return current
    except Exception:
        return None


def _expected_from_error(error: exceptions.ValidationError) -> Any:
    if error.validator in {"type", "enum", "minimum", "maximum", "minLength", "maxLength", "pattern", "format"}:
        return error.validator_value
    if error.validator == "required":
        return error.message
    if error.validator == "additionalProperties":
        return "no additional properties"
    return error.validator_value


def normalize_error(error: exceptions.ValidationError, payload: Any) -> ValidationErrorDetail:
    path = list(error.absolute_path)
    return ValidationErrorDetail(
        code=_ERROR_CODE_MAP.get(error.validator, "SCHEMA_VALIDATION_ERROR"),
        message=error.message,
        path=_json_path(path),
        schema_path=_schema_path(list(error.absolute_schema_path)),
        expected=_expected_from_error(error),
        actual=_actual_value(payload, path),
    )


def validate_payload(json_schema: dict[str, Any], payload: Any) -> list[ValidationErrorDetail]:
    Draft202012Validator.check_schema(json_schema)
    validator = Draft202012Validator(json_schema)
    raw_errors = sorted(validator.iter_errors(payload), key=lambda e: list(e.absolute_path))
    return [normalize_error(error, payload) for error in raw_errors]


def _default_for_schema(schema: dict[str, Any]) -> Any:
    if "default" in schema:
        return deepcopy(schema["default"])
    schema_type = schema.get("type")
    if schema_type == "string":
        return ""
    if schema_type == "integer":
        return 0
    if schema_type == "number":
        return 0
    if schema_type == "boolean":
        return False
    if schema_type == "array":
        return []
    if schema_type == "object":
        return {}
    return None


def suggest_repair(json_schema: dict[str, Any], payload: Any, errors: list[ValidationErrorDetail], strictness: Strictness) -> Any | None:
    """Conservative deterministic repair.

    MVP only fills missing required top-level object fields when a default or safe type placeholder exists.
    It does not coerce types or guess semantic values.
    """
    if not isinstance(payload, dict) or not isinstance(json_schema, dict):
        return None
    if json_schema.get("type") != "object":
        return None

    required = json_schema.get("required", [])
    properties = json_schema.get("properties", {})
    if not isinstance(required, list) or not isinstance(properties, dict):
        return None

    repaired = deepcopy(payload)
    changed = False
    for field in required:
        if field not in repaired and field in properties:
            value = _default_for_schema(properties[field])
            if value is not None or strictness != Strictness.strict:
                repaired[field] = value
                changed = True

    return repaired if changed else None


def summarize(valid: bool, errors: list[ValidationErrorDetail], explain: bool) -> str:
    if valid:
        return "Payload is valid against the supplied JSON Schema."
    if not explain:
        return "Payload is invalid."
    count = len(errors)
    first = errors[0].message if errors else "Unknown validation error."
    return f"Payload is invalid with {count} validation error{'s' if count != 1 else ''}. First error: {first}"
