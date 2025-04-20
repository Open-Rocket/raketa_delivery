import re
import emoji
import asyncio
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
from aiogram.exceptions import TelegramBadRequest


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
    """Проверка состояния курьера и обработка сообщения"""

    RESTRICTED_COMMANDS = [
        "/start",
        "/users",
        "/orders",
        "/admins",
        "/global",
    ]

    log.info(f"state: {state} ")

    if state in (
        AdminState.default.state,
        AdminState.change_standard_order_price.state,
        AdminState.change_subscription_price.state,
        AdminState.change_max_order_price.state,
        AdminState.change_distance_coefficient_less_5.state,
        AdminState.change_distance_coefficient_5_10.state,
        AdminState.change_distance_coefficient_10_20.state,
        AdminState.change_distance_coefficient_more_20.state,
        AdminState.change_time_coefficient_00_06.state,
        AdminState.change_time_coefficient_06_12.state,
        AdminState.change_time_coefficient_12_18.state,
        AdminState.change_time_coefficient_18_21.state,
        AdminState.change_time_coefficient_21_00.state,
        AdminState.change_big_cities_coefficient.state,
        AdminState.change_small_cities_coefficient.state,
        AdminState.change_subscription_discount.state,
        AdminState.change_first_order_discount.state,
        AdminState.change_free_period.state,
        AdminState.change_refund_percent.state,
        AdminState.full_speed_report_by_date.state,
        AdminState.full_speed_report_by_period.state,
        AdminState.full_financial_report_by_date.state,
        AdminState.full_financial_report_by_period.state,
        AdminState.set_new_admin.state,
        AdminState.del_admin.state,
        AdminState.reg_adminPhone.state,
        AdminState.change_min_refund_amount.state,
        AdminState.change_max_refund_amount.state,
        AdminState.process_request.state,
        AdminState.change_base_order_XP.state,
        AdminState.change_distance_XP.state,
        AdminState.change_speed_XP.state,
        AdminState.full_distance_report_by_date.state,
        AdminState.full_distance_report_by_period.state,
        AdminState.full_orders_report_by_date.state,
        AdminState.full_orders_report_by_period.state,
        AdminState.full_earned_report_by_date.state,
        AdminState.full_earned_report_by_period.state,
        AdminState.change_interval.state,
        AdminState.change_support_link.state,
        AdminState.change_radius_km.state,
        AdminState.choose_order.state,
        AdminState.choose_user_by_ID.state,
        AdminState.choose_courier_by_ID.state,
        AdminState.choose_partner_by_SEED.state,
        AdminState.mailing_users.state,
        AdminState.mailing_couriers.state,
        AdminState.mailing_partners.state,
        AdminState.add_XP.state,
        AdminState.change_max_orders_count.state,
    ):
        if event.text in RESTRICTED_COMMANDS:
            await fsm_context.set_state(AdminState.default.state)
            await asyncio.sleep(0.3)
            new_state = await fsm_context.get_state()
            log.info(f"new state: {new_state}")
            return await handler(event, data)

    return await handler(event, data)


__all__ = ["AdminOuterMiddleware"]
