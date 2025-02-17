import pytest
import pytest
from unittest.mock import AsyncMock
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, Update
from aiogram.fsm.context import FSMContext
from src.config import moscow_time
from src.app.customer import customer_r, CustomerState


@pytest.mark.asyncio
async def test_customer_router():
    bot = AsyncMock(spec=Bot)
    bot.id = 777

    dp = Dispatcher()
    dp.include_router(customer_r)

    message = Message(
        message_id=1,
        from_user={"id": 56782547, "is_bot": False, "first_name": "Gogich"},
        chat={"id": 1846124, "type": "private"},
        text="/start",
        date=moscow_time,
    )

    update = Update(update_id=1, message=message)

    await dp.feed_update(bot, update)


# pytest tests/customerBot/test_cmd_start.py -s -v
