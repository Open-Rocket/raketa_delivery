from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable

import os
from dotenv import load_dotenv

from app.u_pack.u_states import UserState

load_dotenv()
password = os.getenv("ADMIN_PASSWORD")


async def check_state_and_handle_message(state: str, event: Message, handler: Callable, data: Dict[str, Any]) -> Any:
    message_text = event.text

    # Обработка команды /start в любом состоянии
    if message_text == "/start":
        return await handler(event, data)

    # Проверка на каждое состояние пользователя
    if state == UserState.reg_state.state:
        await event.delete()
        return

    if state == UserState.reg_Name.state:
        if message_text in ["/order", "/profile", "/ai", "/rules", "/help", "/become_courier"]:
            await event.delete()
            return

    if state == UserState.reg_Phone.state:
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


# async def check_state_and_handle_message(state: str, event: Message, handler: Callable, data: Dict[str, Any]) -> Any:
#     message_text = event.text
#
#     if state == UserState.regstate.state:
#         if message_text == "/start":
#             return await handler(event, data)
#         else:
#             await event.delete()
#             return
#
#     if state == UserState.set_Name.state:
#         if message_text == "/start":
#             return await handler(event, data)
#         if message_text in ["/order", "/profile", "/ai", "/rules", "/help", "/become_courier"]:
#             await event.delete()
#             return
#
#     if state == UserState.set_Phone.state:
#         if message_text == "/start":
#             return await handler(event, data)
#         if event.content_type == "contact":
#             return await handler(event, data)
#         elif event.text:
#             await event.delete()
#             return
#         else:
#             await event.delete()
#             return
#
#     if state == UserState.waiting_Courier.state:
#         if message_text == "/start":
#             return await handler(event, data)
#         elif event.text:
#             await event.delete()
#             return
#         else:
#             await event.delete()
#             return
#
#     return await handler(event, data)


class OuterMiddleware(BaseMiddleware):

    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any]) -> Any:

        # Обработка состояния до вызова хендлера
        fsm_context = data.get("state")
        if fsm_context:
            state = await fsm_context.get_state()
        else:
            state = "No state"

        if isinstance(event, Message):
            user_id = event.from_user.id
            message_text = event.text

            print("--------------------")
            print("Users - 🧍")
            print("Outer_mw")
            print(f"User message: {message_text}")
            print(f"User ID: {user_id}")
            print(f"User state previous: {state}")

            # Передаем данные дальше в цепочку
            result = await check_state_and_handle_message(state, event, handler, data)
            return result

        # Обработка callback-запроса
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            callback_data = event.data

            print("--------------------")
            print("Users - 🧍")
            print("Outer_mw")
            print(f"Callback data: {callback_data}")
            print(f"User ID: {user_id}")
            print(f"User state previous: {state}")

            # Вызываем хендлер для callback'ов
            return await handler(event, data)


class InnerMiddleware(BaseMiddleware):

    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any]) -> Any:

        # Обработка состояния до вызова хендлера
        fsm_context = data.get("state")
        if fsm_context:
            state = await fsm_context.get_state()
        else:
            state = "No state"

        if isinstance(event, Message):
            user_id = event.from_user.id
            message_text = event.text

            print("--------------------")
            print("Users - 🧍")
            print("Inner_mw")
            print(f"User message: {message_text}")
            print(f"User ID: {user_id}")
            print(f"User state previous: {state}")

        # Обработка callback-запроса
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            callback_data = event.data

            print("--------------------")
            print("Users - 🧍")
            print("Inner_mw")
            print(f"Callback data: {callback_data}")
            print(f"User ID: {user_id}")

        # Вызываем хендлер после обработки
        result = await handler(event, data)

        # Вывод обновленного состояния после вызова хендлера
        if fsm_context:
            updated_state = await fsm_context.get_state()
        else:
            updated_state = "No state"

        print(f"User state now: {updated_state}")

        return result

# class AdminPasswordAcception(BaseMiddleware):
#
#     async def __call__(self,
#                        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
#                        event: TelegramObject,
#                        data: Dict[str, Any]) -> Any:
#         print("--------------------")
#         print(f"Processing message: {event.text}")
#         result = await handler(event, data)
#         print("Попытка входа в админ панель")
#         if event.text == password:
#             print(f"Доступ разрешен!")
#             return result
#         else:
#             print(f"Доступ откланен!")
#             return result
