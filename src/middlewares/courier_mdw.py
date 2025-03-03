from aiogram import BaseMiddleware
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
        """Обработка внешних событий"""

        tg_id = event.from_user.id
        bot_id = event.bot.id
        fsm_context = data.get("state")
        state: FSMContext = await fsm_context.get_state()
        state_data = await fsm_context.get_data()

        log.info(f"\nfsm_state: {state}\nfsm_state_data: {state_data}")

        if not state_data:
            await self.rediska.restore_fsm_state(fsm_context, bot_id, tg_id)
            state_data = await fsm_context.get_data()
            log.info(f"is_fsm_restore_data: {True if state_data else False}")

        if state == None:
            state = await self.rediska.get_state(bot_id, tg_id)
            log.info(
                f"\n"
                f"- Courier 🧍\n"
                f"- Outer_mw\n"
                f"- Courier state from redis: {state}"
            )
            if state == None:
                state_previous = state
                state = CustomerState.default.state
                log.info(
                    f"\n"
                    f"- Courier 🧍\n"
                    f"- Outer_mw\n"
                    f"- Courier ID: {tg_id} visited the service for the first time\n"
                    f"- Courier state previous: {state_previous}\n"
                    f"- Courier state: {state}"
                )

            await fsm_context.set_state(state)

        if isinstance(event, Message):
            user_id = event.from_user.id
            message_text = event.text

            log.info(
                f"\n"
                f"- Courier 🧍\n"
                f"- Outer_mw\n"
                f"- Customer message: {message_text}\n"
                f"- Courier ID: {user_id}\n"
                f"- Courier state previous: {state}"
            )

            result = await _check_state_and_handle_message(state, event, handler, data)
            return result

        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            callback_data = event.data

            log.info(
                f"\n"
                f"- Courier - 🧍\n"
                f"- Outer_mw\n"
                f"- Callback data: {callback_data}\n"
                f"- Courier ID: {user_id}\n"
                f"- Courier state previous: {state}"
            )

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
