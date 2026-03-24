import asyncpg
from redis.asyncio import Redis
from contextlib import asynccontextmanager
import os

_pg_pool: asyncpg.Pool | None = None
_redis: Redis | None = None


async def init_db():
    global _pg_pool, _redis
    _pg_pool = await asyncpg.create_pool(
        dsn=os.environ["DATABASE_URL"],
        min_size=2,
        max_size=10,
    )
    _redis = Redis.from_url(os.environ["REDIS_URL"], decode_responses=True)


async def close_db():
    if _pg_pool:
        await _pg_pool.close()
    if _redis:
        await _redis.aclose()


def get_pool() -> asyncpg.Pool:
    assert _pg_pool is not None, "Database pool not initialised"
    return _pg_pool


def get_redis() -> Redis:
    assert _redis is not None, "Redis not initialised"
    return _redis