import asyncio

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.enums import ContentType
from aiogram import filters

from app.u_pack.u_middlewares import InnerMiddleware, OuterMiddleware
from app.u_pack.u_states import UserState
from app.u_pack.u_kb import get_user_kb
from app.u_pack.u_voice_to_text import process_audio_data
from app.u_pack.u_ai_assistant import process_order_text, get_parsed_addresses
from app.common.coords_and_price import get_coordinates, calculate_osrm_route, get_price

from app.common.message_handler import MessageHandler
from app.common.titles import get_image_title_user

from app.database.requests import user_data, order_data

from datetime import datetime
import pytz

# ------------------------------------------------------------------------------------------------------------------- #

users_router = Router()

# middleware_Outer
users_router.message.outer_middleware(OuterMiddleware())
users_router.callback_query.outer_middleware(OuterMiddleware())

# middleware_Inner
users_router.message.middleware(InnerMiddleware())
users_router.callback_query.middleware(InnerMiddleware())


# ------------------------------------------------------------------------------------------------------------------- #

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
        text = ("▼ <b>Выберите действие в меню</b>")
        new_message = await message.answer(text)
        await handler.handle_new_message(new_message, message)
        return
    else:
        await user_data.set_user(message.from_user.id)
        await handler.delete_previous_message(message.chat.id)
        photo_title = await get_image_title_user("/start")
        text = (f"Ракета — это современный сервис доставки, предлагающий минимальные цены и удобство использования.\n\n"
                f"Почему выбирают Нас?\n\n"
                f"◉ Самые низкие цены:\n"
                f"Наши пешие курьеры обнаруживаются в радиусе вашего заказа, "
                f"что снижает стоимость и ускоряет доставку.\n\n"
                f"◉ Удобство и простота:\n"
                f"Оформление заказа с нами — это быстро и легко благодаря технологиям искусственного интеллекта, "
                f"которые позволяют мгновенно создать заказ и отправить его на выполнение.")
        reply_kb = await get_user_kb(message)

        new_message = await message.answer_photo(photo=photo_title,
                                                 caption=text,
                                                 reply_markup=reply_kb,
                                                 parse_mode="HTML",
                                                 disable_notification=True)
        await handler.handle_new_message(new_message, message)


# registration
@users_router.callback_query(F.data == "reg")
async def data_next_user(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.set_Name)
    handler = MessageHandler(state, callback_query.bot)
    # text = "Пройдите небольшую регистрацию, это не займет много времени.\n\n"
    # await callback_query.answer(text, show_alert=True)
    text = ("Пройдите небольшую регистрацию.\n"
            "Это не займет много времени.\n\n"
            "<b>Как вас зовут?</b>")
    new_message = await callback_query.message.answer(text, disable_notification=True, parse_mode="HTML")
    await handler.handle_new_message(new_message, callback_query.message)


# registration_Name
@users_router.message(filters.StateFilter(UserState.set_Name))
async def data_email_user(message: Message, state: FSMContext):
    await state.set_state(UserState.set_Phone)
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)

    tg_id = message.from_user.id
    name = message.text

    await user_data.set_user_name(tg_id, name)
    reply_kb = await get_user_kb(text="phone_number")
    text = (f"Привет, {name}!👋\n\nЧтобы мы могли быстро оформить заказ и курьер смог связаться с вами "
            f"в случае необходимости, пожалуйста, укажите ваш номер телефона.\n\n"
            f"<b>Ваш номер:</b>")
    msg = await message.answer(text, disable_notification=True, reply_markup=reply_kb, parse_mode="HTML")
    await handler.handle_new_message(msg, message)


# registration_Phone
@users_router.message(filters.StateFilter(UserState.set_Phone))
async def data_phone_user(message: Message, state: FSMContext):
    await state.set_state(UserState.zero)
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)

    tg_id = message.from_user.id
    phone = message.contact.phone_number

    await user_data.set_user_phone(tg_id, phone)
    name, phone_number = await user_data.get_user_info(tg_id)
    text = (f"Вы успешно зарегистрировались! 🎉\n\n"
            f"Имя: {name}\n"
            f"Номер: {phone_number}\n\n▼ <b>Выберите действие в меню</b>")
    msg = await message.answer(text, disable_notification=True, parse_mode="HTML")
    await handler.handle_new_message(msg, message)


