import pytest
from aiogram.types import Update, Contact
from src.utils import CustomerState


# ---


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


# ---


@pytest.mark.asyncio
async def test_cmd_order(bot, dp, message, state, user_id):

    test_message = await message(text="/order", user_id=user_id)
    await state(state_value=CustomerState.default)
    update = Update(update_id=1, message=test_message)
    await dp.feed_update(bot, update)


@pytest.mark.asyncio
async def test_cmd_profile(bot, dp, message, state, user_id):

    test_message = await message(text="/profile", user_id=user_id)
    await state(state_value=CustomerState.default)
    update = Update(update_id=1, message=test_message)
    await dp.feed_update(bot, update)


@pytest.mark.asyncio
async def test_cmd_faq(bot, dp, message, state, user_id):

    test_message = await message(text="/faq", user_id=user_id)
    await state(state_value=CustomerState.default)
    update = Update(update_id=1, message=test_message)
    await dp.feed_update(bot, update)


@pytest.mark.asyncio
async def test_cmd_rules(bot, dp, message, state, user_id):

    test_message = await message(text="/rules", user_id=user_id)
    await state(state_value=CustomerState.default)
    update = Update(update_id=1, message=test_message)
    await dp.feed_update(bot, update)


@pytest.mark.asyncio
async def test_cmd_become_courier(bot, dp, message, state, user_id):

    test_message = await message(text="/rules", user_id=user_id)
    await state(state_value=CustomerState.default)
    update = Update(update_id=1, message=test_message)
    await dp.feed_update(bot, update)


# ---


@pytest.mark.asyncio
async def test_set_name(bot, dp, callback_query, state, user_id):
    test_cq = await callback_query(data="set_my_name", user_id=user_id)
    await state(state_value=CustomerState.change_Name)
    update = Update(update_id=1, callback_query=test_cq)
    await dp.feed_update(bot, update)


@pytest.mark.asyncio
async def test_set_phone(bot, dp, callback_query, state, user_id):
    test_cq = await callback_query(data="set_my_phone", user_id=user_id)
    await state(state_value=CustomerState.change_Phone)
    update = Update(update_id=1, callback_query=test_cq)
    await dp.feed_update(bot, update)


@pytest.mark.asyncio
async def test_set_city(bot, dp, callback_query, state, user_id):
    test_cq = await callback_query(data="set_my_city", user_id=user_id)
    await state(state_value=CustomerState.change_City)
    update = Update(update_id=1, callback_query=test_cq)
    await dp.feed_update(bot, update)


# ---


@pytest.mark.asyncio
async def test_change_name(bot, dp, message, state, user_id):
    test_message = await message(text="Gogi", user_id=user_id)
    await state(state_value=CustomerState.change_Name)
    update = Update(update_id=1, message=test_message)
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


@pytest.mark.asyncio
async def test_change_city(bot, dp, message, state, user_id):
    test_message = await message(text="Владикавказ", user_id=user_id)
    await state(state_value=CustomerState.change_City)
    update = Update(update_id=1, message=test_message)
    await dp.feed_update(bot, update)


# ---


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
async def test_handle_my_orders_message(bot, dp, message, state, user_id):
    test_message = await message(text="/my_orders", user_id=user_id)
    await state(state_value=CustomerState.default)
    update = Update(update_id=1, message=test_message)
    await dp.feed_update(bot, update)


@pytest.mark.asyncio
async def test_handle_my_orders_callback(bot, dp, callback_query, state, user_id):
    test_cq = await callback_query(data="back_myOrders", user_id=user_id)
    await state(state_value=CustomerState.default)
    update = Update(update_id=1, callback_query=test_cq)
    await dp.feed_update(bot, update)


# ---


@pytest.mark.asyncio
async def test_process_order(bot, dp, message, state, user_id):
    order_text: str = (
        "Привет! Заказ в Москве, забирать нужно с улицы Мосфильмовская, дом 53. Доставить на улицу Петровка, дом 19. Там лекарства, это важно, потому что их ждут. Забрать можно с 14:00. Получатель — Ольга, номер 89978987865, свяжитесь с ней, если возникнут вопросы. Спасибо!"
    )

    test_message = await message(text=order_text, user_id=user_id)
    await state(state_value=CustomerState.ai_voice_order)
    update = Update(update_id=1, message=test_message)
    await dp.feed_update(bot, update)


"""

pytest tests/customerBot/test_clicks.py -s -v -k test_cmd_start
pytest tests/customerBot/test_clicks.py -s -v -k test_data_reg_customer
pytest tests/customerBot/test_clicks.py -s -v -k test_data_name_customer
pytest tests/customerBot/test_clicks.py -s -v -k test_data_phone_customer
pytest tests/customerBot/test_clicks.py -s -v -k test_data_city_customer
pytest tests/customerBot/test_clicks.py -s -v -k test_customer_accept_tou

pytest tests/customerBot/test_clicks.py -s -v -k test_cmd_order
pytest tests/customerBot/test_clicks.py -s -v -k test_cmd_profile
pytest tests/customerBot/test_clicks.py -s -v -k test_cmd_faq
pytest tests/customerBot/test_clicks.py -s -v -k test_cmd_rules
pytest tests/customerBot/test_clicks.py -s -v -k test_cmd_become_courier

pytest tests/customerBot/test_clicks.py -s -v -k test_set_name
pytest tests/customerBot/test_clicks.py -s -v -k test_set_phone
pytest tests/customerBot/test_clicks.py -s -v -k test_set_city

pytest tests/customerBot/test_clicks.py -s -v -k test_change_name
pytest tests/customerBot/test_clicks.py -s -v -k test_change_phone
pytest tests/customerBot/test_clicks.py -s -v -k test_change_city

pytest tests/customerBot/test_clicks.py -s -v -k test_data_ai

pytest tests/customerBot/test_clicks.py -s -v -k test_cancel_order

pytest tests/customerBot/test_clicks.py -s -v -k test_handle_my_orders_message
pytest tests/customerBot/test_clicks.py -s -v -k test_handle_my_orders_callback

pytest tests/customerBot/test_clicks.py -s -v -k test_process_order



"""
