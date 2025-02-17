import pytest_asyncio
from unittest.mock import AsyncMock, patch
from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery, User
from src.app.customer import FSMContext
from src.config import moscow_time
from src.app.customer import customer_r
from src.config import fsm_customer_storage
from aiogram.fsm.storage.base import StorageKey


@pytest_asyncio.fixture(scope="function")
async def bot():
    bot = AsyncMock(spec=Bot)
    bot.id = 88888888
    return bot


@pytest_asyncio.fixture(scope="function")
async def dp():
    dp = Dispatcher(storage=fsm_customer_storage)
    dp.include_router(customer_r)
    return dp


@pytest_asyncio.fixture(scope="function")
async def message():
    async def _message(text="/start", user_id=56782547):

        user = User(id=user_id, is_bot=False, first_name="Ruslan")

        return Message(
            message_id=1,
            from_user=user,
            chat={"id": 1846124, "type": "private"},
            text=text,
            date=moscow_time,
        )

    return _message


@pytest_asyncio.fixture(scope="function")
async def callback_query():
    async def _callback_query(
        user_id=56782547,
        data="test_data",
        chat_id=1846124,
        message_id=1,
        callback_query_id="1",
    ):

        user = User(id=user_id, is_bot=False, first_name="Ruslan_*")

        return CallbackQuery(
            id=callback_query_id,
            from_user=user,
            chat_instance="test_instance",
            data=data,
            message=Message(
                message_id=message_id,
                from_user=user,
                chat={"id": chat_id, "type": "private"},
                text="Test message",
                date=moscow_time,
            ),
        )

    return _callback_query


@pytest_asyncio.fixture(scope="function")
async def mock_state():
    async def _state(state_value=None):
        fsm_state = AsyncMock(spec=FSMContext)
        fsm_state.get_state = AsyncMock(return_value=state_value)
        return fsm_state

    return _state


# Фикстура для состояния
@pytest_asyncio.fixture(scope="function")
async def state():

    storage = fsm_customer_storage

    async def _state(state_value=None):
        key = StorageKey(bot_id=88888888, chat_id=1846124, user_id=56782547)
        fsm_context = FSMContext(storage=storage, key=key)

        # Устанавливаем состояние, если оно передано
        if state_value:
            await fsm_context.set_state(state_value)

        return fsm_context

    return _state
