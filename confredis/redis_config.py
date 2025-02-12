import redis.asyncio as aioredis


class RedisConfig:

    REDIS_URL = "redis://localhost"

    @staticmethod
    async def create_redis():
        return await aioredis.from_url(RedisConfig.REDIS_URL)


__all__ = ["RedisConfig"]
