from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import (
    Message,
    TelegramObject,
    CallbackQuery,
)
from src.confredis import RedisService
from src.utils import CustomerState


class CustomerOuterMiddleware(BaseMiddleware):

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
        state_data = await fsm_context.get_data()

        if not state_data:
            await self.rediska.restore_fsm_state(fsm_context, bot_id, tg_id)
            state_data = await fsm_context.get_data()

        if not state:
            state = await self.rediska.get_state(bot_id, tg_id)

            if state == None:
                state = CustomerState.default.state

            await fsm_context.set_state(state)

        if isinstance(event, Message):
            result = await _check_state_and_handle_message(state, event, handler, data)
            return result

        elif isinstance(event, CallbackQuery):
            return await handler(event, data)


async def _check_state_and_handle_message(
    state: str, event: Message, handler: Callable, data: Dict[str, Any]
) -> Any:
    """Проверка состояния пользователя и обработка сообщения"""

    message_text = event.text

    if message_text == "/start":
        return await handler(event, data)

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

    if state == CustomerState.assistant_run.state:
        await event.delete()
        return

    return await handler(event, data)


__all__ = ["CustomerOuterMiddleware"]
