from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    app_version: str = "0.2.0"
    payment_mode: str = os.getenv("SCHEMACHECK_PAYMENT_MODE", "disabled").lower()
    placeholder_payment_token: str = os.getenv("SCHEMACHECK_PLACEHOLDER_PAYMENT_TOKEN", "test-payment-token")
    log_requests: bool = os.getenv("SCHEMACHECK_LOG_REQUESTS", "true").lower() not in {"0", "false", "no"}


def get_settings() -> Settings:
    return Settings()
