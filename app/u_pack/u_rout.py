import asyncio

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.enums import ContentType
from aiogram import filters

from app.u_pack.u_middlewares import AdminPasswordAcception, InnerMiddleware, OuterMiddleware
from app.u_pack.u_states import UserState
from app.u_pack.u_kb import get_user_kb
from app.u_pack.u_voice_to_text import process_audio_data
from app.u_pack.u_ai_assistant import process_order_text, get_parsed_addresses, get_city
from app.u_pack.u_coordinates import get_coordinates, calculate_osrm_route, get_price

from app.common.message_handler import MessageHandler
from app.common.titles import get_image_title_user

from app.database.requests import set_user, get_users, set_username, set_user_email, set_user_phone, get_user_info

from datetime import datetime

users_router = Router()
admins_router_pass = Router()

users_router.message.outer_middleware(OuterMiddleware())
users_router.callback_query.outer_middleware(OuterMiddleware())

users_router.message.middleware(InnerMiddleware())
users_router.callback_query.middleware(InnerMiddleware())

admins_router_pass.message.middleware(AdminPasswordAcception())


# start


@users_router.message(CommandStart())
async def cmd_start_user(message: Message, state: FSMContext) -> None:
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)
    photo_title = await get_image_title_user("/start")
    text = ("Ракета — это новый, современный сервис доставки, созданный для вашего комфорта. "
            "Мы используем технологии искусственного интеллекта, "
            "чтобы обеспечить максимально удобное оформление и отслеживание заказов.\n\n"
            "Почему стоит выбрать Нас?\n\n"
            "◉ Низкие цены:\n"
            "Самые низкие цены и полная свобода выбора! Вы всегда видите доступные заказы и выбираете тех курьеров, "
            "кто наиболее подходит вашим требованиям по времени и местоположению.\n\n"
            "◉ Максимальное удобство:\n"
            "Простой и понятный интерфейс, быстрая обработка заказов и никаких сложностей. "
            "С Ракетой вы получаете доставку тогда, когда вам нужно, без лишних ожиданий.\n\n"
            "Ракета — это ваша гарантия доступной и быстрой доставки. Присоединяйтесь и ощутите, "
            "как легко и удобно пользоваться современным сервисом!")
    reply_kb = await get_user_kb(message)

    new_message = await message.answer_photo(photo=photo_title,
                                             caption=text,
                                             reply_markup=reply_kb,
                                             disable_notification=True)
    await handler.handle_new_message(new_message, message)
    await set_user(message.from_user.id)


# registration

@users_router.callback_query(F.data == "next")
async def data_next_user(callback_query: CallbackQuery, state: FSMContext):
    handler = MessageHandler(state, callback_query.bot)
    await state.set_state(UserState.state_Name)
    text = "Пройдите небольшую регистрацию, это не займет много времени.\n\nКак вас зовут?"
    new_message = await callback_query.message.answer(text, disable_notification=True)
    await handler.handle_new_message(new_message, callback_query.message)


@users_router.message(filters.StateFilter(UserState.state_Name))
async def data_name_user(message: Message, state: FSMContext):
    await state.set_state(UserState.state_email)
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)
    tg_id = message.from_user.id
    name = message.text
    await set_username(tg_id, name)
    text = f"Спасибо {name}\nТеперь введите ваш email:"
    new_message = await message.answer(text, disable_notification=True)
    await handler.handle_new_message(new_message, message)


@users_router.message(filters.StateFilter(UserState.state_email))
async def data_email_user(message: Message, state: FSMContext):
    await state.set_state(UserState.state_Phone)
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)

    tg_id = message.from_user.id
    email = message.text

    # Сохраняем email пользователя в БД
    await set_user_email(tg_id, email)
    reply_kb = await get_user_kb(text="phone_number")
    text = ("Последний шаг!\n\n"
            "Ваш номер телефона:")
    msg = await message.answer(text, disable_notification=True, reply_markup=reply_kb)
    await handler.handle_new_message(msg, message)


