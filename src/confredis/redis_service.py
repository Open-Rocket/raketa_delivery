import asyncio
import json
import redis.asyncio as aioredis
from .redis_config import RedisConfig
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import Message
from src.config import log


class RedisKey:
    DEFAULT_DESTINY = "default"

    def __init__(
        self,
        bot_id,
        user_id,
        thread_id=None,
        business_connection_id=None,
        destiny=DEFAULT_DESTINY,
        is_state=False,
    ):
        self.bot_id = bot_id
        self.user_id = user_id
        self.chat_id = f"{bot_id}" if is_state else f"{bot_id}{user_id}"
        self.thread_id = thread_id
        self.business_connection_id = business_connection_id
        self.destiny = destiny

    def __str__(self):
        return self.chat_id


class RedisService:

    def __init__(self, redis: aioredis.Redis):
        self.redis = redis
        self.fsm_storage = RedisStorage(self.redis)

    # ---

    async def set_state(self, bot_id: int, user_id: int, state: State):
        """Сохраняет состояние FSM пользователя в Redis"""
        key = RedisKey(bot_id, user_id, is_state=True)
        try:
            await self.fsm_storage.set_state(key=key, state=state)
        except Exception as e:
            log.error(f"Ошибка записи состояния в Redis: {e}")

    async def save_fsm_state(
        self, state: FSMContext, bot_id: int, user_id: int
    ) -> None:
        """Сохраняет состояние FSM в Redis"""
        data = await state.get_data()
        key = RedisKey(bot_id, user_id)
        await self.redis.set(f"state_data: {str(key)}", json.dumps(data))

    async def get_state(self, bot_id: int, user_id: int) -> str | None:
        """Получает текущее состояние FSM пользователя из Redis"""
        key = RedisKey(bot_id, user_id, is_state=True)
        return await self.fsm_storage.get_state(key=key)

    async def load_fsm_state(self, bot_id: int, user_id: int) -> dict:
        """Загружает состояние FSM из Redis"""
        key = RedisKey(bot_id, user_id)
        raw_data = await self.redis.get(f"state_data: {str(key)}")
        return json.loads(raw_data) if raw_data else {}

    async def restore_fsm_state(
        self,
        state: FSMContext,
        bot_id: int,
        user_id: int,
    ) -> None:
        """Восстанавливает состояние FSM из Redis"""
        data = await self.load_fsm_state(bot_id, user_id)
        await state.set_data(data)

    # ---

    async def set_message(self, bot_id: int, user_id: int, message: Message):
        """Сохраняет ID сообщения от пользователя в Redis."""
        key = f"user_message:{RedisKey(bot_id, user_id)}"
        await self.redis.set(key, message.message_id)

    async def get_message_id(self, bot_id: int, user_id: int) -> int | None:
        """Получает ID сообщения от пользователя из Redis."""
        key = f"user_message:{RedisKey(bot_id, user_id)}"
        message_id = await self.redis.get(key)
        return int(message_id) if message_id else None

    async def delete_message(self, bot_id: int, user_id: int):
        """Удаляет ID сообщения от пользователя из Redis."""
        key = f"user_message:{RedisKey(bot_id, user_id)}"
        await self.redis.delete(key)

    # ---

    async def set_name(self, bot_id: int, user_id: int, name: str) -> bool:
        """Сохраняет имя пользователя в Redis и возвращает статус операции"""
        key = RedisKey(bot_id, user_id)
        try:
            # raise Exception("TestException")
            await self.redis.hset(f"user_info:{key}", mapping={"name": name})
            return True
        except Exception as e:
            log.error(f"Ошибка записи имени в Redis: {e}")
            return False

    async def set_phone(self, bot_id: int, user_id: int, phone: str) -> bool:
        """Сохраняет имя и телефон пользователя в Redis"""
        key = RedisKey(bot_id, user_id)
        try:
            await self.redis.hset(f"user_info:{key}", mapping={"phone": phone})
            return True
        except Exception as e:
            log.error(f"Ошибка записи телефона в Redis: {e}")
            return False

    async def set_city(self, bot_id: int, user_id: int, city: str) -> bool:
        """Сохраняет имя и телефон пользователя в Redis"""
        key = RedisKey(bot_id, user_id)
        try:
            await self.redis.hset(f"user_info:{key}", mapping={"city": city})
            return True
        except Exception as e:
            log.error(f"Ошибка записи города в Redis: {e}")
            return False

    async def set_reg(self, bot_id: int, user_id: int, value: bool) -> bool:
        """Устанавливает статус регистрации пользователя в Redis"""
        key = RedisKey(bot_id, user_id)
        try:
            # raise Exception("TestException")
            await self.redis.hset(f"user_info:{key}", "is_reg", int(value))
            return True
        except Exception as e:
            log.error(f"Ошибка записи статуса регистрации в Redis: {e}")
            return False

    async def set_read_info(self, bot_id: int, user_id: int, value: bool) -> bool:
        """Устанавливает статус ознакомления пользователя с оформлением заказа"""
        key = RedisKey(bot_id, user_id)
        try:
            await self.redis.hset(f"user_info:{key}", "read_info", int(value))
            return True
        except Exception as e:
            log.error(f"Ошибка записи статуса ознакомления с информацией в Redis: {e}")
            return False

    # ---

    async def get_name(self, bot_id: int, user_id: int) -> str | None:
        """Получает имя и телефон пользователя из Redis"""
        key = RedisKey(bot_id, user_id)
        user_data = await self.redis.hgetall(f"user_info:{key}")
        if not user_data:
            return None
        return user_data.get(b"name", b"").decode("utf-8")

    async def get_phone(self, bot_id: int, user_id: int) -> str | None:
        """Получает имя и телефон пользователя из Redis"""
        key = RedisKey(bot_id, user_id)
        user_data = await self.redis.hgetall(f"user_info:{key}")
        if not user_data:
            return None
        return user_data.get(b"phone", b"").decode("utf-8")

    async def get_city(self, bot_id: int, user_id: int) -> str | None:
        """Получает имя и телефон пользователя из Redis"""
        key = RedisKey(bot_id, user_id)
        user_data = await self.redis.hgetall(f"user_info:{key}")
        if not user_data:
            return None
        return user_data.get(b"city", b"").decode("utf-8")

    async def get_tou(self, bot_id: int, user_id: int) -> str | None:
        """Получает имя и телефон пользователя из Redis"""
        key = RedisKey(bot_id, user_id)
        user_data = await self.redis.hgetall(f"user_info:{key}")
        if not user_data:
            return None
        return user_data.get(b"tou", b"").decode("utf-8")

    async def get_user_info(self, bot_id: int, user_id: int) -> str | None:
        """Получает имя и телефон пользователя из Redis"""
        key = RedisKey(bot_id, user_id)
        user_data = await self.redis.hgetall(f"user_info:{key}")
        if not user_data:
            return (
                None,
                None,
                None,
            )
        return (
            user_data.get(b"name", b"").decode("utf-8"),
            user_data.get(b"phone", b"").decode("utf-8"),
            user_data.get(b"city", b"").decode("utf-8"),
        )

    # ---

    async def is_reg(self, bot_id: int, user_id: int) -> bool | None:
        """Получает статус регистрации пользователя из Redis"""
        key = RedisKey(bot_id, user_id)
        try:
            is_reg = await self.redis.hget(f"user_info:{key}", "is_reg")
            if is_reg is None:
                return False
            return bool(int(is_reg.decode("utf-8")))
        except Exception as e:
            log.error(f"Ошибка чтения статуса регистрации из Redis: {e}")
            return None

    async def is_read_info(self, bot_id: int, user_id: int) -> bool:
        """Получает значение is_read из Redis"""
        key = RedisKey(bot_id, user_id)
        try:
            is_read = await self.redis.hget(f"user_info:{key}", "read_info")
            if is_read is None:
                return False
            return bool(int(is_read.decode("utf-8")))
        except Exception as e:
            log.error(f"Ошибка чтения статуса ознакомления с информацией из Redis: {e}")
            return False

    # ---


async def create_redis_service() -> RedisService:
    """Асинхронная фабрика для создания экземпляра RedisService"""
    redis_instance = await RedisConfig.create_redis()
    return RedisService(redis_instance)


async def main():

    rediska: RedisService = await create_redis_service()

    return rediska


rediska: RedisService = asyncio.run(main())

__all__ = ["rediska", "create_redis_service", "RedisService"]
