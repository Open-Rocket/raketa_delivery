import pytest
from aiogram.types import Update, Contact
from src.utils import CourierState


# ---


@pytest.mark.asyncio
async def test_cmd_start(bot, dp, message, state, user_id):
    test_message = await message(text="/start", user_id=user_id)
    await state(state_value=None)
    update = Update(update_id=1, message=test_message)
    await dp.feed_update(bot, update)


@pytest.mark.asyncio
async def test_data_reg_courier(bot, dp, callback_query, state, user_id):
    test_cq = await callback_query(data="reg", user_id=user_id)
    await state(state_value=CourierState.reg_state)
    update = Update(update_id=1, callback_query=test_cq)
    await dp.feed_update(bot, update)


@pytest.mark.asyncio
async def test_data_name_courier(bot, dp, message, state, user_id):
    test_message = await message(text="Ruslan", user_id=user_id)
    await state(state_value=CourierState.reg_Name)
    update = Update(update_id=1, message=test_message)
    await dp.feed_update(bot, update)


@pytest.mark.asyncio
async def test_data_phone_courier(bot, dp, message, state, user_id):
    test_message = await message(
        text=None,
        contact=Contact(phone_number="89993501515", first_name="Gogi", user_id=user_id),
    )
    await state(state_value=CourierState.reg_Phone)
    update = Update(update_id=1, message=test_message)
    await dp.feed_update(bot, update)


@pytest.mark.asyncio
async def test_data_city_courier(bot, dp, message, state, user_id):
    test_message = await message(text="Москва", user_id=user_id)
    await state(state_value=CourierState.reg_City)
    update = Update(update_id=1, message=test_message)
    await dp.feed_update(bot, update)


@pytest.mark.asyncio
async def test_courier_accept_tou(bot, dp, callback_query, state, user_id):
    test_cq = await callback_query(data="accept_tou", user_id=user_id)
    await state(state_value=CourierState.reg_City)
    update = Update(update_id=1, callback_query=test_cq)
    await dp.feed_update(bot, update)


# ---


@pytest.mark.asyncio
async def test_cmd_profile(bot, dp, message, state, user_id):
    test_message = await message(text="/profile", user_id=user_id)
    await state(state_value=CourierState.default)
    update = Update(update_id=1, message=test_message)
    await dp.feed_update(bot, update)


@pytest.mark.asyncio
async def test_cmd_faq(bot, dp, message, state, user_id):
    test_message = await message(text="/faq", user_id=user_id)
    await state(state_value=CourierState.default)
    update = Update(update_id=1, message=test_message)
    await dp.feed_update(bot, update)


@pytest.mark.asyncio
async def test_cmd_rules(bot, dp, message, state, user_id):
    test_message = await message(text="/rules", user_id=user_id)
    await state(state_value=CourierState.default)
    update = Update(update_id=1, message=test_message)
    await dp.feed_update(bot, update)


# ---


@pytest.mark.asyncio
async def test_set_name(bot, dp, callback_query, state, user_id):
    test_cq = await callback_query(data="set_my_name", user_id=user_id)
    await state(state_value=CourierState.change_Name)
    update = Update(update_id=1, callback_query=test_cq)
    await dp.feed_update(bot, update)


@pytest.mark.asyncio
async def test_set_phone(bot, dp, callback_query, state, user_id):
    test_cq = await callback_query(data="set_my_phone", user_id=user_id)
    await state(state_value=CourierState.change_Phone)
    update = Update(update_id=1, callback_query=test_cq)
    await dp.feed_update(bot, update)


@pytest.mark.asyncio
async def test_set_city(bot, dp, callback_query, state, user_id):
    test_cq = await callback_query(data="set_my_city", user_id=user_id)
    await state(state_value=CourierState.change_City)
    update = Update(update_id=1, callback_query=test_cq)
    await dp.feed_update(bot, update)


# ---


@pytest.mark.asyncio
async def test_change_name(bot, dp, message, state, user_id):
    test_message = await message(text="Gogi", user_id=user_id)
    await state(state_value=CourierState.change_Name)
    update = Update(update_id=1, message=test_message)
    await dp.feed_update(bot, update)


@pytest.mark.asyncio
async def test_change_phone(bot, dp, message, state, user_id):
    test_message = await message(
        text=None,
        contact=Contact(phone_number="89993502424", first_name="Gogi", user_id=user_id),
    )
    await state(state_value=CourierState.change_Phone)
    update = Update(update_id=1, message=test_message)
    await dp.feed_update(bot, update)


@pytest.mark.asyncio
async def test_change_city(bot, dp, message, state, user_id):
    test_message = await message(text="Владикавказ", user_id=user_id)
    await state(state_value=CourierState.change_City)
    update = Update(update_id=1, message=test_message)
    await dp.feed_update(bot, update)


# ---


@pytest.mark.asyncio
async def test_handle_pending_orders_message(bot, dp, message, state, user_id):
    pass


@pytest.mark.asyncio
async def test_handle_pending_orders_callback(bot, dp, callback_query, state, user_id):
    pass


# ---


@pytest.mark.asyncio
async def test_update_order_status_to_db(bot, dp, callback_query, state, user_id):
    pass


"""

pytest tests/courierBot/test_clicks.py -s -v -k test_cmd_start
pytest tests/courierBot/test_clicks.py -s -v -k test_data_reg_courier
pytest tests/courierBot/test_clicks.py -s -v -k test_data_name_courier
pytest tests/courierBot/test_clicks.py -s -v -k test_data_phone_courier
pytest tests/courierBot/test_clicks.py -s -v -k test_data_city_courier
pytest tests/courierBot/test_clicks.py -s -v -k test_courier_accept_tou

pytest tests/courierBot/test_clicks.py -s -v -k test_cmd_profile
pytest tests/courierBot/test_clicks.py -s -v -k test_cmd_faq
pytest tests/courierBot/test_clicks.py -s -v -k test_cmd_rules

pytest tests/courierBot/test_clicks.py -s -v -k test_set_name
pytest tests/courierBot/test_clicks.py -s -v -k test_set_phone
pytest tests/courierBot/test_clicks.py -s -v -k test_set_city

pytest tests/courierBot/test_clicks.py -s -v -k test_change_name
pytest tests/courierBot/test_clicks.py -s -v -k test_change_phone
pytest tests/courierBot/test_clicks.py -s -v -k test_change_city

pytest tests/courierBot/test_clicks.py -s -v -k test_handle_pending_orders_message
pytest tests/courierBot/test_clicks.py -s -v -k test_handle_pending_orders_callback

pytest tests/courierBot/test_clicks.py -s -v -k test_update_order_status_to_db

"""
