from __future__ import annotations

import base64
import json
from typing import Any

from fastapi import Header, HTTPException, status

from app.config import Settings, get_settings


X_PAYMENT_HEADER = "X-PAYMENT"
PAYMENT_REQUIRED_HEADER = "PAYMENT-REQUIRED"
PAYMENT_RESPONSE_HEADER = "PAYMENT-RESPONSE"
PAYMENT_SIGNATURE_HEADER = "PAYMENT-SIGNATURE"

PAYMENT_REQUIRED_DETAIL = {
    "code": "PAYMENT_REQUIRED",
    "message": "Payment is required to access this endpoint.",
    "payment_protocol": "x402-placeholder",
    "payment_hint": "Send X-Payment-Token: test-payment-token while placeholder mode is enabled.",
}


def _base64_encode(data: str) -> str:
    return base64.b64encode(data.encode("utf-8")).decode("utf-8")


def build_x402_payment_required(settings: Settings, resource_url: str) -> dict[str, Any]:
    """Build a v2 PaymentRequired response body.

    Matches the x402 SDK v2 PaymentRequired schema:
    {
        x402Version: 2,
        resource: { url, description },
        accepts: [ PaymentRequirements ]
    }
    """
    if not settings.x402_pay_to:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "X402_PAY_TO_MISSING", "message": "SCHEMACHECK_X402_PAY_TO is required for x402 mode."},
        )

    return {
        "x402Version": 2,
        "resource": {
            "url": resource_url,
            "description": "Validate a JSON payload against a JSON Schema. Returns structured errors, error codes, JSONPath locations, and a plain-English summary.",
            "mimeType": "application/json",
            "serviceName": "SchemaCheck Agent",
            "tags": ["json", "validation", "schema", "agent", "api"],
        },
        "accepts": [
            {
                "scheme": settings.x402_scheme,
                "network": settings.x402_network,
                "asset": settings.x402_asset,
                "amount": settings.x402_amount,
                "payTo": settings.x402_pay_to,
                "maxTimeoutSeconds": settings.x402_max_timeout_seconds,
                # EIP-712 domain for USDC on Base mainnet — required for client signing
                "extra": {
                    "name": "USD Coin",
                    "version": "2",
                },
            }
        ],
        "extensions": {
            "bazaar": {
                "discoverable": True,
                "inputSchema": {
                    "body": {
                        "json_schema": {
                            "type": "object",
                            "description": "JSON Schema document to validate the payload against",
                            "required": True,
                        },
                        "payload": {
                            "type": "any",
                            "description": "The JSON value to validate",
                            "required": True,
                        },
                        "strictness": {
                            "type": "string",
                            "description": "Validation strictness: strict | normal | lenient. Default: normal",
                            "required": False,
                        },
                        "repair": {
                            "type": "boolean",
                            "description": "If true, return a suggested corrected payload when possible. Default: false",
                            "required": False,
                        },
                        "explain": {
                            "type": "boolean",
                            "description": "If true, include a plain-English summary. Default: true",
                            "required": False,
                        },
                    }
                },
                "outputSchema": {
                    "type": "object",
                    "properties": {
                        "valid": {"type": "boolean", "description": "True if the payload passes schema validation"},
                        "errors": {"type": "array", "description": "List of structured validation errors"},
                        "summary": {"type": "string", "description": "Plain-English validation summary"},
                        "suggested_payload": {"type": "any", "description": "Suggested corrected payload (when repair=true)"},
                        "confidence": {"type": "number", "description": "Confidence score 0-1"},
                    },
                },
            }
        },
    }


def _raise_x402_payment_required(settings: Settings) -> None:
    resource_url = "https://projectx402-production.up.railway.app/v1/schema-check"
    payment_required = build_x402_payment_required(settings, resource_url)
    header_value = _base64_encode(json.dumps(payment_required, separators=(",", ":")))
    raise HTTPException(
        status_code=status.HTTP_402_PAYMENT_REQUIRED,
        detail=payment_required,
        headers={PAYMENT_REQUIRED_HEADER: header_value},
    )


