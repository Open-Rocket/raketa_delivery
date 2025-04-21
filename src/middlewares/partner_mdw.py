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
from src.utils import PartnerState
from src.config import admin_bot, partner_bot
from aiogram.types import ReplyKeyboardRemove, ContentType
from src.services import partner_data, admin_data
from src.utils import kb
from aiogram.exceptions import TelegramBadRequest


class AgentOuterMiddleware(BaseMiddleware):
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
        chat_id = event.chat.id if isinstance(event, Message) else event.message.chat.id
        bot_id = event.bot.id
        fsm_context: FSMContext = data.get("state")

        state = await fsm_context.get_state()
        state_data = await fsm_context.get_data()

        if state is None:
            state = await self.rediska.get_state(bot_id, tg_id)

            if state is None:
                state = PartnerState.default.state

            await fsm_context.set_state(state)

        if not state_data:
            await self.rediska.restore_fsm_state(fsm_context, bot_id, tg_id)
            state_data = await fsm_context.get_data()

        service_status = await admin_data.get_service_status()
        partner_program_status = await admin_data.get_partner_program_status()
        is_block = await admin_data.get_partner_block_status(tg_id=tg_id)

        if is_block:
            await event.answer(
                text="🚫 Вы были заблокированы!",
                reply_markup=ReplyKeyboardRemove(),
                parse_mode="HTML",
            )
            return

        if not service_status:
            if isinstance(event, Message):
                await event.answer(
                    text="<b>🛠️ Сервис временно недоступен!</b>\nВедутся технические работы.",
                    reply_markup=ReplyKeyboardRemove(),
                    parse_mode="HTML",
                )
            elif isinstance(event, CallbackQuery):
                await event.answer(
                    text="🛠️ Сервис временно недоступен!\nВедутся технические работы.",
                    show_alert=True,
                )

            return

        if not partner_program_status:
            if isinstance(event, Message):
                await event.answer(
                    text="🚫 <b>Партнерская программа временно недоступна</b>",
                    reply_markup=ReplyKeyboardRemove(),
                    parse_mode="HTML",
                )
            elif isinstance(event, CallbackQuery):
                await event.answer(
                    text="🚫 Партнерская программа временно недоступна",
                    show_alert=True,
                )
                log.info(
                    f"🚫 Партнерская программа временно недоступна для пользователя {event.from_user.id}"
                )

            return

        if isinstance(event, Message):

            result = await _check_state_and_handle_message(
                tg_id,
                chat_id,
                fsm_context,
                state,
                event,
                handler,
                data,
            )
            return result

        elif isinstance(event, CallbackQuery):
            try:
                return await handler(event, data)
            except TelegramBadRequest as e:
                return


async def _check_state_and_handle_message(
    tg_id: int,
    chat_id: int,
    fsm_context: FSMContext,
    state: str,
    event: Message | CallbackQuery,
    handler: Callable,
    data: Dict,
):
    """Проверка состояния агента и обработка сообщения"""

    seed_key = await partner_data.get_my_seed_key(tg_id)

    if not seed_key:
        text = "Вам нужно сгенерировать ваш персональный SEED-ключ, чтобы начать работу с сервисом.\n\n"

        reply_kb = await kb.get_partner_kb("generate_seed")

        await event.answer(
            text=text,
            reply_markup=reply_kb,
            parse_mode="HTML",
        )
        return

    return await handler(event, data)


__all__ = ["AgentOuterMiddleware"]
