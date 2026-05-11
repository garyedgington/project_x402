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


def _payment_required_header_value(requirements: dict[str, Any]) -> str:
    """Encode payment requirements into a compact HTTP-header-safe value."""
    raw = json.dumps(requirements, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii")


def build_x402_payment_requirements(settings: Settings | None = None) -> dict[str, Any]:
    """Build x402-shaped payment requirements for this protected resource.

    This intentionally returns a plain dict so local tests do not require a live
    facilitator. Real SDK verification is handled separately and remains guarded.
    """
    settings = settings or get_settings()
    if not settings.x402_pay_to:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "X402_PAY_TO_MISSING", "message": "SCHEMACHECK_X402_PAY_TO is required for x402 mode."},
        )

    return {
        "x402Version": 2,
        "scheme": settings.x402_scheme,
        "network": settings.x402_network,
        "payTo": settings.x402_pay_to,
        "price": settings.x402_price,
        "resource": "/v1/schema-check",
        "description": "SchemaCheck Agent JSON Schema validation request",
        "facilitator": settings.x402_facilitator_url,
    }


def _raise_x402_payment_required(settings: Settings) -> None:
    requirements = build_x402_payment_requirements(settings)
    raise HTTPException(
        status_code=status.HTTP_402_PAYMENT_REQUIRED,
        detail={
            "code": "PAYMENT_REQUIRED",
            "message": "x402 payment is required to access this endpoint.",
            "payment_protocol": "x402",
            "payment_requirements": requirements,
            "payment_header": X_PAYMENT_HEADER,
        },
        headers={PAYMENT_REQUIRED_HEADER: _payment_required_header_value(requirements)},
    )


def verify_x402_payment(payment_payload: str, settings: Settings) -> None:
    """Verify x402 payment through the SDK when explicitly enabled.

    Phase 3.6 wires the real SDK flow behind a guard. Until live payment tests are
    intentionally enabled, requests with X-PAYMENT return 501 instead of silently
    pretending to settle funds.
    """
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
        from x402.schemas import parse_payment_payload
        from x402.server import ResourceConfig, x402ResourceServerSync
    except Exception as exc:  # pragma: no cover - depends on optional SDK install
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "X402_SDK_UNAVAILABLE", "message": f"Unable to import x402 SDK: {exc}"},
        ) from exc

    try:
        facilitator = HTTPFacilitatorClient(FacilitatorConfig(url=settings.x402_facilitator_url))
        resource_server = x402ResourceServerSync(facilitator)
        resource_server.register(settings.x402_network, ExactEvmServerScheme())
        resource_server.initialize()

        config = ResourceConfig(
            scheme=settings.x402_scheme,
            network=settings.x402_network,
            payTo=settings.x402_pay_to,
            price=settings.x402_price,
        )
        requirements = resource_server.build_payment_requirements(config)
        if not requirements:
            raise RuntimeError("x402 SDK returned no payment requirements")

        payload = parse_payment_payload(payment_payload.encode("utf-8"))
        verify_result = resource_server.verify_payment(payload, requirements[0])
        if not getattr(verify_result, "isValid", False) and not getattr(verify_result, "valid", False):
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={"code": "X402_PAYMENT_INVALID", "message": "x402 payment verification failed."},
            )

        resource_server.settle_payment(payload, requirements[0])
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - live SDK/facilitator dependent
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
