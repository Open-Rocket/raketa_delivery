import pytest
from aiogram.types import Update, Contact
from src.utils import CustomerState


@pytest.mark.asyncio
async def test_cmd_order(bot, dp, message, state):

    test_message = await message(text="/order", user_id=56782547)
    await state(state_value=CustomerState.default)
    update = Update(update_id=1, message=test_message)
    await dp.feed_update(bot, update)


"""

pytest tests/customerBot/test_commands.py -s -v -k test_cmd_order


"""
