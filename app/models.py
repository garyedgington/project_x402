from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class Strictness(str, Enum):
    strict = "strict"
    normal = "normal"
    lenient = "lenient"


class SchemaCheckRequest(BaseModel):
    json_schema: dict[str, Any] = Field(..., description="JSON Schema used to validate payload")
    payload: Any = Field(..., description="JSON payload to validate")
    strictness: Strictness = Strictness.normal
    repair: bool = False
    explain: bool = True


class ValidationErrorDetail(BaseModel):
    code: str
    message: str
    path: str
    schema_path: str
    expected: Optional[Any] = None
    actual: Optional[Any] = None


class ResponseMeta(BaseModel):
    strictness: Strictness
    repair_attempted: bool
    engine: str = "jsonschema"
    schema_draft: str = "auto"


class SchemaCheckResponse(BaseModel):
    valid: bool
    errors: list[ValidationErrorDetail]
    summary: str
    suggested_payload: Optional[Any] = None
    confidence: float
    meta: ResponseMeta


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
