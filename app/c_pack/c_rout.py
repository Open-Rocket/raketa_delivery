import asyncio

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.enums import ContentType
from aiogram import filters

from app.c_pack.c_middlewares import OuterMiddleware, InnerMiddleware
from app.c_pack.c_states import CourierState
from app.common.message_handler import MessageHandler
from app.common.titles import get_image_title_courier
from app.common.titles import get_image_title_courier
from app.c_pack.c_kb import get_courier_kb

from app.database.requests import courier_data

from datetime import datetime

couriers_router = Router()

couriers_router.message.outer_middleware(OuterMiddleware())
couriers_router.callback_query.outer_middleware(OuterMiddleware())

couriers_router.message.middleware(InnerMiddleware())
couriers_router.callback_query.middleware(InnerMiddleware())


# start

@couriers_router.message(CommandStart())
async def cmd_start_courier(message: Message, state: FSMContext) -> None:
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)
    photo_title = await get_image_title_courier("/start")
    text = (
        "Ракета — это новый, современный сервис доставки, созданный для того, "
        "чтобы курьеры могли работать свободно и зарабатывать больше. "
        "С нами вы сами управляете своими доходами без скрытых комиссий и сложных условий.\n\n"
        "Почему стоит выбрать Нас?\n\n"
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
    await courier_data.set_courier(message.from_user.id)


# registration

@couriers_router.callback_query(F.data == "next")
async def data_next_user(callback_query: CallbackQuery, state: FSMContext):
    handler = MessageHandler(state, callback_query.bot)
    await state.set_state(CourierState.state_Name)
    text = "Пройдите небольшую регистрацию, это не займет много времени.\n\nКак вас зовут?"
    new_message = await callback_query.message.answer(text, disable_notification=True)
    await handler.handle_new_message(new_message, callback_query.message)


@couriers_router.message(filters.StateFilter(CourierState.state_Name))
async def data_name_user(message: Message, state: FSMContext):
    await state.set_state(CourierState.state_email)
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)
    tg_id = message.from_user.id
    name = message.text
    await courier_data.set_courier_name(tg_id, name)
    text = f"Спасибо {name}\nТеперь введите ваш email:"
    new_message = await message.answer(text, disable_notification=True)
    await handler.handle_new_message(new_message, message)


@couriers_router.message(filters.StateFilter(CourierState.state_email))
async def data_email_user(message: Message, state: FSMContext):
    await state.set_state(CourierState.state_Phone)
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)

    tg_id = message.from_user.id
    email = message.text

    # Сохраняем email пользователя в БД
    await courier_data.set_courier_email(tg_id, email)
    reply_kb = await get_courier_kb(text="phone_number")
    text = ("Последний шаг!\n\n"
            "Ваш номер телефона:")
    msg = await message.answer(text, disable_notification=True, reply_markup=reply_kb)
    await handler.handle_new_message(msg, message)


@couriers_router.message(filters.StateFilter(CourierState.state_Phone))
async def data_phone_user(message: Message, state: FSMContext):
    await state.set_state(CourierState.zero)
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)

    tg_id = message.from_user.id
    phone = message.contact.phone_number

    # Сохраняем email пользователя в БД
    await courier_data.set_courier_phone(tg_id, phone)
    name, email, phone_number = await courier_data.get_courier_info(tg_id)
    text = (f"Вы успешно зарегистрировались!\n\n"
            f"Имя: {name}\n"
            f"Почта: {email}\n"
            f"Номер: {phone_number}\n\n▼ Выберите действие в меню")
    msg = await message.answer(text, disable_notification=True)
    await handler.handle_new_message(msg, message)


# commands

@couriers_router.message(F.text == "/run")
async def cmd_run(message: Message, state: FSMContext):
    await state.set_state(CourierState.run_state)
    await asyncio.sleep(0)
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)
    photo_title = await get_image_title_courier(message.text)
    text = ("Отправьте свою локацию 🧭")
    reply_kb = await get_courier_kb(message)
    await asyncio.sleep(0)

    new_message = await message.answer_photo(photo=photo_title, caption=text, reply_markup=reply_kb)
    await handler.handle_new_message(new_message, message)


# callbacks


# Location

@couriers_router.message(F.content_type == ContentType.LOCATION)
async def get_location(message: Message, state: FSMContext):
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)
    caption_message = await message.answer("Мы ищем заказы поблизости 🔎\n\n")
    # location_message = await message.answer_location(latitude=message.location.latitude,
    #                                                  longitude=message.location.longitude,
    #                                                  disable_notification=True)

    # await handler.update_previous_message_ids(
    #     [location_message.message_id, caption_message.message_id])
    await handler.handle_new_message(caption_message, message)
    await message.delete()