@users_router.message(filters.StateFilter(UserState.state_Phone))
async def data_phone_user(message: Message, state: FSMContext):
    await state.set_state(UserState.zero)
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)

    tg_id = message.from_user.id
    phone = message.contact.phone_number

    # Сохраняем email пользователя в БД
    await set_user_phone(tg_id, phone)
    name, email, phone_number = await get_user_info(tg_id)
    text = (f"Вы успешно зарегистрировались!\n\n"
            f"Имя: {name}\n"
            f"Почта: {email}\n"
            f"Номер: {phone_number}\n\n▼ Выберите действие в меню")
    msg = await message.answer(text, disable_notification=True)
    await handler.handle_new_message(msg, message)


# commands


@users_router.message(F.text == "/order")
async def cmd_order(message: Message, state: FSMContext):
    await asyncio.sleep(0)
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)
    photo_title = await get_image_title_user(message.text)
    text = ("• Вы можете сделать заказ с помощью текста или голоса, "
            "и наш ИИ ассистент быстро его обработает его и передаст курьеру.\n\n"
            "• При записи голосового сообщения или набора текста описывайте заказ так как вам удобно, "
            "ассистент создаст заявку для вашего заказа.")
    reply_kb = await get_user_kb(message)
    await asyncio.sleep(0)

    new_message = await message.answer_photo(photo=photo_title, caption=text, reply_markup=reply_kb)
    await handler.handle_new_message(new_message, message)


@users_router.message(F.text == "/profile")
async def cmd_p_customer(message: Message, state: FSMContext):
    await state.set_state(UserState.state_Profile)
    await asyncio.sleep(0)
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)
    tg_id = message.from_user.id
    photo_title = await get_image_title_user(message.text)
    name, email, phone_number = await get_user_info(tg_id)

    text = (f"Имя: {name} \n"
            f"Почта: {email}\n"
            f"Номер: {phone_number}")
    reply_kb = await get_user_kb(message=message)
    await asyncio.sleep(0)

    new_message = await message.answer_photo(photo=photo_title,
                                             caption=text,
                                             reply_markup=reply_kb,
                                             disable_notification=True)
    await handler.handle_new_message(new_message, message)


@users_router.message(F.text == "/ai")
async def cmd_ai(message: Message, state: FSMContext):
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)
    photo_title = await get_image_title_user(message.text)
    reply_kb = await get_user_kb(message)
    await asyncio.sleep(0)

    new_message = await message.answer_photo(photo=photo_title, reply_markup=reply_kb)
    await handler.handle_new_message(new_message, message)


@users_router.message(F.text == "/help")
async def cmd_help(message: Message, state: FSMContext):
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)
    await asyncio.sleep(0)

    text = ("/order — Оформить доставку. C помощью голоса или вручную.\n"
            "/profile — Просмотр и редактирование профиля.\n"
            "/ai — Взаимодействие с ИИ ассистентом для поддержки и оформления заказов.\n"
            "/rules — Ознакомление с правилами использования сервиса."
            "/become_courier - Станьте курьером и зарабатывайте.")

    new_message = await message.answer(text, disable_notification=True)
    await handler.handle_new_message(new_message, message)


@users_router.message(F.text == "/become_courier")
async def cmd_become_courier(message: Message, state: FSMContext):
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)
    photo_title = await get_image_title_user("/become_courier")
    reply_kb = await get_user_kb(message)
    new_message = await message.answer_photo(photo=photo_title, reply_markup=reply_kb)

    await handler.handle_new_message(new_message, message)


# callbacks


@users_router.callback_query(F.data == "ai_order")
async def data_ai(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.ai_voice_order)
    handler = MessageHandler(state, callback_query.bot)
    example_text = ("• Укажите в описании к заказу:\n"
                    "Город,адреса, что доставляем, имя и номер получателя, кто оплатит заказ.")
    new_message = await callback_query.message.answer(text=f"{example_text}\n\nゞ Опишите ваш заказ ...",
                                                      disable_notification=True)
    await handler.handle_new_message(new_message, callback_query.message)


@users_router.callback_query(F.data == "make_order")
async def data_order(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.order_state)
    await asyncio.sleep(0)
    handler = MessageHandler(state, callback_query.bot)
    photo_title = await get_image_title_user("/order")
    text = ("☞ Вы можете сделать заказ с помощью голоса, "
            "и наш ИИ помощник быстро обработает его и передаст курьеру.\n\n"
            "☞ Если предпочитаете, можете оформить заказ Вручную, "
            "просто указав нужные адреса.\n\n"
            "⚙︎ Убедитесь, что ваш профиль клиента заполнен.")
    reply_kb = await get_user_kb(callback_data=callback_query.data)
    await asyncio.sleep(0)
    new_message = await callback_query.message.answer_photo(photo=photo_title,
                                                            caption=text,
                                                            reply_markup=reply_kb,
                                                            disable_notification=True)
    await handler.handle_new_message(new_message, callback_query.message)


