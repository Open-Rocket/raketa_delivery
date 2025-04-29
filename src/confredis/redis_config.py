import os
from dotenv import load_dotenv
import redis.asyncio as aioredis

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST")


class RedisConfig:

    REDIS_URL = f"redis://{REDIS_HOST}"

    @staticmethod
    async def create_redis() -> aioredis.Redis:
        """Создание подключения к Redis"""

        return await aioredis.from_url(RedisConfig.REDIS_URL)


__all__ = ["RedisConfig"]
