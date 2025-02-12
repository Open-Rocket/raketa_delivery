import redis.asyncio as aioredis
from .redis_config import RedisConfig
from aiogram.fsm.storage.redis import RedisStorage


class RedisService:
    """Сервис для работы с пользователями и состояниями FSM в Redis"""

    def __init__(self, redis: aioredis.Redis):
        self.redis = redis
        self.fsm_storage = RedisStorage(self.redis)

    async def set_user_info(self, user_id: int, name: str, phone: str) -> bool:
        """Сохраняет имя и телефон пользователя в Redis"""
        await self.redis.hset(f"user:{user_id}", mapping={"name": name, "phone": phone})
        return True

    async def get_user_info(self, user_id: int) -> tuple[str | None, str | None]:
        """Получает имя и телефон пользователя из Redis"""
        user_data = await self.redis.hgetall(f"user:{user_id}")
        if not user_data:
            return None, None
        return (
            user_data.get(b"name", b"").decode("utf-8") or None,
            user_data.get(b"phone", b"").decode("utf-8") or None,
        )

    async def set_state(self, user_id: int, state: str) -> None:
        """Сохраняет состояние FSM пользователя"""
        await self.fsm_storage.set_state(bot=None, key=str(user_id), state=state)

    async def get_state(self, user_id: int) -> str | None:
        """Получает текущее состояние FSM пользователя"""
        return await self.fsm_storage.get_state(bot=None, key=str(user_id))

    async def reset_state(self, user_id: int) -> None:
        """Удаляет текущее состояние FSM пользователя"""
        await self.fsm_storage.set_state(bot=None, key=str(user_id), state=None)


async def create_redis_service() -> RedisService:
    """Асинхронная фабрика для создания экземпляра RedisService"""
    redis_instance = await RedisConfig.create_redis()
    return RedisService(redis_instance)


__all__ = ["create_redis_service", "RedisService"]
