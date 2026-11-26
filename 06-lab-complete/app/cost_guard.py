"""Redis-backed daily cost guard."""
from datetime import datetime, timezone
import redis
from fastapi import HTTPException
from .config import settings
from .redis_client import r

PRICE_INPUT_PER_1K = 0.00015
PRICE_OUTPUT_PER_1K = 0.0006

def _key() -> str:
    return f"agent:cost:{datetime.now(timezone.utc).strftime('%Y-%m-%d')}"

def check_budget() -> None:
    try:
        used = float(r.get(_key()) or 0.0)
    except (redis.RedisError, ValueError) as exc:
        raise HTTPException(status_code=503, detail="Cost guard unavailable") from exc
    if used >= settings.daily_budget_usd:
        raise HTTPException(status_code=402, detail="Daily budget exceeded")

def record_cost(input_tokens: int, output_tokens: int) -> float:
    cost = (input_tokens / 1000) * PRICE_INPUT_PER_1K + (output_tokens / 1000) * PRICE_OUTPUT_PER_1K
    try:
        pipe = r.pipeline(transaction=True)
        pipe.incrbyfloat(_key(), cost)
        pipe.expire(_key(), 172800)
        pipe.execute()
    except redis.RedisError as exc:
        raise HTTPException(status_code=503, detail="Cost guard unavailable") from exc
    return cost

