import re
import emoji
from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from typing import Callable, Dict, Awaitable
from aiogram.types import (
    Message,
    TelegramObject,
    CallbackQuery,
    ContentType,
)
from src.confredis import RedisService
from src.utils import CustomerState
from src.config import customer_bot
from aiogram.types import ReplyKeyboardRemove


class CustomerOuterMiddleware(BaseMiddleware):

    def __init__(self, rediska: RedisService):
        self.rediska = rediska

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict], Awaitable],
        event: Message | CallbackQuery,
        data: Dict,
    ):
        """Обработка внешних событий"""

        tg_id = event.from_user.id
        bot_id = event.bot.id
        fsm_context: FSMContext = data.get("state")
        state: FSMContext = await fsm_context.get_state()
        state_data = await fsm_context.get_data()

        if not state:
            state = await self.rediska.get_state(bot_id, tg_id)

            if state == None:
                state = CustomerState.default.state

            await fsm_context.set_state(state)

        if not state_data:
            await self.rediska.restore_fsm_state(fsm_context, bot_id, tg_id)
            state_data = await fsm_context.get_data()

        if isinstance(event, Message):
            result = await _check_state_and_handle_message(
                fsm_context, state, event, handler, data
            )
            return result

        elif isinstance(event, CallbackQuery):
            return await handler(event, data)


async def _check_state_and_handle_message(
    fsm_context: FSMContext,
    state: str,
    event: Message,
    handler: Callable,
    data: Dict,
):
    """Проверка состояния пользователя и обработка сообщения"""

    if state == CustomerState.assistant_run.state:
        await event.delete()
        return

    if state in (CustomerState.reg_Phone.state,):
        if event.text in [
            "/start",
        ]:

            return await handler(event, data)

    if state in (
        CustomerState.change_Name.state,
        CustomerState.change_City.state,
    ):
        if event.text in [
            "/order",
            "/my_orders",
            "/profile",
            "/faq",
            "/rules",
            "/become_courier",
        ]:

            await fsm_context.set_state(CustomerState.default.state)
            return await handler(event, data)

    if state in (
        CustomerState.reg_Name.state,
        CustomerState.reg_City.state,
        CustomerState.change_Name.state,
        CustomerState.change_City.state,
    ):
        if event.content_type != ContentType.TEXT:
            await event.delete()
            return

        if emoji.emoji_count(event.text) > 0:

            text_without_emojis = emoji.replace_emoji(event.text, replace="")
            text_only_chars = re.sub(r"\s", "", text_without_emojis)

            if not text_only_chars:
                await event.delete()
                return

            return await handler(event, data)

    if state in (
        CustomerState.reg_state.state,
        CustomerState.reg_Name.state,
        CustomerState.reg_Phone.state,
        CustomerState.reg_City.state,
        CustomerState.reg_tou.state,
    ):
        if event.text in [
            "/order",
            "/my_orders",
            "/profile",
            "/faq",
            "/rules",
            "/become_courier",
        ]:
            await event.delete()
            return

    if state in (CustomerState.reg_Phone.state,):
        if not event.contact or event.contact.user_id != event.from_user.id:
            await event.delete()
            return

    if state in (CustomerState.change_Phone.state,):

        if event.text in [
            "/order",
            "/my_orders",
            "/profile",
            "/faq",
            "/rules",
            "/become_courier",
        ]:
            await customer_bot.send_message(
                chat_id=event.from_user.id,
                text="-",
                reply_markup=ReplyKeyboardRemove(),
                disable_notification=True,
            )

            return await handler(event, data)

        if not event.contact or event.contact.user_id != event.from_user.id:
            await event.delete()
            return

    return await handler(event, data)


__all__ = ["CustomerOuterMiddleware"]
