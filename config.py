"""
App configuration loader with dotenv support.

Usage:
    from config import config
    if config.USE_MOCK_AZURE: ...

Best practice:
    - Local dev: use a .env file (not committed)
    - Production: use environment variables provided by the platform (App Settings)
      and store secrets in Azure Key Vault; do not rely on .env in production.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

try:
    # Load .env if present for local development
    from dotenv import load_dotenv
    load_dotenv(override=False)
except Exception:
    # dotenv is optional at runtime
    pass


def _get_bool(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return str(val).strip().lower() in {"1", "true", "yes", "y", "on"}


def _get_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except Exception:
        return default


@dataclass(frozen=True)
class AppConfig:
    ENV: str = "development"  # development | staging | production
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Azure / Backend
    USE_MOCK_AZURE: bool = True
    AZURE_FUNCTION_URL: Optional[str] = None
    AZURE_STORAGE_ACCOUNT: Optional[str] = None

    # App
    APP_PORT: int = 8501

    @staticmethod
    def from_env() -> "AppConfig":
        env = os.getenv("ENV", os.getenv("ENVIRONMENT", "development")).lower()
        debug = _get_bool("DEBUG", env != "production")
        log_level = os.getenv("LOG_LEVEL", "DEBUG" if debug else "INFO").upper()

        use_mock = _get_bool("USE_MOCK_AZURE", True)
        function_url = os.getenv("AZURE_FUNCTION_URL")
        storage_account = os.getenv("AZURE_STORAGE_ACCOUNT")

        app_port = _get_int("APP_PORT", 8501)

        return AppConfig(
            ENV=env,
            DEBUG=debug,
            LOG_LEVEL=log_level,
            USE_MOCK_AZURE=use_mock,
            AZURE_FUNCTION_URL=function_url,
            AZURE_STORAGE_ACCOUNT=storage_account,
            APP_PORT=app_port,
        )


# Singleton config instance
config = AppConfig.from_env()
