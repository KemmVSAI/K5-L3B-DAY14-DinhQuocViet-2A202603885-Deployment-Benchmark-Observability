"""Redis-backed sliding-window rate limiter."""
import time
import uuid
import redis
from fastapi import HTTPException
from .config import settings
from .redis_client import r

def check_rate_limit(key: str) -> None:
    now = time.time()
    redis_key = f"agent:rate:{key}"
    try:
        pipe = r.pipeline(transaction=True)
        pipe.zremrangebyscore(redis_key, 0, now - 60)
        pipe.zcard(redis_key)
        count = pipe.execute()[1]
        if count >= settings.rate_limit_per_minute:
            oldest = r.zrange(redis_key, 0, 0, withscores=True)
            retry_after = max(1, int(oldest[0][1] + 60 - now) + 1) if oldest else 60
            raise HTTPException(status_code=429, detail="Rate limit exceeded",
                                headers={"Retry-After": str(retry_after)})
        r.zadd(redis_key, {f"{now:.6f}:{uuid.uuid4().hex}": now})
        r.expire(redis_key, 60)
    except HTTPException:
        raise
    except redis.RedisError as exc:
        raise HTTPException(status_code=503, detail="Rate limiter unavailable") from exc

