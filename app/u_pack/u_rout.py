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
from app.u_pack.u_ai_assistant import process_order_text, get_parsed_addresses
from app.common.coords_and_price import get_coordinates, calculate_osrm_route, get_price

from app.common.message_handler import MessageHandler
from app.common.titles import get_image_title_user

from app.database.requests import user_data, order_data

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
    await state.set_state(UserState.regstate)
    handler = MessageHandler(state, message.bot)
    user = await user_data.get_username_userphone(message.from_user.id)
    user_name, user_phone = user

    # Если пользователь уже зарегистрирован
    if user_name and user_phone:
        await state.set_state(UserState.zero)
        await handler.delete_previous_message(message.chat.id)
        text = ("▼ Выберите действие в меню")
        new_message = await message.answer(text)
        await handler.handle_new_message(new_message, message)
        return
    else:
        await user_data.set_user(message.from_user.id)
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


# registration

@users_router.callback_query(F.data == "reg")
async def data_next_user(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.set_Name)
    handler = MessageHandler(state, callback_query.bot)
    text = "Пройдите небольшую регистрацию, это не займет много времени.\n\n"
    await callback_query.answer(text, show_alert=True)
    new_message = await callback_query.message.answer("Как вас зовут?", disable_notification=True)
    await handler.handle_new_message(new_message, callback_query.message)


@users_router.message(filters.StateFilter(UserState.set_Name))
async def data_email_user(message: Message, state: FSMContext):
    await state.set_state(UserState.set_Phone)
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)

    tg_id = message.from_user.id
    name = message.text

    await user_data.set_user_name(tg_id, name)
    reply_kb = await get_user_kb(text="phone_number")
    text = ("Ваш номер телефона:")
    msg = await message.answer(text, disable_notification=True, reply_markup=reply_kb)
    await handler.handle_new_message(msg, message)


@users_router.message(filters.StateFilter(UserState.set_Phone))
async def data_phone_user(message: Message, state: FSMContext):
    await state.set_state(UserState.zero)
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)

    tg_id = message.from_user.id
    phone = message.contact.phone_number

    await user_data.set_user_phone(tg_id, phone)
    name, phone_number = await user_data.get_user_info(tg_id)
    text = (f"Вы успешно зарегистрировались!\n\n"
            f"Имя: {name}\n"
            f"Номер: {phone_number}\n\n▼ Выберите действие в меню")
    msg = await message.answer(text, disable_notification=True)
    await handler.handle_new_message(msg, message)


# commands


@users_router.message(F.text == "/order")
async def cmd_order(message: Message, state: FSMContext):
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)
    photo_title = await get_image_title_user(message.text)
    text = ("◉ Вы можете сделать заказ с помощью текста или голоса, "
            "и наш ИИ ассистент быстро его обработает его и передаст курьеру.\n\n"
            "◉ При записи голосового сообщения или набора текста описывайте заказ так как вам удобно, "
            "ассистент создаст заявку для вашего заказа.")
    reply_kb = await get_user_kb(message)
    await asyncio.sleep(0)

    new_message = await message.answer_photo(photo=photo_title,
                                             caption=text,
                                             reply_markup=reply_kb,
                                             disable_notification=True)
    await handler.handle_new_message(new_message, message)


@users_router.message(F.text == "/profile")
async def cmd_profile(message: Message, state: FSMContext):
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)
    tg_id = message.from_user.id
    photo_title = await get_image_title_user(message.text)
    name, phone_number = await user_data.get_user_info(tg_id)

    text = (f"Имя: {name} \n"
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

    new_message = await message.answer_photo(photo=photo_title,
                                             reply_markup=reply_kb,
                                             disable_notification=True)
    await handler.handle_new_message(new_message, message)


# @users_router.message(F.text == "/commands")
# async def cmd_help(message: Message, state: FSMContext):
#     handler = MessageHandler(state, message.bot)
#     await handler.delete_previous_message(message.chat.id)
#     await asyncio.sleep(0)
#
#     text = ("/order — Оформить доставку.\n"
#             "/profile — Ваш профиль.\n"
#             "/become_courier - Станьте курьером и зарабатывайте.\n\n"
#             )
#
#     new_message = await message.answer(text, disable_notification=True)
#     await handler.handle_new_message(new_message, message)


@users_router.message(F.text == "/become_courier")
async def cmd_become_courier(message: Message, state: FSMContext):
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)
    photo_title = await get_image_title_user("/become_courier")
    reply_kb = await get_user_kb(message)
    new_message = await message.answer_photo(photo=photo_title,
                                             reply_markup=reply_kb,
                                             disable_notification=True)

    await handler.handle_new_message(new_message, message)


