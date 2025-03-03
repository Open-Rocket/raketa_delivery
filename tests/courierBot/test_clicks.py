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
    pass


@pytest.mark.asyncio
async def test_data_name_courier(bot, dp, message, state, user_id):
    pass


@pytest.mark.asyncio
async def test_data_phone_courier(bot, dp, message, state, user_id):
    pass


@pytest.mark.asyncio
async def test_data_city_courier(bot, dp, message, state, user_id):
    pass


@pytest.mark.asyncio
async def test_courier_accept_tou(bot, dp, callback_query, state, user_id):
    pass


# ---


@pytest.mark.asyncio
async def test_cmd_profile(bot, dp, message, state, user_id):
    pass


@pytest.mark.asyncio
async def test_cmd_faq(bot, dp, message, state, user_id):
    pass


@pytest.mark.asyncio
async def test_cmd_rules(bot, dp, message, state, user_id):
    pass


@pytest.mark.asyncio
async def test_cmd_make_order(bot, dp, message, state, user_id):
    pass


# ---


@pytest.mark.asyncio
async def test_set_name(bot, dp, callback_query, state, user_id):
    pass


@pytest.mark.asyncio
async def test_set_phone(bot, dp, callback_query, state, user_id):
    pass


@pytest.mark.asyncio
async def test_set_city(bot, dp, callback_query, state, user_id):
    pass


# ---


@pytest.mark.asyncio
async def test_change_name(bot, dp, message, state, user_id):
    pass


@pytest.mark.asyncio
async def test_change_phone(bot, dp, message, state, user_id):
    pass


@pytest.mark.asyncio
async def test_change_city(bot, dp, message, state, user_id):
    pass


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

pytest tests/customerBot/test_clicks.py -s -v -k test_cmd_start
pytest tests/customerBot/test_clicks.py -s -v -k test_data_reg_courier
pytest tests/customerBot/test_clicks.py -s -v -k test_data_name_courier
pytest tests/customerBot/test_clicks.py -s -v -k test_data_phone_courier
pytest tests/customerBot/test_clicks.py -s -v -k test_data_city_courier
pytest tests/customerBot/test_clicks.py -s -v -k test_courier_accept_tou

pytest tests/customerBot/test_clicks.py -s -v -k test_cmd_profile
pytest tests/customerBot/test_clicks.py -s -v -k test_cmd_faq
pytest tests/customerBot/test_clicks.py -s -v -k test_cmd_rules
pytest tests/customerBot/test_clicks.py -s -v -k test_cmd_make_order

pytest tests/customerBot/test_clicks.py -s -v -k test_set_name
pytest tests/customerBot/test_clicks.py -s -v -k test_set_phone
pytest tests/customerBot/test_clicks.py -s -v -k test_set_city

pytest tests/customerBot/test_clicks.py -s -v -k test_change_name
pytest tests/customerBot/test_clicks.py -s -v -k test_change_phone
pytest tests/customerBot/test_clicks.py -s -v -k test_change_city

pytest tests/customerBot/test_clicks.py -s -v -k test_handle_pending_orders_message
pytest tests/customerBot/test_clicks.py -s -v -k test_handle_pending_orders_callback

pytest tests/customerBot/test_clicks.py -s -v -k test_update_order_status_to_db

"""