def _build_facilitator_config(settings: Settings) -> Any:
    """Build a FacilitatorConfig, adding CDP authentication when the facilitator is CDP-hosted.

    The hosted CDP facilitator (api.cdp.coinbase.com) requires per-request JWT auth
    generated from CDP API key + secret. The open testnet facilitator (x402.org) does not.
    """
    from x402.http import FacilitatorConfig, CreateHeadersAuthProvider

    url = settings.x402_facilitator_url
    if "cdp.coinbase.com" not in url:
        return FacilitatorConfig(url=url)

    import os
    api_key_id = os.getenv("CDP_API_KEY_ID")
    api_key_secret = os.getenv("CDP_API_KEY_SECRET")
    if not api_key_id or not api_key_secret:
        raise RuntimeError(
            "CDP facilitator requires CDP_API_KEY_ID and CDP_API_KEY_SECRET environment variables."
        )

    from urllib.parse import urlparse
    from cdp.auth import get_auth_headers, GetAuthHeadersOptions

    parsed = urlparse(url)
    host = parsed.netloc
    base_path = parsed.path.rstrip("/")

    def _hdrs(method: str, path: str) -> dict[str, str]:
        return get_auth_headers(GetAuthHeadersOptions(
            api_key_id=api_key_id,
            api_key_secret=api_key_secret,
            request_method=method,
            request_host=host,
            request_path=path,
        ))

    def create_headers() -> dict[str, dict[str, str]]:
        return {
            "verify":    _hdrs("POST", f"{base_path}/verify"),
            "settle":    _hdrs("POST", f"{base_path}/settle"),
            "supported": _hdrs("GET",  f"{base_path}/supported"),
        }

    return FacilitatorConfig(url=url, auth_provider=CreateHeadersAuthProvider(create_headers))


def verify_x402_payment(payment_payload: str, settings: Settings) -> None:
    """Verify x402 payment through the SDK when explicitly enabled."""
    if not settings.x402_real_verification_enabled:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail={
                "code": "X402_REAL_VERIFICATION_DISABLED",
                "message": "x402 payment payload was received, but live verification is disabled.",
            },
        )

    try:
        from x402.http import FacilitatorConfig, HTTPFacilitatorClientSync
        from x402.mechanisms.evm.exact import ExactEvmServerScheme
        from x402.http.utils import decode_payment_signature_header
        from x402.server import x402ResourceServerSync
        from x402.schemas import PaymentRequirements
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "X402_SDK_UNAVAILABLE", "message": f"Unable to import x402 SDK: {exc}"},
        ) from exc

    try:
        facilitator = HTTPFacilitatorClientSync(_build_facilitator_config(settings))
        resource_server = x402ResourceServerSync(facilitator)
        resource_server.register(settings.x402_network, ExactEvmServerScheme())
        resource_server.initialize()

        requirements = PaymentRequirements(
            scheme=settings.x402_scheme,
            network=settings.x402_network,
            asset=settings.x402_asset,
            amount=settings.x402_amount,
            pay_to=settings.x402_pay_to,
            max_timeout_seconds=settings.x402_max_timeout_seconds,
            extra={"name": "USD Coin", "version": "2"},
        )

        payload = decode_payment_signature_header(payment_payload)
        verify_result = resource_server.verify_payment(payload, requirements)
        if not getattr(verify_result, "is_valid", False):
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "code": "X402_PAYMENT_INVALID",
                    "message": "x402 payment verification failed.",
                    "reason": getattr(verify_result, "invalid_reason", None),
                    "detail": getattr(verify_result, "invalid_message", None),
                },
            )

        resource_server.settle_payment(payload, requirements)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={"code": "X402_PAYMENT_FAILED", "message": str(exc)},
        ) from exc


def enforce_payment(
    x_payment_token: str | None = Header(default=None, alias="X-Payment-Token"),
    x_payment: str | None = Header(default=None, alias="X-PAYMENT"),
    payment_signature: str | None = Header(default=None, alias="PAYMENT-SIGNATURE"),
) -> None:
    """Payment gate for disabled, placeholder, and guarded x402 modes.

    x402 v2 clients send PAYMENT-SIGNATURE (not X-PAYMENT).
    x402 v1 clients send X-PAYMENT.
    Both are accepted.
    """
    settings = get_settings()

    if settings.payment_mode == "disabled":
        return

    if settings.payment_mode == "placeholder":
        if x_payment_token != settings.placeholder_payment_token:
            raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=PAYMENT_REQUIRED_DETAIL)
        return

    if settings.payment_mode == "x402":
        # Accept either v2 PAYMENT-SIGNATURE or v1 X-PAYMENT
        payment_payload = payment_signature or x_payment
        if not payment_payload:
            _raise_x402_payment_required(settings)
        verify_x402_payment(payment_payload, settings)
        return

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={"code": "PAYMENT_GATE_MISCONFIGURED", "message": f"Unsupported payment mode: {settings.payment_mode}"},
    )
