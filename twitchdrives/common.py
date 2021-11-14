import os

import aioredis
import redis

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost")

def get_redis() -> redis.Redis():
    return redis.from_url(
        REDIS_URL,
        decode_responses=True
    )


def get_aioredis():
    return aioredis.from_url(REDIS_URL, decode_responses=True)
