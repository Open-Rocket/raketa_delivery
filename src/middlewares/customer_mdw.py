import logging
from aiogram import Router, BaseMiddleware, filters, F
from aiogram.fsm.context import FSMContext
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import (
    Message,
    TelegramObject,
    CallbackQuery,
)

from src.config import log
from src.confredis import RedisService
from src.utils import CustomerState


class CustomerOuterMiddleware(BaseMiddleware):

    def __init__(self, rediska: RedisService):
        super().__init__()
        self.rediska = rediska

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:

        customer_id = event.from_user.id
        fsm_context = data.get("state")
        state = await fsm_context.get_state()

        log.info(f"fsm_state: {state}")

        if state == None:
            state = await self.rediska.get_state(event.bot.id, customer_id)
            log.info(
                f"\n"
                f"- Customer 🧍\n"
                f"- Outer_mw\n"
                f"- Customer state from redis: {state}"
            )
            if state == None:
                state_previous = state
                state = CustomerState.default.state
                log.info(
                    f"\n"
                    f"- Customer 🧍\n"
                    f"- Outer_mw\n"
                    f"- Customer ID: {customer_id} visited the service for the first time\n"
                    f"- Customer state previous: {state_previous}\n"
                    f"- Customer state: {state}"
                )

            await fsm_context.set_state(state)

        if isinstance(event, Message):
            user_id = event.from_user.id
            message_text = event.text

            log.info(
                f"\n"
                f"- Customer 🧍\n"
                f"- Outer_mw\n"
                f"- Customer message: {message_text}\n"
                f"- Customer ID: {user_id}\n"
                f"- Customer state previous: {state}"
            )

            result = await _check_state_and_handle_message(state, event, handler, data)
            return result

        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            callback_data = event.data

            log.info(
                f"\n"
                f"- Customer - 🧍\n"
                f"- Outer_mw\n"
                f"- Callback data: {callback_data}\n"
                f"- Customer ID: {user_id}\n"
                f"- Customer state previous: {state}"
            )

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
