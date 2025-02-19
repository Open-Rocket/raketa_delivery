import pytest
from aiogram.types import Update, Contact
from src.utils import CustomerState


@pytest.mark.asyncio
async def test_cmd_start(bot, dp, message, state, user_id):
    test_message = await message(text="/start", user_id=user_id)
    await state(state_value=None)
    update = Update(update_id=1, message=test_message)
    await dp.feed_update(bot, update)


@pytest.mark.asyncio
async def test_data_reg_customer(bot, dp, callback_query, state, user_id):
    test_cq = await callback_query(data="reg", user_id=user_id)
    await state(state_value=CustomerState.reg_state)
    update = Update(update_id=1, callback_query=test_cq)
    await dp.feed_update(bot, update)


@pytest.mark.asyncio
async def test_data_name_customer(bot, dp, message, state, user_id):
    test_message = await message(text="Ruslan", user_id=user_id)
    await state(state_value=CustomerState.reg_Name)
    update = Update(update_id=1, message=test_message)
    await dp.feed_update(bot, update)


@pytest.mark.asyncio
async def test_data_phone_customer(bot, dp, message, state, user_id):
    test_message = await message(
        text=None,
        contact=Contact(
            phone_number="89993501515", first_name="Ruslan_*", user_id=user_id
        ),
    )
    await state(state_value=CustomerState.reg_Phone)
    update = Update(update_id=1, message=test_message)
    await dp.feed_update(bot, update)


@pytest.mark.asyncio
async def test_data_city_customer(bot, dp, message, state, user_id):
    test_message = await message(text="Москва", user_id=user_id)
    await state(state_value=CustomerState.reg_City)
    update = Update(update_id=1, message=test_message)
    await dp.feed_update(bot, update)


@pytest.mark.asyncio
async def test_customer_accept_tou(bot, dp, callback_query, state, user_id):
    test_cq = await callback_query(data="accept_tou", user_id=user_id)
    await state(state_value=CustomerState.reg_City)
    update = Update(update_id=1, callback_query=test_cq)
    await dp.feed_update(bot, update)


"""

pytest tests/customerBot/test_registration_steps.py -s -v -k test_cmd_start
pytest tests/customerBot/test_registration_steps.py -s -v -k test_data_reg_customer
pytest tests/customerBot/test_registration_steps.py -s -v -k test_data_name_customer
pytest tests/customerBot/test_registration_steps.py -s -v -k test_data_phone_customer
pytest tests/customerBot/test_registration_steps.py -s -v -k test_data_city_customer
pytest tests/customerBot/test_registration_steps.py -s -v -k test_customer_accept_tou

"""
