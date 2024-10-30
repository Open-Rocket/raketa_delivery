from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable

import os
from dotenv import load_dotenv

from app.c_pack.c_states import CourierRegistration, CourierState
from app.u_pack.u_states import UserState

load_dotenv()
password = os.getenv("ADMIN_PASSWORD")


async def check_state_and_handle_message(state: str, event: Message, handler: Callable,
                                         data: Dict[str, Any]) -> Any:
    message_text = event.text

    if state == CourierState.location.state:
        return await handler(event, data)

    # Обработка команды /start для курьера
    if message_text == "/start":
        return await handler(event, data)

    # Обработка состояния регистрации курьера
    if state in (CourierRegistration.name.state,
                 CourierRegistration.phone_number.state,
                 CourierRegistration.city.state,
                 CourierRegistration.accept_tou.state):
        if message_text in ["/my_orders", "/location", "/start"]:
            await event.delete()
            return

    # Если курьер пытается выполнить команду не в `default` состоянии
    if state in {CourierState.location.state, CourierState.myOrders.state}:
        if message_text not in ["/my_orders", "/location", "/start"]:
            await event.delete()
            return

    # Состояние при отсутствии регистрации (инициализация)
    if state == CourierState.start_reg.state:
        await event.delete()
        return

    # Если состояние регистрации курьера и сообщение не содержит номер телефона
    if state == CourierRegistration.phone_number.state and not event.contact:
        await event.delete()
        return

    # Обработка остальных состояний по умолчанию
    return await handler(event, data)


class OuterMiddleware(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any]) -> Any:

        # Проверка состояния до вызова хендлера
        fsm_context = data.get("state")
        state = await fsm_context.get_state() if fsm_context else "No state"

        if isinstance(event, Message):
            user_id = event.from_user.id
            message_text = event.text

            print("--------------------")
            print("Couriers - 🚴")
            print("Outer_mw")
            print(f"Courier message: {message_text}")
            print(f"Courier ID: {user_id}")
            print(f"Courier state previous: {state}")

            # Передаем данные дальше в цепочку
            result = await check_state_and_handle_message(state, event, handler, data)
            return result

        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            callback_data = event.data

            print("--------------------")
            print("Couriers - 🚴")
            print("Outer_mw")
            print(f"Callback data: {callback_data}")
            print(f"Courier ID: {user_id}")
            print(f"Courier state previous: {state}")

            return await handler(event, data)


class InnerMiddleware(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any]) -> Any:

        fsm_context = data.get("state")
        state = await fsm_context.get_state() if fsm_context else "No state"

        if isinstance(event, Message):
            user_id = event.from_user.id
            message_text = event.text

            print("--------------------")
            print("Couriers - 🚴")
            print("Inner_mw")
            print(f"Courier message: {message_text}")
            print(f"Courier ID: {user_id}")
            print(f"Courier state previous: {state}")

        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            callback_data = event.data

            print("--------------------")
            print("Couriers - 🚴")
            print("Inner_mw")
            print(f"Callback data: {callback_data}")
            print(f"Courier ID: {user_id}")

        # Вызов хендлера и вывод обновленного состояния
        result = await handler(event, data)

        if fsm_context:
            updated_state = await fsm_context.get_state()
        else:
            updated_state = "No state"

        print(f"Courier state now: {updated_state}")

        return result
