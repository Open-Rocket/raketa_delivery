import pytest
from aiogram.types import Update, Contact
from src.utils import CustomerState


@pytest.mark.asyncio
async def test_data_ai(bot, dp, callback_query, state, user_id):
    test_cq = await callback_query(data="ai_order", user_id=user_id)
    await state(state_value=CustomerState.ai_voice_order)
    update = Update(update_id=1, callback_query=test_cq)
    await dp.feed_update(bot, update)


# ---


@pytest.mark.asyncio
async def test_cancel_order(bot, dp, callback_query, state, user_id):
    test_cq = await callback_query(data="cancel_order", user_id=user_id)
    await state(state_value=CustomerState.default)
    update = Update(update_id=1, callback_query=test_cq)
    await dp.feed_update(bot, update)


# ---


@pytest.mark.asyncio
async def test_set_name(bot, dp, callback_query, state, user_id):
    test_cq = await callback_query(data="set_my_name", user_id=user_id)
    await state(state_value=CustomerState.change_Name)
    update = Update(update_id=1, callback_query=test_cq)
    await dp.feed_update(bot, update)


@pytest.mark.asyncio
async def test_change_name(bot, dp, message, state, user_id):
    test_message = await message(text="Gogi", user_id=user_id)
    await state(state_value=CustomerState.change_Name)
    update = Update(update_id=1, message=test_message)
    await dp.feed_update(bot, update)


# ---


@pytest.mark.asyncio
async def test_set_phone(bot, dp, callback_query, state, user_id):
    test_cq = await callback_query(data="set_my_phone", user_id=user_id)
    await state(state_value=CustomerState.change_Phone)
    update = Update(update_id=1, callback_query=test_cq)
    await dp.feed_update(bot, update)


@pytest.mark.asyncio
async def test_change_phone(bot, dp, message, state, user_id):
    test_message = await message(
        text=None,
        contact=Contact(
            phone_number="89993502424", first_name="Ruslan_*", user_id=user_id
        ),
    )
    await state(state_value=CustomerState.change_Phone)
    update = Update(update_id=1, message=test_message)
    await dp.feed_update(bot, update)


# ---


@pytest.mark.asyncio
async def test_set_city(bot, dp, callback_query, state, user_id):
    test_cq = await callback_query(data="set_my_city", user_id=user_id)
    await state(state_value=CustomerState.change_City)
    update = Update(update_id=1, callback_query=test_cq)
    await dp.feed_update(bot, update)


@pytest.mark.asyncio
async def test_change_city(bot, dp, message, state, user_id):
    test_message = await message(text="Владикавказ", user_id=user_id)
    await state(state_value=CustomerState.change_City)
    update = Update(update_id=1, message=test_message)
    await dp.feed_update(bot, update)


"""

pytest tests/customerBot/test_clicks.py -s -v -k test_data_ai

pytest tests/customerBot/test_clicks.py -s -v -k test_cancel_order

pytest tests/customerBot/test_clicks.py -s -v -k test_set_name
pytest tests/customerBot/test_clicks.py -s -v -k test_change_name

pytest tests/customerBot/test_clicks.py -s -v -k test_set_phone
pytest tests/customerBot/test_clicks.py -s -v -k test_change_phone

pytest tests/customerBot/test_clicks.py -s -v -k test_set_city
pytest tests/customerBot/test_clicks.py -s -v -k test_change_city

"""
