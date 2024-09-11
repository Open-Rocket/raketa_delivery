from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable


import os
from dotenv import load_dotenv

load_dotenv()
password = os.getenv("ADMIN_PASSWORD")


class OuterMiddleware(BaseMiddleware):

    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any]) -> Any:
        fsm_context = data.get("state")
        if fsm_context:
            state = await fsm_context.get_state()
        else:
            state = "No state"

        # Обработка обычного сообщения
        if isinstance(event, Message):
            user_id = event.from_user.id
            message_text = event.text

            print("--------------------")
            print("Couriers")
            print("Outer_mw")
            print(f"User message: {message_text}")
            print(f"User ID: {user_id}")
            print(f"User state previous: {state}")

        # Обработка callback-запроса
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            callback_data = event.data

            print("--------------------")
            print("Couriers")
            print("Outer_mw")
            print(f"Callback data: {callback_data}")
            print(f"User ID: {user_id}")
            print(f"User state previous: {state}")

        result = await handler(event, data)
        return result


class InnerMiddleware(BaseMiddleware):

    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any]) -> Any:

        # Обработка обычного сообщения
        if isinstance(event, Message):
            user_id = event.from_user.id
            message_text = event.text

            print("--------------------")
            print("Couriers")
            print("Inner_mw")
            print(f"User message: {message_text}")
            print(f"User ID: {user_id}")

        # Обработка callback-запроса
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            callback_data = event.data

            print("--------------------")
            print("Couriers")
            print("Inner_mw")
            print(f"Callback data: {callback_data}")
            print(f"User ID: {user_id}")

        # Вызов хендлера
        result = await handler(event, data)

        # Проверка состояния после вызова хендлера
        fsm_context = data.get("state")
        if fsm_context:
            state = await fsm_context.get_state()
        else:
            state = "No state"

        # Вывод обновленного состояния
        print(f"User state now: {state}")

        return result


class AdminPasswordAcception(BaseMiddleware):

    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any]) -> Any:
        print("--------------------")
        print(f"Processing message: {event.text}")
        result = await handler(event, data)
        print("Попытка входа в админ панель")
        if event.text == password:
            print(f"Доступ разрешен!")
            return result
        else:
            print(f"Доступ откланен!")
            return result
