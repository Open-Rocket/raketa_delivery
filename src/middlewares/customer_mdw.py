import logging
from aiogram import Router, BaseMiddleware, filters, F
from aiogram.fsm.context import FSMContext
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import (
    Message,
    TelegramObject,
    CallbackQuery,
)

from config import log
from confredis import RedisService
from utils import CustomerState


logging.basicConfig(
    level=logging.INFO, format="--------------------\n%(message)s\n--------------------"
)


class CustomerOuterMiddleware(BaseMiddleware):

    def __init__(self, rediska: RedisService, state: FSMContext):
        super().__init__()
        self.rediska = rediska

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:

        customer_id = event.from_user.id
        fsm_context: FSMContext = data.get("state")

        if fsm_context is not None:
            state = fsm_context.get_state()
            await self.rediska.set_state(event.bot, customer_id, state)
        else:
            state = await self.rediska.get_state(event.bot, customer_id)
            if state is None:
                state = CustomerState.default.state
                await fsm_context.set_state(state)
                await self.rediska.set_state(event.bot, customer_id, state)

        if isinstance(event, Message):
            user_id = event.from_user.id
            message_text = event.text

            # Формируем лог-сообщение для OuterMiddleware
            log_message = f"Customer - 🧍\nOuter_mw\nUser message: {message_text}\Customer ID: {user_id}\Customer state previous: {state}"
            log.info(log_message)

            result = await _check_state_and_handle_message(state, event, handler, data)
            return result

        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            callback_data = event.data

            log_message = f"Customer - 🧍\nOuter_mw\nCallback data: {callback_data}\Customer ID: {user_id}\Customer state previous: {state}"
            log.info(log_message)

            return await handler(event, data)


async def _check_state_and_handle_message(
    state: str, event: Message, handler: Callable, data: Dict[str, Any]
) -> Any:
    message_text = event.text

    # Обработка команды /start в любом состоянии
    if message_text == "/start":
        return await handler(event, data)

    # Проверка на каждое состояние пользователя
    if state == CustomerState.reg_state.state:
        await event.delete()
        return

    if state in (
        CustomerState.reg_Name.state,
        CustomerState.reg_City.state,
        CustomerState.reg_tou.state,
    ):
        if message_text in [
            "/order",
            "/profile",
            "/my_orders",
            "/faq",
            "/rules",
            "/become_courier",
        ]:
            await event.delete()
            return

    if (
        state == CustomerState.reg_Phone.state
        or state == CustomerState.change_Phone.state
    ):
        if event.content_type == "contact":
            return await handler(event, data)
        else:
            await event.delete()
            return

    if state == CustomerState.waiting_Courier.state:
        await event.delete()
        return

    # Обработка сообщения в случае, если ни одно состояние не совпало
    return await handler(event, data)


__all__ = ["CustomerOuterMiddleware"]
