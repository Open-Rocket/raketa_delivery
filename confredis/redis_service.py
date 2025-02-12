import redis.asyncio as aioredis
from .redis_config import RedisConfig


class RedisService:
    """Простой сервис для работы с пользователями в Redis"""

    def __init__(self, redis: aioredis.Redis):
        self.redis = redis

    async def set_user_info(self, user_id: int, name: str, phone: str) -> bool:
        """Сохраняет имя и телефон пользователя в Redis"""

        await self.redis.hset(f"user:{user_id}", "name", name)
        await self.redis.hset(f"user:{user_id}", "phone", phone)
        return True

    async def get_user_info(self, user_id: int) -> tuple[str | None, str | None]:
        """Получает имя и телефон пользователя из Redis"""

        user_data = await self.redis.hgetall(f"user:{user_id}")
        name = user_data.get(b"name", None)
        phone = user_data.get(b"phone", None)
        return (
            name.decode("utf-8") if name else None,
            phone.decode("utf-8") if phone else None,
        )


async def create_redis_service() -> RedisService:
    """Асинхронная фабрика для создания нового экземпляра RedisService"""

    redis_event = await RedisConfig.create_redis()
    return RedisService(redis_event)


__all__ = ["create_redis_service", "RedisService"]
