import asyncio
import json
import redis.asyncio as aioredis
from .redis_config import RedisConfig
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from typing import Optional
from src.config import log
from aiogram.types import Message


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

    async def set_fsm_state_and_data(
        self,
        bot_id: int,
        user_id: int,
        state: str,
        data: dict | None,
    ) -> None:
        """Сохраняет состояние и данные FSM пользователя в Redis"""

        key_state = RedisKey(bot_id, user_id, is_state=True)
        await self.fsm_storage.set_state(key=key_state, state=state)

        if data:
            key_data = RedisKey(bot_id, user_id, is_state=False)
            await self.fsm_storage.set_state(key=key_data, state=json.dumps(data))

    async def get_fsm_state_and_data(self, bot_id: int, user_id: int) -> tuple:
        """Получает состояние и данные FSM пользователя из Redis"""

        # Ключ для состояния
        key = RedisKey(bot_id, user_id, is_state=True)
        raw_state = await self.fsm_storage.get_state(key=key)

        # Ключ для данных
        key_data = RedisKey(bot_id, user_id, is_state=False)
        raw_data = await self.fsm_storage.get_state(key=key_data)

        # Если данные и состояние найдены, возвращаем их
        if raw_state and raw_data:
            return raw_state, json.loads(raw_data)  # В данных преобразуем JSON
        else:
            log.warning(f"FSM state or data not found for user {user_id}.")
            return None, None

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

    async def set_state(self, bot_id: int, user_id: int, state: State) -> None:
        """Сохраняет состояние FSM пользователя в Redis"""
        key = RedisKey(bot_id, user_id, is_state=True)
        await self.fsm_storage.set_state(key=key, state=state)

    async def get_state(self, bot_id: int, user_id: int) -> str | None:
        """Получает текущее состояние FSM пользователя из Redis"""
        key = RedisKey(bot_id, user_id)
        return await self.fsm_storage.get_state(key=key)

    # ---

    async def set_name(self, bot_id: int, user_id: int, name: str) -> bool:
        """Сохраняет имя и телефон пользователя в Redis"""
        key = RedisKey(bot_id, user_id)
        await self.redis.hset(f"user_info:{key}", mapping={"name": name})
        return True

    async def set_phone(self, bot_id: int, user_id: int, phone: str) -> bool:
        """Сохраняет имя и телефон пользователя в Redis"""
        key = RedisKey(bot_id, user_id)
        await self.redis.hset(f"user_info:{key}", mapping={"phone": phone})
        return True

    async def set_city(self, bot_id: int, user_id: int, city: str) -> bool:
        """Сохраняет имя и телефон пользователя в Redis"""
        key = RedisKey(bot_id, user_id)
        await self.redis.hset(f"user_info:{key}", mapping={"city": city})
        return True

    async def set_tou(self, bot_id: int, user_id: int, tou: str) -> bool:
        """Сохраняет имя и телефон пользователя в Redis"""
        key = RedisKey(bot_id, user_id)
        await self.redis.hset(f"user_info:{key}", mapping={"tou": tou})
        return True

    async def set_reg(self, bot_id: int, user_id: int, value: bool) -> bool:
        """Устанавливает статус регистрации пользователя в Redis"""
        key = RedisKey(bot_id, user_id)
        await self.redis.hset(f"user_info:{key}", "is_reg", int(value))
        return True

    async def set_read_info(self, bot_id: int, user_id: int, value: bool) -> bool:
        """Устанавливает статус ознакомления пользователя с оформлением заказа"""
        key = RedisKey(bot_id, user_id)
        await self.redis.hset(f"user_info:{key}", "read_info", int(value))
        return True

    # ---

    async def save_fsm_state(
        self, state: FSMContext, bot_id: int, user_id: int
    ) -> None:
        """Сохраняет состояние FSM в Redis"""
        data = await state.get_data()
        key = RedisKey(bot_id, user_id)
        await self.redis.set(f"state_data: {str(key)}", json.dumps(data))

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

    async def restore_fsm_state_2(
        self,
        state: FSMContext,
        bot_id: int,
        user_id: int,
    ) -> None:
        """Полностью восстанавливает состояние и данные FSM из Redis"""

        fsm_state, fsm_data = await self.get_fsm_state_and_data(bot_id, user_id)

        if fsm_state:
            # Восстанавливаем состояние
            await state.set_state(fsm_state)
            log.info(f"FSM state restored for user {user_id}: {fsm_state}")
        else:
            log.warning(f"FSM state not found for user {user_id}.")
            return  # Без состояния нет смысла загружать данные

        if fsm_data:
            # Восстанавливаем данные FSM
            await state.set_data(fsm_data)
            log.info(f"FSM data restored for user {user_id}: {fsm_data}")
        else:
            log.warning(f"No FSM data found for user {user_id}.")

    async def reset_fsm_state(
        self, state: FSMContext, bot_id: int, user_id: int
    ) -> bool:
        """Очищает данные в state"""
        await state.clear()
        key = RedisKey(bot_id, user_id)
        await self.redis.set(f"state_data: {str(key)}", json.dumps({}))
        return True

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
                None,
            )
        return (
            user_data.get(b"name", b"").decode("utf-8"),
            user_data.get(b"phone", b"").decode("utf-8"),
            user_data.get(b"city", b"").decode("utf-8"),
            user_data.get(b"tou", b"").decode("utf-8"),
        )

    # ---

    async def is_reg(self, bot_id: int, user_id: int) -> bool:
        """Получает статус регистрации пользователя из Redis"""
        key = RedisKey(bot_id, user_id)
        is_reg = await self.redis.hget(f"user_info:{key}", "is_reg")

        if is_reg is not None:
            return bool(int(is_reg.decode("utf-8")))
        else:
            return False

    async def is_read_info(self, bot_id: int, user_id: int) -> bool:
        """Получает значение is_read из Redis"""
        key = RedisKey(bot_id, user_id)
        is_read = await self.redis.hget(f"user_info:{key}", "read_info")

        if is_read is not None:
            return bool(int(is_read.decode("utf-8")))
        else:
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
