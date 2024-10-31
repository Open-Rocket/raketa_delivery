import logging
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
import os
from dotenv import load_dotenv
from app.u_pack.u_states import UserState

# Загрузка переменных окружения
load_dotenv()
password = os.getenv("ADMIN_PASSWORD")

# Настройка логгера для одного сообщения на логический блок
logging.basicConfig(level=logging.INFO, format='--------------------\n%(message)s\n--------------------')
logger = logging.getLogger(__name__)

async def check_state_and_handle_message(state: str, event: Message, handler: Callable,
                                         data: Dict[str, Any]) -> Any:
    message_text = event.text

    # Обработка команды /start в любом состоянии
    if message_text == "/start":
        return await handler(event, data)

    # Проверка на каждое состояние пользователя
    if state == UserState.reg_state.state:
        await event.delete()
        return

    if state in (UserState.reg_Name.state, UserState.reg_City.state, UserState.reg_tou.state):
        if message_text in ["/order", "/profile", "/my_orders", "/faq", "/rules", "/become_courier"]:
            await event.delete()
            return

    if state == UserState.reg_Phone.state or state == UserState.change_Phone.state:
        if event.content_type == "contact":  # Если тип контента - контакт
            return await handler(event, data)
        else:
            await event.delete()
            return

    if state == UserState.waiting_Courier.state:
        await event.delete()
        return

    # Обработка сообщения в случае, если ни одно состояние не совпало
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
            log_message = f"Users - 🧍\nOuter_mw\nUser message: {message_text}\nUser ID: {user_id}\nUser state previous: {state}"
            logger.info(log_message)

            result = await check_state_and_handle_message(state, event, handler, data)
            return result

        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            callback_data = event.data

            log_message = f"Users - 🧍\nOuter_mw\nCallback data: {callback_data}\nUser ID: {user_id}\nUser state previous: {state}"
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

            log_message += f"Users - 🧍\nInner_mw\nUser message: {message_text}\nUser ID: {user_id}\nUser state previous: {state}"

        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            callback_data = event.data

            log_message += f"Users - 🧍\nInner_mw\nCallback data: {callback_data}\nUser ID: {user_id}"

        result = await handler(event, data)

        updated_state = await fsm_context.get_state() if fsm_context else "No state"
        log_message += f"\nUser state now: {updated_state}"

        logger.info(log_message)
        return result
