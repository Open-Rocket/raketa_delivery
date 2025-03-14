from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import (
    Message,
    TelegramObject,
    CallbackQuery,
)
from src.confredis import RedisService
from src.config import log
from src.utils import CourierState


class CourierOuterMiddleware(BaseMiddleware):

    def __init__(self, rediska: RedisService):
        self.rediska = rediska

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        """Обработка внешних событий"""

        tg_id = event.from_user.id
        bot_id = event.bot.id
        fsm_context: FSMContext = data.get("state")
        state: FSMContext = await fsm_context.get_state()

        if state == None:
            state = await self.rediska.get_state(bot_id, tg_id)

            if state == None:
                state = CourierState.default.state

            await fsm_context.set_state(None)
            await fsm_context.set_state(state)
            data["state"] = fsm_context

        state_data = await fsm_context.get_data()

        if not state_data:
            await self.rediska.restore_fsm_state(fsm_context, bot_id, tg_id)
            state_data = await fsm_context.get_data()

        log.info(f"FSM перед вызовом хендлера: {state}")

        if isinstance(event, Message):
            result = await _check_state_and_handle_message(state, event, handler, data)
            return result

        elif isinstance(event, CallbackQuery):
            return await handler(event, data)


async def _check_state_and_handle_message(
    state: str, event: Message, handler: Callable, data: Dict[str, Any]
) -> Any:
    message_text = event.text

    if state in (
        CourierState.reg_state.state,
        CourierState.reg_Name.state,
        CourierState.reg_Phone.state,
        CourierState.reg_City.state,
        CourierState.reg_tou.state,
        CourierState.change_Name.state,
        CourierState.change_Phone.state,
        CourierState.change_City.state,
    ):
        if message_text in [
            "/run",
            "/my_orders",
            "/profile",
            "/start",
            "/subs",
            "/faq",
            "/rules",
            "/make_order",
        ]:
            log.info(f"MessageText: {message_text}")
            await event.delete()
            return

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

    if state in {CourierState.location.state, CourierState.myOrders.state}:
        if message_text not in ["/my_orders", "/location", "/start"]:
            await event.delete()
            return

    if state == CourierState.reg_state.state:
        await event.delete()
        return

    if state == CourierState.reg_Phone.state and not event.contact:
        await event.delete()
        return

    log.info(f"State: {state}")

    return await handler(event, data)


__all__ = ["CourierOuterMiddleware"]