# ai_order

@users_router.message(filters.StateFilter(UserState.ai_voice_order),
                      F.content_type.in_([ContentType.VOICE, ContentType.TEXT]))
async def process_message(message: Message, state: FSMContext):
    wait_message = await message.answer("Сообщение обрабатывается, подождите немного ...")
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)
    reply_kb = await get_user_kb(text="voice_order_accept")
    new_message = "Заказ не было обработан ..."
    order_time = datetime.now().replace(microsecond=0)

    if message.content_type == ContentType.VOICE:
        voice = message.voice
        file_info = await message.bot.get_file(voice.file_id)
        file = await message.bot.download_file(file_info.file_path)
        audio_data = file.read()
        recognized_text = await process_audio_data(audio_data)
    else:
        recognized_text = message.text

    if not recognized_text:
        recognized_text = "Ошибка распознавания. Попробуйте снова."
        structured_text = recognized_text
    else:
        # Отправляем текст в OpenAI для обработки
        addresses = await get_parsed_addresses(recognized_text)

        # Проверяем, что ИИ вернул два адреса
        if len(addresses) == 2:
            pickup_address, delivery_address = addresses

            # Получаем координаты для адресов
            pickup_latitude, pickup_longitude = await get_coordinates(pickup_address)
            delivery_latitude, delivery_longitude = await get_coordinates(delivery_address)

            if pickup_latitude and pickup_longitude and delivery_latitude and delivery_longitude:
                yandex_maps_url = (
                    f"https://yandex.ru/maps/?rtext={pickup_latitude},{pickup_longitude}~{delivery_latitude},{delivery_longitude}&rtt=auto")
                pickup_point = (
                    f"https://yandex.ru/maps/?ll={pickup_longitude},{pickup_latitude}&pt={pickup_longitude},{pickup_latitude}&z=14")
                delivery_point = (
                    f"https://yandex.ru/maps/?ll={delivery_longitude},{delivery_latitude}&pt={delivery_longitude},{delivery_latitude}&z=14")
                distance, duration = await calculate_osrm_route(pickup_latitude, pickup_longitude, delivery_latitude,
                                                                delivery_longitude)
                duration_text = f"{(duration - duration % 60) // 60} часов {duration % 60} минут."
                city_order = await get_city(recognized_text)
                price = await get_price(distance, order_time, city_order)
                structured_text = await process_order_text(recognized_text, distance, duration_text, price)

                new_message = await message.answer(
                    text=(f"Ваш заказ ✍︎\n"
                          f"---------------------------------------------\n"
                          f"Дата/Время: {order_time}\n\n"
                          f"{structured_text}\n"
                          f"---------------------------------------------\n\n"
                          f"* Проверьте ваш заказ и если все верно, то разместите. "
                          f"Подождите немного пока найдется свободный курьер и откликнется на него.\n\n"
                          f"* Курьер может связатсья с вами для уточнения деталей!\n\n"
                          f"Вот ссылка на маршрут в Яндекс.Картах:\n{yandex_maps_url}\n\n"
                          f"Откуда забрать:\n{pickup_point}\n\n"
                          f"Куда отвезти:\n{delivery_point}\n\n"),
                    reply_markup=reply_kb, disable_notification=True
                )
            else:
                new_message = await message.answer(
                    text=f"Ваш заказ ✍︎\n\n{recognized_text} \n\n"
                         f"Проверьте ваш заказ и если все верно, то разместите его "
                         f"и ждите ответа от курьера.",
                    reply_markup=reply_kb, disable_notification=True
                )
        else:
            new_message = await message.answer(
                text=f"Ваш заказ ✍︎\n\n{recognized_text} \n\n"
                     f"Проверьте ваш заказ и если все верно, то разместите его "
                     f"и ждите ответа от курьера.",
                reply_markup=reply_kb, disable_notification=True
            )

    await wait_message.delete()
    await handler.handle_new_message(new_message, message)
    await state.set_state(UserState.order_state)
