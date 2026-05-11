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
            "description": "SchemaCheck Agent JSON Schema validation request",
        },
        "accepts": [
            {
                "scheme": settings.x402_scheme,
                "network": settings.x402_network,
                "asset": settings.x402_asset,
                "amount": settings.x402_amount,
                "payTo": settings.x402_pay_to,
                "maxTimeoutSeconds": settings.x402_max_timeout_seconds,
                "extra": {},
            }
        ],
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
        from x402.http import FacilitatorConfig, HTTPFacilitatorClient
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
        facilitator = HTTPFacilitatorClient(FacilitatorConfig(url=settings.x402_facilitator_url))
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
        )

        payload = decode_payment_signature_header(payment_payload)
        verify_result = resource_server.verify_payment(payload, requirements)
        if not getattr(verify_result, "is_valid", False) and not getattr(verify_result, "isValid", False):
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={"code": "X402_PAYMENT_INVALID", "message": "x402 payment verification failed."},
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
    x_payment: str | None = Header(default=None, alias=X_PAYMENT_HEADER),
) -> None:
    """Payment gate for disabled, placeholder, and guarded x402 modes."""
    settings = get_settings()

    if settings.payment_mode == "disabled":
        return

    if settings.payment_mode == "placeholder":
        if x_payment_token != settings.placeholder_payment_token:
            raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=PAYMENT_REQUIRED_DETAIL)
        return

    if settings.payment_mode == "x402":
        if not x_payment:
            _raise_x402_payment_required(settings)
        verify_x402_payment(x_payment, settings)
        return

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={"code": "PAYMENT_GATE_MISCONFIGURED", "message": f"Unsupported payment mode: {settings.payment_mode}"},
    )
