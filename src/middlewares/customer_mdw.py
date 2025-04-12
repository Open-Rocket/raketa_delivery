import re
import time
import emoji
import asyncio
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
from src.config import customer_bot, log
from aiogram.types import ReplyKeyboardRemove
from src.services import admin_data, customer_data
from aiogram.exceptions import TelegramBadRequest


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

        service_status = await admin_data.get_service_status()

        if not service_status:
            if isinstance(event, Message):
                await event.answer(
                    text="🚫 <b>Сервис временно недоступен</b>",
                    reply_markup=ReplyKeyboardRemove(),
                    parse_mode="HTML",
                )
            elif isinstance(event, CallbackQuery):
                await event.answer(
                    text="🚫 Сервис временно недоступен",
                    show_alert=True,
                )
                log.info(
                    f"🚫 Сервис временно недоступен для пользователя {event.from_user.id}"
                )

            return

        if isinstance(event, Message):
            start_time = time.time()
            result = await _check_state_and_handle_message(
                fsm_context,
                state,
                event,
                handler,
                data,
                tg_id,
            )
            end_time = time.time()
            log.info(f"Время выполнения: {end_time - start_time:.2f} секунд")
            return result

        elif isinstance(event, CallbackQuery):
            try:
                return await handler(event, data)
            except TelegramBadRequest as e:
                return


async def _check_state_and_handle_message(
    fsm_context: FSMContext,
    state: str,
    event: Message | CallbackQuery,
    handler: Callable,
    data: Dict,
    tg_id: int,
):
    """Проверка состояния пользователя и обработка сообщения"""

    RESTRICTED_COMMANDS = [
        "/order",
        "/my_orders",
        "/profile",
        "/faq",
        "/rules",
        "/become_courier",
        "/become_partner",
        "/channel",
        "/promo",
        "/support",
        "/restart",
    ]

    async def restart_bot():
        await fsm_context.set_state(CustomerState.default.state)
        await customer_bot.send_message(
            chat_id=event.from_user.id,
            text=f"▼ <b>Выберите действие в • ≡ Меню •</b>",
            reply_markup=ReplyKeyboardRemove(),
            disable_notification=True,
            parse_mode="HTML",
        )

    if state == CustomerState.ai_voice_order.state:

        if event.text in RESTRICTED_COMMANDS or event.text == "/start":

            await fsm_context.set_state(CustomerState.default.state)
            await customer_bot.send_message(
                chat_id=event.from_user.id,
                text="Оформление заказа прервано!\nПовторите команду\n\n▼ <b>Выберите действие ...</b>",
                reply_markup=ReplyKeyboardRemove(),
                disable_notification=True,
                parse_mode="HTML",
            )

            await event.delete()

            return

    if state == CustomerState.assistant_run.state:
        if event.text in ("/restart", "/start"):
            await restart_bot()
            return
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
        CustomerState.set_seed_key.state,
    ):
        if event.text in RESTRICTED_COMMANDS:

            await fsm_context.set_state(CustomerState.default.state)
            await asyncio.sleep(0.3)
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
        if event.text in RESTRICTED_COMMANDS:
            await event.delete()
            return

    if state in (CustomerState.reg_Phone.state,):
        if not event.contact or event.contact.user_id != event.from_user.id:
            await event.delete()
            return

    user_is_reg = await customer_data.get_customer_is_reg(tg_id=tg_id)

    log.info(f"reg_status: {tg_id} {user_is_reg}")

    if not user_is_reg:
        if event.text in RESTRICTED_COMMANDS:
            await event.answer(text="Вы не зарегистрировались!\n\n/start")
            return

    if state in (CustomerState.change_Phone.state,):
        if event.text in RESTRICTED_COMMANDS or event.text == "/start":
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

    if event.text == "/restart":
        await restart_bot()
        return

    return await handler(event, data)


__all__ = ["CustomerOuterMiddleware"]