# ------------------------------------------------------------------------------------------------------------------- #


# commands_Order
@users_router.message(F.text == "/order")
async def cmd_order(message: Message, state: FSMContext):
    data = await state.get_data()
    read_info = data.get("read_info", False)  # Извлекаем флаг или устанавливаем False по умолчанию

    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)

    if not read_info:
        # Отправляем инструкцию пользователю
        photo_title = await get_image_title_user(message.text)
        text = ("◉ Вы можете сделать заказ с помощью текста или голоса, "
                "и наш ИИ ассистент быстро его обработает и передаст курьеру.\n\n"
                "◉ При записи голосового сообщения или набора текста описывайте заказ так, как вам удобно, "
                "ассистент создаст заявку для вашего заказа.")
        reply_kb = await get_user_kb(message)

        new_message = await message.answer_photo(photo=photo_title,
                                                 caption=text,
                                                 reply_markup=reply_kb,
                                                 disable_notification=True)
        # Обновляем флаг, чтобы больше не показывать инструкцию
        await state.update_data(read_info=True)
        # Устанавливаем нужный стейт для дальнейшего использования
        await state.set_state(UserState.ai_voice_order)

    else:
        # Если инструкция уже была показана, сразу переходим к процессу заказа
        text = ("◉ Укажите в описании к заказу:\n\n"
                "Город:\n"
                "Адрес 1: Откуда забрать заказ.\n"
                "Адрес 2: Куда доставить заказ.\n"
                "Предмет доставки:\n"
                "Имя получателя:\n"
                "Номер получателя:\n"
                "Комментарии курьеру:\n\n"
                "*Вы можете отрпвить как голосовое сообщение так и текстовое, "
                "заказ будет оформлен в считанные секунды.")

        new_message = await message.answer(text=f"{text}\n\nゞ <b>Опишите ваш заказ ...</b>",
                                           disable_notification=True,
                                           parse_mode="HTML")
        # Вновь устанавливаем стейт для корректной работы хендлера
        await state.set_state(UserState.ai_voice_order)

    # Обрабатываем новое сообщение
    await handler.handle_new_message(new_message, message)


# commands_Profile
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


# commands_BecomeCourier
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


# read_Info
@users_router.callback_query(F.data == "ai_order")
async def data_ai(callback_query: CallbackQuery, state: FSMContext):
    # Устанавливаем флаг прочитанной информации
    await state.update_data(read_info=True)
    # Устанавливаем нужный стейт
    await state.set_state(UserState.ai_voice_order)

    handler = MessageHandler(state, callback_query.bot)
    text = ("◉ Укажите в описании к заказу:\n\n"
            "Город:\n"
            "Адрес 1: Откуда забрать заказ.\n"
            "Адрес 2: Куда доставить заказ.\n"
            "Предмет доставки:\n"
            "Имя получателя:\n"
            "Номер получателя:\n"
            "Комментарии курьеру:\n\n"
            "*Вы можете отрпвить как голосовое сообщение так и текстовое, "
            "заказ будет оформлен в считанные секунды.")

    new_message = await callback_query.message.answer(text=f"{text}\n\nゞ <b>Опишите ваш заказ ...</b>",
                                                      disable_notification=True,
                                                      parse_mode="HTML")
    await handler.handle_new_message(new_message, callback_query.message)


# ------------------------------------------------------------------------------------------------------------------- #


