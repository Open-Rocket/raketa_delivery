import asyncio
import redis.asyncio as aioredis
from .redis_config import RedisConfig
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from typing import Optional


class RedisKey:
    DEFAULT_DESTINY = "default"

    def __init__(
        self,
        bot_id,
        user_id,
        thread_id=None,
        business_connection_id=None,
        destiny=DEFAULT_DESTINY,
    ):
        self.bot_id = bot_id
        self.user_id = user_id
        self.chat_id = f"{bot_id}{user_id}"
        self.thread_id = thread_id
        self.business_connection_id = business_connection_id
        self.destiny = destiny

    def __str__(self):
        return self.chat_id


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

    async def get_user_info(
        self, user_id: int
    ) -> tuple[str | None, str | None, str | None, bool | None]:
        """Получает имя и телефон пользователя из Redis"""
        user_data = await self.redis.hgetall(f"user:{user_id}")
        if not user_data:
            return None, None, None, None
        return (
            user_data.get(b"name", b"").decode("utf-8"),
            user_data.get(b"phone", b"").decode("utf-8"),
            user_data.get(b"city", b"").decode("utf-8"),
            bool(int(user_data.get(b"is_reg", b"0").decode("utf-8"))),
        )

    async def is_reg(self, user_id: int) -> bool:
        """Получает статус регистрации пользователя из Redis"""
        is_reg = await self.redis.hget(f"user:{user_id}", "is_reg")

        if is_reg is not None:
            return bool(int(is_reg.decode("utf-8")))
        else:
            return False

    async def set_state(self, bot_id: int, user_id: int, state: State) -> None:
        """Сохраняет состояние FSM пользователя в Redis"""
        key = RedisKey(bot_id, user_id)
        await self._reset_state(bot_id, user_id)
        await self.fsm_storage.set_state(key=key, state=state)

    async def get_state(self, bot_id: int, user_id: int) -> str | None:
        """Получает текущее состояние FSM пользователя из Redis"""
        key = RedisKey(bot_id, user_id)
        return await self.fsm_storage.get_state(key=key)

    async def _reset_state(self, bot_id: int, user_id: int) -> None:
        """Удаляет текущее состояние FSM пользователя"""
        key = RedisKey(bot_id, user_id)
        await self.fsm_storage.set_state(key=key, state=None)

    async def restore_state(self, bot_id: int, user_id: int, state: FSMContext) -> None:
        """Восстанавливает состояние FSM из Redis в FSMContext"""
        saved_state = await self.get_state(bot_id, user_id)
        if saved_state:
            await state.set_state(saved_state)


async def create_redis_service() -> RedisService:
    """Асинхронная фабрика для создания экземпляра RedisService"""
    redis_instance = await RedisConfig.create_redis()
    return RedisService(redis_instance)


async def main():

    rediska: RedisService = await create_redis_service()

    return rediska


rediska = asyncio.run(main())

__all__ = ["rediska", "create_redis_service", "RedisService"]
