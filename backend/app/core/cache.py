import redis
import json
from typing import Optional
from app.core.config import REDIS_HOST, REDIS_PORT, REDIS_DB

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

def get_cached_query(query: str) -> Optional[str]:
    try:
        return redis_client.get(f"cache:query:{query}")
    except redis.RedisError:
        return None

def set_cached_query(query: str, answer: str, ttl: int = 3600) -> None:
    try:
        redis_client.setex(f"cache:query:{query}", ttl, answer)
    except redis.RedisError:
        pass

def clear_cache() -> None:
    try:
        redis_client.flushdb()
    except redis.RedisError:
        pass