# callbacks


@users_router.callback_query(F.data == "ai_order")
async def data_ai(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.ai_voice_order)
    handler = MessageHandler(state, callback_query.bot)
    example_text = ("◉ Укажите в описании к заказу:\n"
                    "Город,адреса, что доставляем, имя и номер получателя, кто оплатит заказ.")
    new_message = await callback_query.message.answer(text=f"{example_text}\n\nゞ Опишите ваш заказ ...",
                                                      disable_notification=True)
    await handler.handle_new_message(new_message, callback_query.message)


# ai_order


# @users_router.message(filters.StateFilter(UserState.ai_voice_order),
#                       F.content_type.in_([ContentType.VOICE, ContentType.TEXT]))
# async def process_message(message: Message, state: FSMContext):
#     wait_message = await message.answer("Сообщение обрабатывается, подождите немного ...")
#     handler = MessageHandler(state, message.bot)
#     await handler.delete_previous_message(message.chat.id)
#     reply_kb = await get_user_kb(text="voice_order_accept")
#     new_message = "Заказ не было обработан ..."
#     order_time = datetime.now().replace(microsecond=0)
#
#     if message.content_type == ContentType.VOICE:
#         voice = message.voice
#         file_info = await message.bot.get_file(voice.file_id)
#         file = await message.bot.download_file(file_info.file_path)
#         audio_data = file.read()
#         recognized_text = await process_audio_data(audio_data)
#     else:
#         recognized_text = message.text
#
#     if not recognized_text:
#         recognized_text = "Ошибка распознавания. Попробуйте снова."
#         structured_text = recognized_text
#     else:
#         # Отправляем текст в OpenAI для обработки
#         addresses = await get_parsed_addresses(recognized_text)
#
#         # Проверяем, что ИИ вернул два адреса
#         if len(addresses) == 2:
#             pickup_address, delivery_address = addresses
#
#             # Получаем координаты для адресов
#             pickup_latitude, pickup_longitude = await get_coordinates(pickup_address)
#             delivery_latitude, delivery_longitude = await get_coordinates(delivery_address)
#
#             if pickup_latitude and pickup_longitude and delivery_latitude and delivery_longitude:
#                 yandex_maps_url = (
#                     f"https://yandex.ru/maps/?rtext={pickup_latitude},{pickup_longitude}~{delivery_latitude},{delivery_longitude}&rtt=auto")
#                 pickup_point = (
#                     f"https://yandex.ru/maps/?ll={pickup_longitude},{pickup_latitude}&pt={pickup_longitude},{pickup_latitude}&z=14")
#                 delivery_point = (
#                     f"https://yandex.ru/maps/?ll={delivery_longitude},{delivery_latitude}&pt={delivery_longitude},{delivery_latitude}&z=14")
#                 distance, duration = await calculate_osrm_route(pickup_latitude, pickup_longitude, delivery_latitude,
#                                                                 delivery_longitude)
#
#                 tg_id = message.from_user.id
#                 sender_info = await user_data.get_user_info(tg_id)
#
#                 duration_text = f"{(duration - duration % 60) // 60} часов {duration % 60} минут."
#                 city_order = await get_city(recognized_text)
#                 price = await get_price(distance, order_time, city_order)
#                 structured_text = await process_order_text(recognized_text, distance, duration_text, price, sender_info)
#
#                 new_message = await message.answer(
#                     text=(f"Ваш заказ ✍︎\n"
#                           f"---------------------------------------------\n"
#                           f"Дата/Время: {order_time}\n\n"
#                           f"{structured_text}\n"
#                           f"---------------------------------------------\n\n"
#                           f"* Проверьте ваш заказ и если все верно, то разместите. "
#                           f"Подождите немного пока найдется свободный курьер и откликнется на него.\n\n"
#                           f"* Курьер может связатсья с вами для уточнения деталей!\n\n"
#                           f"Вот ссылка на маршрут в Яндекс.Картах:\n{yandex_maps_url}\n\n"
#                           f"Откуда забрать:\n{pickup_point}\n\n"
#                           f"Куда отвезти:\n{delivery_point}\n\n"),
#                     reply_markup=reply_kb, disable_notification=True
#                 )
#             else:
#                 new_message = await message.answer(
#                     text=f"Ваш заказ ✍︎\n\n{recognized_text} \n\n"
#                          f"Проверьте ваш заказ и если все верно, то разместите его "
#                          f"и ждите ответа от курьера.",
#                     reply_markup=reply_kb, disable_notification=True
#                 )
#         else:
#             new_message = await message.answer(
#                 text=f"Ваш заказ ✍︎\n\n{recognized_text} \n\n"
#                      f"Проверьте ваш заказ и если все верно, то разместите его "
#                      f"и ждите ответа от курьера.",
#                 reply_markup=reply_kb, disable_notification=True
#             )
#
#     await wait_message.delete()
#     await handler.handle_new_message(new_message, message)
#     await state.set_state(UserState.waiting_Courier)


