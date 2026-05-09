from __future__ import annotations

from fastapi import Header, HTTPException, status

from app.config import get_settings


PAYMENT_REQUIRED_DETAIL = {
    "code": "PAYMENT_REQUIRED",
    "message": "Payment is required to access this endpoint.",
    "payment_protocol": "x402-placeholder",
    "payment_hint": "Send X-Payment-Token: test-payment-token while placeholder mode is enabled.",
}


def enforce_payment(x_payment_token: str | None = Header(default=None, alias="X-Payment-Token")) -> None:
    """Payment gate placeholder.

    Default mode is disabled. In placeholder mode, the endpoint requires a static test token.
    Real x402 verification should replace this dependency in Phase 3.
    """
    settings = get_settings()
    if settings.payment_mode == "disabled":
        return
    if settings.payment_mode != "placeholder":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "PAYMENT_GATE_MISCONFIGURED", "message": f"Unsupported payment mode: {settings.payment_mode}"},
        )
    if x_payment_token != settings.placeholder_payment_token:
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=PAYMENT_REQUIRED_DETAIL)
