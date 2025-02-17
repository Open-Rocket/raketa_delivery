import pytest
from aiogram.types import Update
from src.utils import CustomerState


@pytest.mark.asyncio
async def test_cmd_start(bot, dp, message, state):
    test_message = await message(text="/start", user_id=56782547)
    await state(state_value=None)
    update = Update(update_id=1, message=test_message)
    await dp.feed_update(bot, update)


@pytest.mark.asyncio
async def test_data_reg_customer(bot, dp, callback_query, state):
    test_cq = await callback_query(data="reg", user_id=56782547)
    await state(state_value=CustomerState.reg_state)
    update = Update(update_id=1, callback_query=test_cq)
    await dp.feed_update(bot, update)


@pytest.mark.asyncio
async def test_data_name_customer(bot, dp, message, state):
    test_message = await message(text="Ruslan", user_id=56782547)
    await state(state_value=CustomerState.reg_Name)
    update = Update(update_id=1, message=test_message)
    await dp.feed_update(bot, update)


@pytest.mark.asyncio
async def test_data_phone_customer(bot, dp, message, state):
    test_message = await message(text="89993501515", user_id=56782547)
    await state(state_value=CustomerState.reg_Phone)
    update = Update(update_id=1, message=test_message)
    await dp.feed_update(bot, update)


# pytest tests/customerBot/test_registration_steps.py -s -v

# pytest tests/customerBot/test_registration_steps.py -s -v -k test_cmd_start
# pytest tests/customerBot/test_registration_steps.py -s -v -k test_data_reg_customer
# pytest tests/customerBot/test_registration_steps.py -s -v -k test_data_name_customer
# pytest tests/customerBot/test_registration_steps.py -s -v -k test_data_phone_customer