# ai order
@users_router.message(
    filters.StateFilter(UserState.ai_voice_order),
    F.content_type.in_([ContentType.VOICE, ContentType.TEXT])
)
async def process_message(message: Message, state: FSMContext):
    await state.set_state(UserState.waiting_Courier)
    wait_message = await message.answer("Сообщение обрабатывается, подождите немного ...")
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)

    # Инициализация переменных
    reply_kb = await get_user_kb(text="voice_order_accept")
    order_time = datetime.now().replace(microsecond=0)
    recognized_text = None

    # Обработка сообщения в зависимости от типа контента
    if message.content_type == ContentType.VOICE:
        voice = message.voice
        file_info = await message.bot.get_file(voice.file_id)
        file = await message.bot.download_file(file_info.file_path)
        audio_data = file.read()
        recognized_text = await process_audio_data(audio_data)
    else:
        recognized_text = message.text

    # Если распознавание не удалось
    if not recognized_text:
        recognized_text = "Ошибка распознавания. Попробуйте снова."
        new_message = await message.answer(recognized_text, reply_markup=reply_kb)
        await wait_message.delete()
        await handler.handle_new_message(new_message, message)
        return

    # Обработка текста через ИИ
    addresses = await get_parsed_addresses(recognized_text)
    if len(addresses) == 2:
        pickup_address, delivery_address = addresses
        # Получаем координаты для адресов
        pickup_coords = await get_coordinates(pickup_address)
        delivery_coords = await get_coordinates(delivery_address)

        if all(pickup_coords) and all(delivery_coords):
            # Формируем маршрут и другие данные
            yandex_maps_url = (
                f"https://yandex.ru/maps/?rtext={pickup_coords[0]},{pickup_coords[1]}"
                f"~{delivery_coords[0]},{delivery_coords[1]}&rtt=auto"
            )
            pickup_point = (
                f"https://yandex.ru/maps/?ll={pickup_coords[1]},{pickup_coords[0]}"
                f"&pt={pickup_coords[1]},{pickup_coords[0]}&z=14"
            )
            delivery_point = (
                f"https://yandex.ru/maps/?ll={delivery_coords[1]},{delivery_coords[0]}"
                f"&pt={delivery_coords[1]},{delivery_coords[0]}&z=14"
            )

            # Расчет расстояния и времени
            tg_id = message.from_user.id
            distance, duration = await calculate_osrm_route(*pickup_coords, *delivery_coords)
            distance_text = f"{distance} км"
            duration_text = f"{(duration - duration % 60) // 60} часов {duration % 60} минут"
            # city_order = await get_city(recognized_text)
            sender_name, sender_phone = await user_data.get_user_info(tg_id)

            # Структурирование данных заказа
            structured_data = await process_order_text(recognized_text)

            # Декомпозиция данных
            city = structured_data.get('City')
            starting_point_a = structured_data.get('Starting point A')
            destination_point_b = structured_data.get('Destination point B')
            destination_point_c = structured_data.get('Destination point C')
            destination_point_d = structured_data.get('Destination point D')
            payer = structured_data.get('Payer')
            delivery_object = structured_data.get('Delivery object')
            receiver_name = structured_data.get('Receiver name')
            receiver_phone = structured_data.get('Receiver phone')
            order_details = structured_data.get('Order details', None)
            comments = structured_data.get('Comments', None)
            price = await get_price(distance, order_time)
            price_text = f"{price}₽"

            await state.update_data(
                city=city,
                destination_point_a=starting_point_a,
                a_latitude=float(pickup_coords[0]),
                a_longitude=float(pickup_coords[1]),
                a_coordinates=pickup_coords,
                a_url=pickup_point,
                destination_point_b=destination_point_b,
                b_latitude=float(delivery_coords[0]),
                b_longitude=float(delivery_coords[1]),
                b_coordinates=delivery_coords,
                b_url=delivery_point,
                destination_point_c=destination_point_c,
                destination_point_d=destination_point_d,
                payer=payer,
                delivery_object=delivery_object,
                sender_name=sender_name,
                sender_phone=sender_phone,
                receiver_name=receiver_name,
                receiver_phone=receiver_phone,
                order_details=order_details,
                comments=comments,
                distance_km=distance,
                duration_min=duration,
                price_rub=price,
                order_time=order_time,
                yandex_maps_url=yandex_maps_url,
                pickup_point=pickup_point,
                delivery_point=delivery_point
            )

            order_forma = (
                f"Оформлен: {order_time}\n"
                f"Ваш заказ ✍︎\n"
                f"---------------------------------------------\n"
                f"Город: {city}\n"
                f"Адрес 1: {starting_point_a}\n"
                f"Адрес 2: {destination_point_b}\n\n"
                f"Предмет доставки: {delivery_object}\n"
                f"Имя отправителя: {sender_name}\n"
                f"Номер отправителя: {sender_phone}\n\n"
                f"Имя получателя: {receiver_name}\n"
                f"Номер получателя: {receiver_phone}\n\n"
                f"Оплатит: {payer}\n"
                f"Комментарии курьеру: {comments}\n\n"
                f"Расстояние: {distance_text}\n"
                f"Время доставки ≈ {duration_text}\n\n"
                f"Оплата: {price_text}\n"
                f"---------------------------------------------\n\n"
                f"* Проверьте ваш заказ и если все верно, то разместите. "
                f"Подождите немного, пока найдется свободный курьер.\n\n"
                f"* Курьер может связаться с вами для уточнения деталей!\n\n"
                f"Ссылка на маршрут в Яндекс.Картах:\n{yandex_maps_url}\n\n"
                f"Откуда забрать:\n{pickup_point}\n\n"
                f"Куда отвезти:\n{delivery_point}\n\n"
            )

            # Отправка итогового сообщения
            new_message = await message.answer(text=order_forma, reply_markup=reply_kb, disable_notification=True)
        else:
            new_message = await message.answer(
                text=f"Ваш заказ ✍︎\n\n{recognized_text}\n\nПроверьте ваш заказ и разместите его, если всё верно.",
                reply_markup=reply_kb, disable_notification=True
            )
    else:
        new_message = await message.answer(
            text=f"Ваш заказ ✍︎\n\n{recognized_text}\n\nПроверьте ваш заказ и разместите его, если всё верно.",
            reply_markup=reply_kb, disable_notification=True
        )

    # Завершение обработки
    await wait_message.delete()
    await handler.handle_new_message(new_message, message)


