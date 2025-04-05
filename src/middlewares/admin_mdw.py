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
from src.utils import AdminState
from src.config import admin_bot, SUPER_ADMIN_TG_ID
from aiogram.types import ReplyKeyboardRemove, ContentType
from src.services import admin_data


class AdminOuterMiddleware(BaseMiddleware):
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
                state = AdminState.default.state

            await fsm_context.set_state(state)

        if not state_data:
            await self.rediska.restore_fsm_state(fsm_context, bot_id, tg_id)
            state_data = await fsm_context.get_data()

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

            return await handler(event, data)


async def _check_state_and_handle_message(
    tg_id: int,
    chat_id: int,
    fsm_context: FSMContext,
    state: str,
    event: Message,
    handler: Callable,
    data: Dict,
):
    """Проверка состояния курьера и обработка сообщения"""

    admins = await admin_data.get_all_admins()
    admins_tg_id = [admin.admin_tg_id for admin in admins]

    log.info(f"tg_id:{tg_id} SUPER_ADMIN_TG_ID:{SUPER_ADMIN_TG_ID} ")

    if tg_id == SUPER_ADMIN_TG_ID:
        return await handler(event, data)

    # if tg_id not in admins_tg_id:
    #     await admin_bot.send_message(
    #         chat_id=chat_id,
    #         text="У вас нет прав администрирования",
    #         reply_markup=ReplyKeyboardRemove(),
    #     )
    #     return

    return await handler(event, data)


__all__ = ["AdminOuterMiddleware"]
