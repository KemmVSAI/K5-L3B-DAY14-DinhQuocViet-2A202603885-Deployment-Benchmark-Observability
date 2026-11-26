"""Lazy Redis client shared by rate limiting and cost accounting."""
import redis
from .config import settings

r = redis.Redis.from_url(settings.redis_url, decode_responses=True)

def redis_healthy() -> bool:
    try:
        return bool(r.ping())
    except redis.RedisError:
        return False

