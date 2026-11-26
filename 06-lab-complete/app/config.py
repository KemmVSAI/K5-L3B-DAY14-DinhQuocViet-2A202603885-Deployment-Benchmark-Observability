"""Environment-based application configuration."""
import os
from dataclasses import dataclass

def _int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default

def _float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default

@dataclass(frozen=True)
class Settings:
    port: int = _int("PORT", 8000)
    environment: str = os.getenv("ENVIRONMENT", "development")
    agent_api_key: str = os.getenv("AGENT_API_KEY", "")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    rate_limit_per_minute: int = _int("RATE_LIMIT_PER_MINUTE", 10)
    daily_budget_usd: float = _float("DAILY_BUDGET_USD", _float("MONTHLY_BUDGET_USD", 1.0))

settings = Settings()