@users_router.callback_query(F.data == "order_sent")
async def set_order_to_DB(callback_query: CallbackQuery, state: FSMContext):
    # Устанавливаем состояние
    await state.set_state(UserState.waiting_Courier)

    # Создаем обработчик сообщений
    handler = MessageHandler(state, callback_query.bot)

    # Получаем ID пользователя
    tg_id = callback_query.from_user.id
    data = await state.get_data()

    try:
        # Асинхронно создаем заказ
        await order_data.create_order(tg_id, data)
    except Exception as e:
        # Обработка возможных ошибок
        print(f"Ошибка при создании заказа: {str(e)}")

    # Отправляем уведомление пользователю
    text = "Заказ успешно создан!\nИщем курьера 🔎"
    new_message = await callback_query.message.answer(text, disable_notification=True)

    # Обрабатываем новое сообщение
    await handler.handle_new_message(new_message, callback_query.message)


# test
@users_router.message(F.text == "/test")
async def send_welcome(message: Message):
    reply_kb = await get_user_kb(message)
    await message.answer("Это оригинальное сообщение", reply_markup=reply_kb)


@users_router.callback_query(F.data == "press_button")
async def on_button_press(callback_query: CallbackQuery):
    # Отредактируем существующее сообщение
    await callback_query.message.edit_text(
        "Сообщение было обновлено! Но это то же самое сообщение.",
        reply_markup=callback_query.message.reply_markup  # Сохраняем те же кнопки
    )
