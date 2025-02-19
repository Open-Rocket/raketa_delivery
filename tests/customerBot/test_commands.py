import pytest
from aiogram.types import Update, Contact
from src.utils import CustomerState


@pytest.mark.asyncio
async def test_cmd_order(bot, dp, message, state):

    test_message = await message(text="/order", user_id=56782547)
    await state(state_value=CustomerState.default)
    update = Update(update_id=1, message=test_message)
    await dp.feed_update(bot, update)


@pytest.mark.asyncio
async def test_cmd_profile(bot, dp, message, state):

    test_message = await message(text="/profile", user_id=56782547)
    await state(state_value=CustomerState.default)
    update = Update(update_id=1, message=test_message)
    await dp.feed_update(bot, update)


@pytest.mark.asyncio
async def test_cmd_faq(bot, dp, message, state):

    test_message = await message(text="/faq", user_id=56782547)
    await state(state_value=CustomerState.default)
    update = Update(update_id=1, message=test_message)
    await dp.feed_update(bot, update)


@pytest.mark.asyncio
async def test_cmd_rules(bot, dp, message, state):

    test_message = await message(text="/rules", user_id=56782547)
    await state(state_value=CustomerState.default)
    update = Update(update_id=1, message=test_message)
    await dp.feed_update(bot, update)


@pytest.mark.asyncio
async def test_cmd_become_courier(bot, dp, message, state):

    test_message = await message(text="/rules", user_id=56782547)
    await state(state_value=CustomerState.default)
    update = Update(update_id=1, message=test_message)
    await dp.feed_update(bot, update)


"""

pytest tests/customerBot/test_commands.py -s -v -k test_cmd_order
pytest tests/customerBot/test_commands.py -s -v -k test_cmd_profile
pytest tests/customerBot/test_commands.py -s -v -k test_cmd_faq
pytest tests/customerBot/test_commands.py -s -v -k test_cmd_rules
pytest tests/customerBot/test_commands.py -s -v -k test_cmd_become_courier

"""
