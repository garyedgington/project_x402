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
    x402_asset: str          # USDC contract address on the target network
    x402_amount: str         # Payment amount in atomic units (USDC has 6 decimals)
    x402_max_timeout_seconds: int
    x402_facilitator_url: str
    x402_real_verification_enabled: bool


def get_settings() -> Settings:
    return Settings(
        app_version=os.getenv("SCHEMACHECK_APP_VERSION", "0.3.0"),
        payment_mode=os.getenv("SCHEMACHECK_PAYMENT_MODE", "disabled").lower(),
        placeholder_payment_token=os.getenv("SCHEMACHECK_PLACEHOLDER_PAYMENT_TOKEN", "test-payment-token"),
        log_requests=_as_bool(os.getenv("SCHEMACHECK_LOG_REQUESTS"), True),
        x402_pay_to=os.getenv("SCHEMACHECK_X402_PAY_TO", "0x8fC4006534801c17A3368075A1Fb3b3C511EdB1F"),
        x402_network=os.getenv("SCHEMACHECK_X402_NETWORK", "eip155:8453"),
        x402_scheme=os.getenv("SCHEMACHECK_X402_SCHEME", "exact"),
        # USDC on Base mainnet: 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913
        # $0.005 = 5000 atomic units (6 decimals)
        x402_asset=os.getenv("SCHEMACHECK_X402_ASSET", "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"),
        x402_amount=os.getenv("SCHEMACHECK_X402_AMOUNT", "5000"),
        x402_max_timeout_seconds=int(os.getenv("SCHEMACHECK_X402_MAX_TIMEOUT_SECONDS", "300")),
        x402_facilitator_url=os.getenv("SCHEMACHECK_X402_FACILITATOR_URL", "https://api.cdp.coinbase.com/platform/v2/x402"),
        x402_real_verification_enabled=_as_bool(os.getenv("SCHEMACHECK_X402_REAL_VERIFICATION_ENABLED"), False),
    )
