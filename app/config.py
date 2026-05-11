from __future__ import annotations

from dataclasses import dataclass
import os


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.lower() not in {"0", "false", "no", "off", ""}


@dataclass(frozen=True)
class Settings:
    app_version: str
    payment_mode: str
    placeholder_payment_token: str
    log_requests: bool
    x402_pay_to: str
    x402_network: str
    x402_scheme: str
    x402_price: str
    x402_facilitator_url: str
    x402_real_verification_enabled: bool


def get_settings() -> Settings:
    return Settings(
        app_version=os.getenv("SCHEMACHECK_APP_VERSION", "0.3.0"),
        payment_mode=os.getenv("SCHEMACHECK_PAYMENT_MODE", "disabled").lower(),
        placeholder_payment_token=os.getenv("SCHEMACHECK_PLACEHOLDER_PAYMENT_TOKEN", "test-payment-token"),
        log_requests=_as_bool(os.getenv("SCHEMACHECK_LOG_REQUESTS"), True),
        x402_pay_to=os.getenv("SCHEMACHECK_X402_PAY_TO", "0x8fC4006534801c17A3368075A1Fb3b3C511EdB1F"),
        x402_network=os.getenv("SCHEMACHECK_X402_NETWORK", "eip155:84532"),
        x402_scheme=os.getenv("SCHEMACHECK_X402_SCHEME", "exact"),
        x402_price=os.getenv("SCHEMACHECK_X402_PRICE", "$0.005"),
        x402_facilitator_url=os.getenv("SCHEMACHECK_X402_FACILITATOR_URL", "https://x402.org/facilitator"),
        x402_real_verification_enabled=_as_bool(os.getenv("SCHEMACHECK_X402_REAL_VERIFICATION_ENABLED"), False),
    )
