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
from src.utils import CourierState


logging.basicConfig(
    level=logging.INFO, format="--------------------\n%(message)s\n--------------------"
)


class CourierOuterMiddleware(BaseMiddleware):

    def __init__(self, rediska: RedisService):
        super().__init__()
        self.rediska = rediska

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:

        fsm_context = data.get("state")
        state: FSMContext = (
            await fsm_context.get_state()
            if fsm_context
            else await self.rediska.get_state()
        )

        if isinstance(event, Message):
            user_id = event.from_user.id
            message_text = event.text

            # Формируем лог-сообщение для OuterMiddleware
            log_message = f"Couriers - 🚴\nOuter_mw\nCourier message: {message_text}\nCourier ID: {user_id}\nCourier state previous: {state}"
            log.info(log_message)

            result = await _check_state_and_handle_message(state, event, handler, data)
            return result

        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            callback_data = event.data

            log_message = f"Couriers - 🚴\nOuter_mw\nCallback data: {callback_data}\nCourier ID: {user_id}\nCourier state previous: {state}"
            log.info(log_message)

            return await handler(event, data)


async def _check_state_and_handle_message(
    state: str, event: Message, handler: Callable, data: Dict[str, Any]
) -> Any:
    message_text = event.text

    if state == CourierState.location.state:
        return await handler(event, data)

    if state in (
        CourierState.myOrders.state,
        CourierState.myOrders_completed.state,
        CourierState.myOrders_active.state,
    ):
        return await handler(event, data)

    if message_text == "/start":
        return await handler(event, data)

    if message_text == "/subs":
        return await handler(event, data)

    if state in (
        CourierState.name.state,
        CourierState.phone_number.state,
        CourierState.city.state,
        CourierState.accept_tou.state,
        CourierState.change_Name.state,
        CourierState.change_Phone.state,
        CourierState.change_City.state,
    ):
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

    if state == CourierState.phone_number.state and not event.contact:
        await event.delete()
        return

    return await handler(event, data)


__all__ = ["CourierOuterMiddleware"]
