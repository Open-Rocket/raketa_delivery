import asyncio

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.enums import ContentType
from aiogram import filters

from app.u_pack.u_middlewares import OuterMiddleware, AdminPasswordAcception, InnerMiddleware
from app.u_pack.u_states import UserState
from app.common.message_handler import MessageHandler
from app.common.titles import get_image_title_courier
from app.common.titles import get_image_title_courier
from app.c_pack.c_kb import get_courier_kb

from app.database.requests import set_user, get_users, set_username, set_user_email, set_user_phone, get_user_info

from datetime import datetime

couriers_router = Router()


@couriers_router.message(CommandStart())
async def cmd_start_courier(message: Message, state: FSMContext) -> None:
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)
    photo_title = await get_image_title_courier("/start")
    text = (
        "Ракета — это новый, современный сервис доставки, созданный для того, "
        "чтобы курьеры могли работать свободно и зарабатывать больше. "
        "С нами вы сами управляете своими доходами без скрытых комиссий и сложных условий.\n\n"
        "Почему стоит выбрать Ракету:\n\n"
        "◉ Подписка:\n"
        "Забудьте про комиссии! Оплачивая подписку, вы получаете полную свободу: выбирайте заказы, "
        "определяйте рабочие часы и сами управляйте своим заработком. "
        "Здесь каждый заказ — это чистая прибыль для вас. Хотите заработать больше? Работайте больше! Всё просто.\n\n"
        "◉ Полная прозрачность:\n"
        "Все заработанные вами деньги — только ваши. Нет ни посредников, ни комиссий, ни штрафов. "
        "Это ваш бизнес, а Ракета помогает вам развивать его так, как вы хотите.\n\n"
        "Ракета — это платформа, где независимость и возможности идут вместе с технологиями. "
        "Работайте на своих условиях и зарабатывайте столько, сколько хотите!")
    reply_kb = await get_courier_kb(message)

    new_message = await message.answer_photo(photo=photo_title,
                                             caption=text,
                                             reply_markup=reply_kb,
                                             disable_notification=True)
    await handler.handle_new_message(new_message, message)
    await set_user(message.from_user.id)
    print(await get_users())
