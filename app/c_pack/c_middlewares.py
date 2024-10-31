import logging
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
import os
from dotenv import load_dotenv

from app.c_pack.c_states import CourierRegistration, CourierState

# Загрузка переменных окружения
load_dotenv()
password = os.getenv("ADMIN_PASSWORD")

# Настройка логгера для одного сообщения на логический блок
logging.basicConfig(level=logging.INFO, format='--------------------\n%(message)s\n--------------------')
logger = logging.getLogger(__name__)

async def check_state_and_handle_message(state: str, event: Message, handler: Callable,
                                         data: Dict[str, Any]) -> Any:
    message_text = event.text

    if state == CourierState.location.state:
        return await handler(event, data)

    if message_text == "/start":
        return await handler(event, data)

    if message_text == "/subs":
        return await handler(event, data)

    if state in (CourierRegistration.name.state, CourierRegistration.phone_number.state,
                 CourierRegistration.city.state, CourierRegistration.accept_tou.state):
        if message_text in ["/my_orders", "/location", "/start"]:
            await event.delete()
            return

    if state in {CourierState.location.state, CourierState.myOrders.state}:
        if message_text not in ["/my_orders", "/location", "/start"]:
            await event.delete()
            return

    if state == CourierState.start_reg.state:
        await event.delete()
        return

    if state == CourierRegistration.phone_number.state and not event.contact:
        await event.delete()
        return

    return await handler(event, data)

class OuterMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject, data: Dict[str, Any]) -> Any:

        fsm_context = data.get("state")
        state = await fsm_context.get_state() if fsm_context else "No state"

        if isinstance(event, Message):
            user_id = event.from_user.id
            message_text = event.text

            # Формируем лог-сообщение для OuterMiddleware
            log_message = f"Couriers - 🚴\nOuter_mw\nCourier message: {message_text}\nCourier ID: {user_id}\nCourier state previous: {state}"
            logger.info(log_message)

            result = await check_state_and_handle_message(state, event, handler, data)
            return result

        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            callback_data = event.data

            log_message = f"Couriers - 🚴\nOuter_mw\nCallback data: {callback_data}\nCourier ID: {user_id}\nCourier state previous: {state}"
            logger.info(log_message)

            return await handler(event, data)

class InnerMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject, data: Dict[str, Any]) -> Any:

        fsm_context = data.get("state")
        state = await fsm_context.get_state() if fsm_context else "No state"

        log_message = ""
        if isinstance(event, Message):
            user_id = event.from_user.id
            message_text = event.text

            log_message += f"Couriers - 🚴\nInner_mw\nCourier message: {message_text}\nCourier ID: {user_id}\nCourier state previous: {state}"

        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            callback_data = event.data

            log_message += f"Couriers - 🚴\nInner_mw\nCallback data: {callback_data}\nCourier ID: {user_id}"

        result = await handler(event, data)

        updated_state = await fsm_context.get_state() if fsm_context else "No state"
        log_message += f"\nCourier state now: {updated_state}"

        logger.info(log_message)
        return result
