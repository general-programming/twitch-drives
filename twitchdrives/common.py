from contextlib import asynccontextmanager
import os
from typing import AsyncGenerator

import aioredis
import redis

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost")


def get_redis() -> redis.Redis():
    return redis.from_url(REDIS_URL, decode_responses=True)


def get_aioredis():
    return aioredis.from_url(REDIS_URL, decode_responses=True)


@asynccontextmanager
async def ctx_aioredis() -> AsyncGenerator[aioredis.Redis, None]:
    try:
        redis = await get_aioredis()
        yield redis
    finally:
        await redis.close()
