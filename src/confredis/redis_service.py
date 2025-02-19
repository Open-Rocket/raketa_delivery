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

    async def set_user_name(self, bot_id: int, user_id: int, name: str) -> bool:
        """Сохраняет имя и телефон пользователя в Redis"""
        key = RedisKey(bot_id, user_id)
        await self.redis.hset(f"user:{key}", mapping={"name": name})
        return True

    async def set_user_phone(self, bot_id: int, user_id: int, phone: str) -> bool:
        """Сохраняет имя и телефон пользователя в Redis"""
        key = RedisKey(bot_id, user_id)
        await self.redis.hset(f"user:{key}", mapping={"phone": phone})
        return True

    async def set_user_city(self, bot_id: int, user_id: int, city: str) -> bool:
        """Сохраняет имя и телефон пользователя в Redis"""
        key = RedisKey(bot_id, user_id)
        await self.redis.hset(f"user:{key}", mapping={"city": city})
        return True

    async def set_user_tou(self, bot_id: int, user_id: int, tou: str) -> bool:
        """Сохраняет имя и телефон пользователя в Redis"""
        key = RedisKey(bot_id, user_id)
        await self.redis.hset(f"user:{key}", mapping={"tou": tou})
        return True

    async def set_read_info(self, bot_id: int, user_id: int, is_read: int) -> bool:
        """Сохраняет имя и телефон пользователя в Redis"""
        key = RedisKey(bot_id, user_id)
        await self.redis.hset(f"user:{key}", mapping={"read_info": is_read})
        return True

    async def get_user_name(self, bot_id: int, user_id: int) -> str | None:
        """Получает имя и телефон пользователя из Redis"""
        key = RedisKey(bot_id, user_id)
        user_data = await self.redis.hgetall(f"user:{key}")
        if not user_data:
            return None
        return (user_data.get(b"name", b"").decode("utf-8"),)

    async def get_user_phone(self, bot_id: int, user_id: int) -> str | None:
        """Получает имя и телефон пользователя из Redis"""
        key = RedisKey(bot_id, user_id)
        user_data = await self.redis.hgetall(f"user:{key}")
        if not user_data:
            return None
        return (user_data.get(b"phone", b"").decode("utf-8"),)

    async def get_user_city(self, bot_id: int, user_id: int) -> str | None:
        """Получает имя и телефон пользователя из Redis"""
        key = RedisKey(bot_id, user_id)
        user_data = await self.redis.hgetall(f"user:{key}")
        if not user_data:
            return None
        return (user_data.get(b"city", b"").decode("utf-8"),)

    async def get_user_tou(self, bot_id: int, user_id: int) -> str | None:
        """Получает имя и телефон пользователя из Redis"""
        key = RedisKey(bot_id, user_id)
        user_data = await self.redis.hgetall(f"user:{key}")
        if not user_data:
            return None
        return (user_data.get(b"tou", b"").decode("utf-8"),)

    async def get_user_info(self, bot_id: int, user_id: int) -> str | None:
        """Получает имя и телефон пользователя из Redis"""
        key = RedisKey(bot_id, user_id)
        user_data = await self.redis.hgetall(f"user:{key}")
        if not user_data:
            return (
                None,
                None,
                None,
                None,
            )
        return (
            user_data.get(b"name", b"").decode("utf-8"),
            user_data.get(b"phone", b"").decode("utf-8"),
            user_data.get(b"city", b"").decode("utf-8"),
            user_data.get(b"tou", b"").decode("utf-8"),
        )

    async def set_reg(self, bot_id: int, user_id: int, value: bool) -> bool:
        """Устанавливает статус регистрации пользователя в Redis"""
        key = RedisKey(bot_id, user_id)
        await self.redis.hset(f"user:{key}", "is_reg", int(value))
        return True

    async def set_read_info(self, bot_id: int, user_id: int, value: bool) -> bool:
        """Устанавливает статус ознакомления пользователя с оформлением заказа"""
        key = RedisKey(bot_id, user_id)
        await self.redis.hset(f"user:{key}", "read_info", int(value))
        return True

    async def is_reg(self, bot_id: int, user_id: int) -> bool:
        """Получает статус регистрации пользователя из Redis"""
        key = RedisKey(bot_id, user_id)
        is_reg = await self.redis.hget(f"user:{key}", "is_reg")

        if is_reg is not None:
            return bool(int(is_reg.decode("utf-8")))
        else:
            return False

    async def is_read_info(self, bot_id: int, user_id: int) -> bool:
        """Получает значение is_read из Redis"""
        key = RedisKey(bot_id, user_id)
        is_read = await self.redis.hget(f"user:{key}", "read_info")

        if is_read is not None:
            return bool(int(is_read.decode("utf-8")))
        else:
            return False

    async def set_state(self, bot_id: int, user_id: int, state: State) -> None:
        """Сохраняет состояние FSM пользователя в Redis"""
        key = RedisKey(bot_id, user_id)
        # await self._reset_state(bot_id, user_id)
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
