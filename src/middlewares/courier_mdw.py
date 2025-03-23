import re
import emoji
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
from src.config import courier_bot
from aiogram.types import ReplyKeyboardRemove, ContentType


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

        state = await fsm_context.get_state()
        state_data = await fsm_context.get_data()

        if state is None:
            state = await self.rediska.get_state(bot_id, tg_id)

            if state is None:
                state = CourierState.default.state

            await fsm_context.set_state(state)

        if not state_data:
            await self.rediska.restore_fsm_state(fsm_context, bot_id, tg_id)
            state_data = await fsm_context.get_data()

        if isinstance(event, Message):

            result = await _check_state_and_handle_message(
                fsm_context,
                state,
                event,
                handler,
                data,
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
    """Проверка состояния курьера и обработка сообщения"""

    RESTRICTED_COMMANDS = [
        "/run",
        "/my_orders",
        "/profile",
        "/subs",
        "/faq",
        "/rules",
        "/make_order",
        "/channel",
        "/become_partner",
        "/chat",
        "/orders_bot",
        "/restart",
    ]

    async def restart_bot():
        await fsm_context.set_state(CourierState.default.state)
        await courier_bot.send_message(
            chat_id=event.from_user.id,
            text="Бот был перезапущен!\n\n▼ <b>Выберите действие ...</b>",
            reply_markup=ReplyKeyboardRemove(),
            disable_notification=True,
            parse_mode="HTML",
        )

    if state in (CourierState.reg_Phone.state,):
        if event.text in [
            "/start",
        ]:
            return await handler(event, data)

    if state in (
        CourierState.change_Name.state,
        CourierState.change_City.state,
    ):
        if event.text in RESTRICTED_COMMANDS:

            await fsm_context.set_state(CourierState.default.state)
            return await handler(event, data)

    if state in (
        CourierState.reg_Name.state,
        CourierState.reg_City.state,
        CourierState.change_Name.state,
        CourierState.change_City.state,
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
        CourierState.reg_state.state,
        CourierState.reg_Name.state,
        CourierState.reg_Phone.state,
        CourierState.reg_City.state,
        CourierState.reg_tou.state,
    ):
        if event.text in RESTRICTED_COMMANDS:
            await event.delete()
            return

    if state in (CourierState.reg_Phone.state,):
        if not event.contact or event.contact.user_id != event.from_user.id:
            await event.delete()
            return

    if state in (
        CourierState.location.state,
        CourierState.change_Phone.state,
    ):

        if event.text in [
            "/start",
            "/my_orders",
            "/profile",
            "/subs",
            "/faq",
            "/rules",
            "/make_order",
            "/restart",
        ]:
            await courier_bot.send_message(
                chat_id=event.from_user.id,
                text="-",
                reply_markup=ReplyKeyboardRemove(),
                disable_notification=True,
            )

            return await handler(event, data)

        if event.content_type == ContentType.LOCATION:
            return await handler(event, data)

        if not event.contact or event.contact.user_id != event.from_user.id:
            await event.delete()
            return

    if event.text == "/restart":
        await restart_bot()
        return

    return await handler(event, data)


__all__ = ["CourierOuterMiddleware"]