# form_Order
@users_router.message(
    filters.StateFilter(UserState.ai_voice_order),
    F.content_type.in_([ContentType.VOICE, ContentType.TEXT])
)
async def process_message(message: Message, state: FSMContext):
    await state.set_state(UserState.waiting_Courier)
    wait_message = await message.answer("Заказ обрабатывается, подождите ...")
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)

    # Инициализация переменных
    reply_kb = await get_user_kb(text="voice_order_accept")
    moscow_time = datetime.now(pytz.timezone("Europe/Moscow")).replace(tzinfo=None, microsecond=0)
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
            delivery_object = structured_data.get('Delivery object')
            receiver_name = structured_data.get('Receiver name')
            receiver_phone = structured_data.get('Receiver phone')
            order_details = structured_data.get('Order details', None)
            comments = structured_data.get('Comments', None)
            price = await get_price(distance, moscow_time)
            price_text = f"{price}₽"

            await state.update_data(
                city=city,
                starting_point_a=starting_point_a,
                a_latitude=float(pickup_coords[0]),
                a_longitude=float(pickup_coords[1]),
                a_coordinates=pickup_coords,
                a_url=pickup_point,
                destination_point_b=destination_point_b,
                b_latitude=float(delivery_coords[0]),
                b_longitude=float(delivery_coords[1]),
                b_coordinates=delivery_coords,
                b_url=delivery_point,
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
                order_time=moscow_time,
                yandex_maps_url=yandex_maps_url,
                pickup_point=pickup_point,
                delivery_point=delivery_point,
            )

            order_forma = (
                # f"Оформлен: {order_time}\n"
                f"Ваш заказ ✍︎\n"
                f"---------------------------------------------\n"
                f"Город: {city}\n"
                f"⦿ Адрес 1: <a href='{pickup_point}'>{starting_point_a}</a>\n"
                f"⦿ Адрес 2: <a href='{delivery_point}'>{destination_point_b}</a>\n\n"
                f"Предмет доставки: {delivery_object}\n\n"
                f"Имя отправителя: {sender_name}\n"
                f"Номер отправителя: {sender_phone}\n"
                f"Имя получателя: {receiver_name}\n"
                f"Номер получателя: {receiver_phone}\n\n"
                f"Расстояние: {distance_text}\n"
                f"Время доставки ≈ {duration_text}\n\n"
                f"Оплата: {price_text}\n\n"
                f"Комментарии курьеру: {comments}\n"
                f"---------------------------------------------\n"
                f"* Проверьте ваш заказ и если все верно, то разместите. "
                f"Подождите немного, пока найдется свободный курьер.\n\n"
                f"* Курьер может связаться с вами для уточнения деталей!\n\n"
                # f"⦿ <a href='{pickup_point}'>Забрать отсюда</a>\n\n"
                # f"⦿ <a href='{delivery_point}'>Доставить сюда</a>\n\n"
                f"⦿⌁⦿ <a href='{yandex_maps_url}'>Маршрут</a>\n\n"

            )

            # Отправка итогового сообщения
            new_message = await message.answer(text=order_forma, reply_markup=reply_kb, disable_notification=True,
                                               parse_mode="HTML")
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


# send_Order
@users_router.callback_query(F.data == "order_sent")
async def set_order_to_DB(callback_query: CallbackQuery, state: FSMContext):
    # Устанавливаем состояние
    await state.set_state(UserState.waiting_Courier)

    # Создаем обработчик сообщений
    handler = MessageHandler(state, callback_query.bot)

    # Получаем ID пользователя
    tg_id = callback_query.from_user.id
    data = await state.get_data()
    await state.set_state(UserState.zero)

    try:
        # Асинхронно создаем заказ
        await order_data.create_order(tg_id, data)
    except Exception as e:
        # Обработка возможных ошибок
        print(f"Ошибка при создании заказа: {str(e)}")

    # Отправляем уведомление пользователю
    text = (
        "Заказ успешно создан! 🎉\n"
        "Мы ищем курьера для вашего заказа 🔎\n\n"
        "Все ваши заказы и их статус можно отслеживать в вашем профиле, в разделе '<b>Мои заказы</b>'.\n"
        "☟"
    )
    new_message = await callback_query.message.answer(text, disable_notification=True, parse_mode="HTML")

    # Обрабатываем новое сообщение
    await handler.handle_new_message(new_message, callback_query.message)
    # await state.clear()


