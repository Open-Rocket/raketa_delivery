import asyncio
import redis.asyncio as aioredis
from .redis_config import RedisConfig
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram import Bot
from typing import Optional


class RedisService:
    """Сервис для работы с пользователями и состояниями FSM в Redis"""

    def __init__(self, redis: aioredis.Redis):
        self.redis = redis
        self.fsm_storage = RedisStorage(self.redis)

    async def set_user_info(
        self,
        user_id: Optional[int] = None,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        city: Optional[str] = None,
        is_reg: bool = False,
    ) -> bool:
        """Сохраняет имя и телефон пользователя в Redis"""
        await self.redis.hset(
            f"user:{user_id}",
            mapping={
                "name": name,
                "phone": phone,
                "city": city,
                "is_reg": is_reg,
            },
        )
        return True

    async def get_user_info(self, user_id: int) -> tuple[str | None, str | None]:
        """Получает имя и телефон пользователя из Redis"""
        user_data = await self.redis.hgetall(f"user:{user_id}")
        if not user_data:
            return None * 5
        return (
            user_data.get(b"name", b"").decode("utf-8"),
            user_data.get(b"phone", b"").decode("utf-8"),
            user_data.get(b"city", b"").decode("utf-8"),
            user_data.get(b"is_reg", b""),
        )

    async def set_state(self, bot: Bot, user_id: int, state: State) -> None:
        """Сохраняет состояние FSM пользователя в Redis"""
        await self.fsm_storage.set_state(bot=bot, key=str(user_id), state=state.state)

    async def get_state(self, bot: Bot, user_id: int) -> str | None:
        """Получает текущее состояние FSM пользователя из Redis"""
        return await self.fsm_storage.get_state(bot=bot, key=str(user_id))

    async def reset_state(self, user_id: int) -> None:
        """Удаляет текущее состояние FSM пользователя"""
        await self.fsm_storage.set_state(bot=None, key=str(user_id), state=None)

    async def restore_state(self, bot: Bot, user_id: int, state: FSMContext) -> None:
        """Восстанавливает состояние FSM из Redis в FSMContext"""
        saved_state = await self.get_state(bot, user_id)
        if saved_state:
            await state.set_state(saved_state)


async def create_redis_service() -> RedisService:
    """Асинхронная фабрика для создания экземпляра RedisService"""
    redis_instance = await RedisConfig.create_redis()
    return RedisService(redis_instance)


rediska: RedisService = asyncio.run(create_redis_service())

__all__ = ["rediska", "create_redis_service", "RedisService"]