# ------------------------------------------------------------------------------------------------------------------- #


# test
@users_router.message(F.text == "/test")
async def send_welcome(message: Message, state: FSMContext):
    handler = MessageHandler(state, message.bot)
    my_tg_id = message.from_user.id
    my_lon = 37.483554  # пример координат курьера
    my_lat = 55.680241  # пример координат курьера
    available_orders = await order_data.get_available_orders(my_tg_id, my_lat, my_lon, radius_km=5)

    # Формируем список заказов для отображения
    orders = []
    for order in available_orders:
        order_forma = (
            f"Заказ №{order.order_id}\n"
            f"Дата оформления: {order.created_at}\n"
            f"---------------------------------------------\n"
            f"Город: {order.order_city}\n"
            f"⦿ Адрес 1: <a href='{order.a_url}'>{order.starting_point_a}</a>\n"
            f"⦿ Адрес 2: <a href='{order.b_url}'>{order.destination_point_b}</a>\n\n"
            f"Предмет доставки: {order.delivery_object}\n\n"
            f"Имя отправителя: {order.sender_name}\n"
            f"Номер отправителя: {order.sender_phone}\n\n"
            f"Имя получателя: {order.receiver_name}\n"
            f"Номер получателя: {order.receiver_phone}\n\n"
            f"Оплата: {order.price_rub}₽\n"
            f"---------------------------------------------\n"
            f"Комментарии: {order.comments}\n\n"
            f"⦿⌁⦿ <a href='{order.full_rout}'>Маршрут</a>\n\n"
        )
        orders.append(order_forma)

    # Если заказов нет
    if not orders:
        await handler.delete_previous_message(message.chat.id)
        new_message = await message.answer("Нет доступных заказов в вашем радиусе.")
        await handler.handle_new_message(new_message, message)
        return

    await state.set_state(UserState.testOrders)
    await handler.delete_previous_message(message.chat.id)

    # Устанавливаем начальный заказ и сохраняем его
    counter = 0
    await state.update_data(orders=orders, counter=counter)

    reply_kb = await get_user_kb(message)  # Клавиатура с кнопками для переключения заказов
    new_message = await message.answer(orders[counter], reply_markup=reply_kb, parse_mode="HTML")

    await handler.handle_new_message(new_message, message)


# Обработчик кнопки "⇥" для перехода вперёд
@users_router.callback_query(F.data == "next_right")
async def on_button_next(callback_query: CallbackQuery, state: FSMContext):
    handler = MessageHandler(state, callback_query.bot)
    await state.set_state(UserState.testOrders)
    data = await state.get_data()
    orders = data.get("orders")
    counter = data.get("counter", 0)

    # Увеличиваем счётчик и зацикливаем его
    counter = (counter + 1) % len(orders)

    # Обновляем состояние с новым значением счётчика
    await state.update_data(counter=counter)

    # Обновляем сообщение с новым заказом
    await callback_query.message.edit_text(orders[counter],
                                           reply_markup=callback_query.message.reply_markup,
                                           parse_mode="HTML")

    # await handler.handle_new_message(new_message, callback_query.message)


# Обработчик кнопки "⇤" для перехода назад
@users_router.callback_query(F.data == "back_left")
async def on_button_back(callback_query: CallbackQuery, state: FSMContext):
    handler = MessageHandler(state, callback_query.bot)
    await state.set_state(UserState.testOrders)
    data = await state.get_data()
    orders = data.get("orders")
    counter = data.get("counter", 0)

    # Уменьшаем счётчик и зацикливаем его
    counter = (counter - 1) % len(orders)

    # Обновляем состояние с новым значением счётчика
    await state.update_data(counter=counter)

    # Обновляем сообщение с новым заказом
    await callback_query.message.edit_text(
        orders[counter],
        reply_markup=callback_query.message.reply_markup,
        parse_mode="HTML"
    )

    # await handler.handle_new_message(new_message, callback_query.message)

# ------------------------------------------------------------------------------------------------------------------- #
