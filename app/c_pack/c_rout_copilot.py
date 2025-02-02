import os
import asyncio
import logging

from aiogram import Router, F, Bot, filters
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardRemove,
    LabeledPrice,
    PreCheckoutQuery,
)
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.enums import ContentType

from app.c_pack.c_middlewares import OuterMiddleware, InnerMiddleware
from app.c_pack.c_states import CourierState, CourierRegistration
from app.common.message_handler import MessageHandler
from app.common.titles import get_image_title_courier
from app.c_pack.c_kb import get_courier_kb, get_my_orders_kb
from app.database.models import OrderStatus
from app.database.requests import courier_data, order_data, user_data

from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

couriers_router = Router()

couriers_router.message.outer_middleware(OuterMiddleware())
couriers_router.callback_query.outer_middleware(OuterMiddleware())

couriers_router.message.middleware(InnerMiddleware())
couriers_router.callback_query.middleware(InnerMiddleware())

notification_bot = Bot(token=os.getenv("U_TOKEN"))
logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------------------------------------------- #
#                                              ⇣ Registration steps ⇣
# ------------------------------------------------------------------------------------------------------------------- #


# start
@couriers_router.message(CommandStart())
async def cmd_start_courier(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает команду /start для курьеров.

    Эта функция активируется, когда курьер отправляет команду /start.
    - Назначает курьеру начальное состояние регистрации (`CourierState.reg_state`).
    - Отправляет приветственное сообщение, в котором кратко описывается сервис.
    - Предлагает курьеру пройти процесс регистрации.

    Args:
        message (Message): Объект сообщения от пользователя, содержащий команду /start.
        state (FSMContext): Контекст состояния конечного автомата, используемый для управления состояниями пользователя.

    Returns:
        None: Функция не возвращает значение, только отправляет сообщение и устанавливает состояние.
    """

    await state.set_state(CourierState.start_reg)
    handler = MessageHandler(state, message.bot)
    courier = await courier_data.get_courier_info(message.from_user.id)
    courier_name, courier_phone = courier

    # Если курьер уже зарегистрирован
    if courier_name and courier_phone:
        await state.set_state(CourierState.default)
        await handler.delete_previous_message(message.chat.id)
        text = "▼ <b>Выберите действие ...</b>"
        new_message = await message.answer(
            text, parse_mode="HTML", disable_notification=True
        )
        await handler.handle_new_message(new_message, message)
        return
    else:
        await handler.delete_previous_message(message.chat.id)

        # Приветственное сообщение для курьера
        photo_title = await get_image_title_courier("/start")
        text = (
            "Добро пожаловать в Ракету — платформу, которая делает каждого курьера независимым и успешным!\n"
            "Стань частью сообщества, где ты сам управляешь своими доходами и работаешь на своих условиях.\n\n"
            "Почему Ракета?\n\n"
            "◉ <b>Зарабатывай больше</b>: \n"
            "Ты оплачиваешь только подписку и получаешь 100% прибыли с каждого заказа. Чем больше работаешь, тем больше зарабатываешь.\n\n"
            "◉ <b>Свобода выбора</b>: \n"
            "Твоя работа — на твоих условиях. Бери заказы в любое время и работай так, как удобно тебе.\n\n"
            "◉ <b>Прозрачность</b>: \n"
            "Каждый заработанный рубль — твой. Никаких посредников, штрафов и скрытых условий.\n\n"
            "Присоединяйся к Ракете и начинай зарабатывать больше уже сегодня!"
        )
        reply_kb = await get_courier_kb(message)

        new_message = await message.answer_photo(
            photo=photo_title,
            caption=text,
            reply_markup=reply_kb,
            parse_mode="HTML",
            disable_notification=True,
        )
        await handler.handle_new_message(new_message, message)


@couriers_router.callback_query(F.data == "reg")
async def data_reg_courier(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Обрабатывает нажатие на кнопку регистрации курьера.

    После нажатия на кнопку с идентификатором "reg":
    - Переводит пользователя в состояние регистрации (`CourierRegistration.name`).
    - Отправляет сообщение с просьбой ввести имя курьера.

    Args:
        callback_query (CallbackQuery): Объект, содержащий информацию о нажатии на кнопку.
        state (FSMContext): Контекст состояния конечного автомата для управления регистрацией.

    Returns:
        None: Функция не возвращает значение, только отправляет сообщение и изменяет состояние.
    """
    await state.set_state(CourierRegistration.name)
    handler = MessageHandler(state, callback_query.bot)

    text = (
        "Добро пожаловать в Ракету!\n"
        "Чтобы начать, пройдите короткую регистрацию.\n\n"
        "<b>Как вас зовут?</b>"
    )
    new_message = await callback_query.message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )
    await handler.handle_new_message(new_message, callback_query.message)


@couriers_router.message(filters.StateFilter(CourierRegistration.name))
async def data_name_courier(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает состояние курьера после отправки его имени.

    После отправки курьером своего имени:
    - Переводит пользователя в состояние регистрации (`CourierRegistration.phone_number`).
    - Сохраняет в состояние имя курьера (await state.update_data(name=message.text))
    - Отправляет сообщение с просьбой указать номер телефона с помощью KeyboardButton и никак иначе.

    Args:
        message (Message): Объект сообщения от пользователя, содержащий его имя.
        state (FSMContext): Контекст состояния конечного автомата для управления регистрацией.

    Returns:
        None: Функция не возвращает значение, только отправляет сообщение и изменяет состояние.
    """
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)

    courier_name = message.text
    if len(courier_name) > 42:
        text = "Слишком длинное имя!\n\n" "<b>Введите имя еще раз:</b>"
        msg = await message.answer(text, disable_notification=True, parse_mode="HTML")
    else:
        await state.update_data(name=courier_name)
        await state.set_state(CourierRegistration.phone_number)

        reply_kb = await get_courier_kb(
            text="phone_number"
        )  # кнопка для ввода номера телефона
        text = (
            f"Привет, {courier_name}!👋\n\n"
            "Чтобы начать работу, пожалуйста, укажите ваш номер телефона для связи.\n\n"
            "<b>Ваш номер:</b>"
        )
        msg = await message.answer(
            text, disable_notification=True, reply_markup=reply_kb, parse_mode="HTML"
        )

    await handler.handle_new_message(msg, message)


@couriers_router.message(filters.StateFilter(CourierRegistration.phone_number))
async def data_phone_courier(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает состояние курьера после отправки его номера.

    После отправки курьером своего номера:
    - Сохраняет номер курьера в состоянии.
    - Переводит пользователя в состояние регистрации (`CourierRegistration.city`).
    - Отправляет сообщение с просьбой указать свой город работы.

    Args:
        message (Message): Объект сообщения от пользователя, содержащий его номер телефона.
        state (FSMContext): Контекст состояния конечного автомата для управления регистрацией.

    Returns:
        None: Функция не возвращает значение, только отправляет сообщение и изменяет состояние.
    """
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)
    courier_phone = message.contact.phone_number
    await state.update_data(phone_number=courier_phone)
    await state.set_state(CourierRegistration.city)
    text = (
        "Почти всё готово!\n\n"
        "Чтобы сделать заказы максимально удобными, пожалуйста, укажите город, где вы будете работать.\n\n"
        "<b>Ваш город:</b>"
    )
    msg = await message.answer(text, disable_notification=True, parse_mode="HTML")
    await handler.handle_new_message(msg, message)


@couriers_router.message(filters.StateFilter(CourierRegistration.city))
async def data_city_courier(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает состояние курьера после отправки его города.

    После отправки курьером своего города:
    - Переводит пользователя в состояние регистрации (`CourierRegistration.accept_tou`).
    - Сохраняет в состояние город курьера (await state.update_data(city=message.text))
    - Отправляет сообщение с предложением ознакомиться и принять пользовательское соглашение.

    Args:
        message (Message): Объект сообщения от пользователя, содержащий его город.
        state (FSMContext): Контекст состояния конечного автомата для управления регистрацией.

    Returns:
        None: Функция не возвращает значение, только отправляет сообщение и изменяет состояние.
    """
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)

    courier_city = message.text
    await state.update_data(city=courier_city)
    await state.set_state(CourierRegistration.accept_tou)

    reply_kb = await get_courier_kb(text="accept_tou")
    text = (
        "Спасибо за предоставленную информацию!\n\n"
        "Прежде чем начать, пожалуйста, ознакомьтесь и примите "
        "<a href='https://drive.google.com/file/d/1iKhjWckZhn54aYWjDFLQXL46W6J0NhhC/view?usp=sharing'>"
        "Пользовательское соглашение и правила использования</a>, а также "
        "<a href='https://telegram.org/privacy'>Политику конфиденциальности</a>.\n\n"
        "<i>*Пожалуйста, соблюдайте законы и этические нормы при выполнении заказов.</i>"
    )
    new_message = await message.answer(
        text, reply_markup=reply_kb, disable_notification=True, parse_mode="HTML"
    )
    await handler.handle_new_message(new_message, message)


@couriers_router.callback_query(F.data == "accept_tou")
async def courier_accept_tou(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Обрабатывает принятие курьером пользовательского соглашения.

    После принятия курьером пользовательского соглашения:
    - Извлекает из состояния CourierRegistration данные name, phone_number, city, accept_tou.
    - Отправляет запрос в БД для записи.
    - Переводит пользователя в состояние регистрации (`CourierState.default`).
    - Отправляет сообщение с успешной регистрацией и предложением выбрать дальнейшее действие в пункте меню.

    Args:
        callback_query (CallbackQuery): Объект, содержащий информацию о нажатии на кнопку.
        state (FSMContext): Контекст состояния конечного автомата для управления регистрацией.

    Returns:
        None: Функция не возвращает значение, только отправляет сообщение и изменяет состояние.
    """
    handler = MessageHandler(state, callback_query.bot)
    tg_id = callback_query.from_user.id

    # Извлекаем данные о курьере
    data = await state.get_data()
    name = data.get("name")
    phone_number = data.get("phone_number")
    city = data.get("city")
    accept_tou = (
        "Пользовательское соглашение и правила использования сервиса - Принимаю"
    )

    registration_date = datetime.now().isoformat()  # Используем ISO формат для даты

    # Сохраняем информацию в БД
    await courier_data.set_courier_info(
        tg_id, name, phone_number, city, accept_tou, registration_date
    )

    await state.set_state(CourierState.default)

    text = (
        f"Вы успешно зарегистрировались! 🎉\n\n"
        f"Имя: {name}\n"
        f"Номер: {phone_number}\n"
        f"Город: {city}\n\n"
        f"▼ <b>Выберите действие ...</b>"
    )

    new_message = await callback_query.message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )
    await handler.handle_new_message(new_message, callback_query.message)


# ------------------------------------------------------------------------------------------------------------------- #
#                                                    ⇣ Get orders ⇣
# ------------------------------------------------------------------------------------------------------------------- #


# run
@couriers_router.message(F.text == "/run")
@couriers_router.callback_query(F.data == "lets_go")
async def cmd_run(event: Message | CallbackQuery, state: FSMContext) -> None:
    """
    Обрабатывает команду доставить заказ /run или нажатие кнопки lets_go.

    - Переводит пользователя в состояние (`CourierState.location`).
    - Отправляет сообщение c просьбой поделиться локацией и KeyboardButton(send location).

    Args:
        event (Message | CallbackQuery): Объект, содержащий информацию о событии.
        state (FSMContext): Контекст состояния конечного автомата для отслеживания положения в переходах.

    Returns:
        None: Функция не возвращает значение, только отправляет сообщение и изменяет состояние.
    """

    handler = MessageHandler(state, event.bot)
    chat_id = event.chat.id if isinstance(event, Message) else event.message.chat.id

    # Удаление предыдущего сообщения, если это сообщение
    if isinstance(event, Message):
        await handler.delete_previous_message(chat_id)

    await state.set_state(CourierState.location)
    reply_kb = await get_courier_kb(text="/run")

    # Отправляем новое сообщение с просьбой отправить локацию
    new_message = await event.bot.send_message(
        chat_id=chat_id,
        text="Пожалуйста, отправьте вашу текущую локацию, чтобы мы могли назначить вам ближайшие заказы.\n\n"
        "<i>*Доступно только с мобильных устройств</i>",
        reply_markup=reply_kb,
        disable_notification=True,
        parse_mode="HTML",
    )

    # Обрабатываем новое сообщение с помощью MessageHandler
    await handler.handle_new_message(
        new_message, event if isinstance(event, Message) else event.message
    )


# Location
@couriers_router.message(
    F.content_type == ContentType.LOCATION, filters.StateFilter(CourierState.location)
)
async def get_location(message: Message, state: FSMContext) -> None:
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)

    courier_tg_id = message.from_user.id
    my_lon = message.location.longitude
    my_lat = message.location.latitude
    radius_km = 5

    available_orders = await order_data.get_available_orders(
        courier_tg_id, my_lat, my_lon, radius_km=radius_km
    )

    def format_address(number, address, name, phone, url):
        return (
            f"⦿ Адрес {number}: <a href='{url}'>{address}</a>\n"
            f"Имя: {name if name else '-'}\n"
            f"Телефон: {phone if phone else '-'}\n\n"
        )

    orders = []
    order_ids = []  # Список для хранения order_id

    for order in available_orders:
        order_ids.append(order.order_id)  # Сохраняем order_id текущего заказа

        base_info = (
            f"Заказов рядом: {len(available_orders)}\n\n"
            f"Заказ №{order.order_id}\n"
            f"Дата оформления: {order.created_at_moscow_time}\n"
            f"Статус заказа: {order.order_status.value}\n"
            f"---------------------------------------------\n"
            f"Город: {order.order_city}\n\n"
            f"{format_address(1, order.starting_point_a, order.sender_name, order.sender_phone, order.a_url)}"
        )
        # Добавление адресов
        if order.destination_point_b:
            base_info += format_address(
                2,
                order.destination_point_b,
                order.receiver_name_1,
                order.receiver_phone_1,
                order.b_url,
            )
        if order.destination_point_c:
            base_info += format_address(
                3,
                order.destination_point_c,
                order.receiver_name_2,
                order.receiver_phone_2,
                order.c_url,
            )
        # И так далее...

        base_info += (
            f"Доставляем: {order.delivery_object if order.delivery_object else '-'}\n\n"
            f"Расстояние: {order.distance_km} км\n"
            f"Оплата: {order.price_rub}₽\n"
            f"* Принимайте оплату наличными или переводом.\n"
            f"---------------------------------------------\n"
            f"Комментарии: {order.comments if order.comments else '-'}\n\n"
            f"⦿⌁⦿ <a href='{order.full_rout}'>Маршрут</a>\n\n"
        )

        orders.append(base_info)

    if not orders:
        # await message.answer("Спасибо! Локация получена.", reply_markup=ReplyKeyboardRemove())
        await asyncio.sleep(1)
        new_message = await message.answer(
            "Нет доступных заказов в вашем радиусе.", disable_notification=True
        )
        await handler.handle_new_message(new_message, message)
        return

    # Сохраняем заказы и идентификаторы заказов
    counter = 0
    await state.update_data(orders=orders, order_ids=order_ids, counter=counter)

    # Отправляем первый заказ
    reply_kb = await get_courier_kb(
        text="one_order" if len(orders) == 1 else "available_orders"
    )
    # await message.answer("Спасибо! Локация получена.",
    #                      disable_notification=True,
    #                      reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(1)
    handler = MessageHandler(state, message.bot)
    new_message = await message.answer(
        orders[counter],
        reply_markup=reply_kb,
        parse_mode="HTML",
        disable_notification=True,
    )
    await handler.handle_new_message(new_message, message)


@couriers_router.callback_query(
    F.data == "next_right", filters.StateFilter(CourierState.location)
)
async def on_button_next(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    orders = data.get("orders")
    counter = data.get("counter", 0)

    counter = (counter + 1) % len(orders)
    await state.update_data(counter=counter)
    await callback_query.message.edit_text(
        orders[counter],
        reply_markup=callback_query.message.reply_markup,
        parse_mode="HTML",
    )


@couriers_router.callback_query(
    F.data == "back_left", filters.StateFilter(CourierState.location)
)
async def on_button_back(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    orders = data.get("orders")
    counter = data.get("counter", 0)

    counter = (counter - 1) % len(orders)
    await state.update_data(counter=counter)
    await callback_query.message.edit_text(
        orders[counter],
        reply_markup=callback_query.message.reply_markup,
        parse_mode="HTML",
    )


@couriers_router.callback_query(F.data == "accept_order")
async def accept_order(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    order_ids = data.get("order_ids", [])
    counter = data.get("counter", 0)
    courier_tg_id = callback_query.from_user.id

    if not order_ids:
        await callback_query.answer("Заказы не найдены.", show_alert=True)
        return

    order_id = order_ids[counter]

    try:
        # Назначаем курьера к заказу
        await order_data.assign_courier_to_order(
            order_id=order_id, courier_tg_id=courier_tg_id
        )

        # Обновляем статус заказа на "В работе"
        await order_data.update_order_status(
            order_id=order_id, new_status=OrderStatus.IN_PROGRESS
        )

        # Получаем номер телефона заказчика
        customer_phone = await order_data.get_order_customer_phone(order_id)

        # Получаем tg_id по номеру телефона
        customer_tg_id = await user_data.get_user_tg_id_by_phone(customer_phone)

        # Отправляем уведомление заказчику
        notification_text = (
            f"Ваш заказ №{order_id} был принят курьером!\n"
            f"Подробности смотрите в Моих заказах\n\n"
            f"<i>*Сообщение удалится через 15 минут</i>"
        )
        notification_message = await notification_bot.send_message(
            chat_id=customer_tg_id, text=notification_text, parse_mode="HTML"
        )

        # Уведомляем курьера о принятии заказа
        new_message = await callback_query.message.answer(
            "Заказ принят. Вы закреплены за этим заказом.",
            parse_mode="HTML",
            disable_notification=False,
        )
        await state.set_state(CourierState.default)

        handler = MessageHandler(state, callback_query.message.bot)
        await handler.handle_new_message(new_message, callback_query.message)

        # Удаляем уведомление спустя 1 час
        await asyncio.sleep(900)  # Ожидаем 1 час
        try:
            await notification_bot.delete_message(
                chat_id=customer_tg_id, message_id=notification_message.message_id
            )
        except Exception as e:
            logger.error(f"Ошибка при удалении сообщения: {e}")

    except ValueError as e:
        await callback_query.answer(str(e), show_alert=True)
    except Exception as e:
        await callback_query.answer("Ошибка при принятии заказа.", show_alert=True)
        logger.error(f"Ошибка: {e}")


# ------------------------------------------------------------------------------------------------------------------- #
#                                                    ⇣ My orders ⇣
# ------------------------------------------------------------------------------------------------------------------- #
@couriers_router.message(F.text == "/my_orders")
@couriers_router.callback_query(F.data == "back_myOrders")
async def cmd_my_orders(event, state: FSMContext):
    is_callback = isinstance(event, CallbackQuery)
    courier_tg_id = event.from_user.id
    chat_id = event.message.chat.id if is_callback else event.chat.id
    bot = event.message.bot if is_callback else event.bot

    # Удаление предыдущего сообщения, если это не callback
    if not is_callback:
        handler = MessageHandler(state, bot)
        await handler.delete_previous_message(chat_id)

    await state.set_state(CourierState.myOrders)

    # Получение количества заказов курьера
    active_count = len(await order_data.get_active_orders(courier_tg_id))
    completed_count = len(await order_data.get_completed_orders(courier_tg_id))

    # Клавиатура и текст сообщения
    reply_kb = await get_my_orders_kb(active_count, completed_count)
    text = (
        f"✎ <b>Мои заказы</b>\n\n"
        f"Здесь вы можете посмотреть статус ваших заказов, "
        f"а также статистику их выполнения.\n\n"
        f"<b>Статус ваших заказов:</b>"
    )

    if is_callback:
        new_message = await event.message.edit_text(
            text, reply_markup=reply_kb, disable_notification=True, parse_mode="HTML"
        )
    else:
        new_message = await event.answer(
            text, reply_markup=reply_kb, disable_notification=True, parse_mode="HTML"
        )

    # Если это сообщение, обрабатываем новое сообщение
    if not is_callback:
        handler = MessageHandler(state, bot)
        await handler.handle_new_message(new_message, event)
    else:
        await event.answer()


@couriers_router.callback_query(
    F.data.in_({"active_orders", "completed_orders", "next_order", "prev_order"})
)
async def get_courier_orders(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    # Если курьер листает заказы (вперёд или назад)
    if callback_query.data in {"next_order", "prev_order"}:
        counter = data.get("counter", 0)
        orders_text = data.get("orders_text", [])

        # Переключение по заказам (вперёд или назад) с циклическим зацикливанием
        if orders_text:
            total_orders = len(orders_text)
            if callback_query.data == "next_order":
                counter = (counter + 1) % total_orders
            elif callback_query.data == "prev_order":
                counter = (counter - 1) % total_orders

            await state.update_data(counter=counter)
            reply_kb = await get_courier_kb(text="one_my_order")
            await callback_query.message.edit_text(
                orders_text[counter],
                reply_markup=reply_kb,
                parse_mode="HTML",
                disable_notification=True,
            )
        return

    # Основная логика получения заказов
    order_type = callback_query.data
    courier_tg_id = callback_query.from_user.id

    if order_type == "active_orders":
        courier_orders = await order_data.get_active_orders(courier_tg_id)
        await state.set_state(CourierState.myOrders_active)
        status_text = "активных"
    elif order_type == "completed_orders":
        courier_orders = await order_data.get_completed_orders(courier_tg_id)
        await state.set_state(CourierState.myOrders_completed)
        status_text = "завершенных"

    # Проверяем наличие заказов и настраиваем клавиатуру соответственно
    num_orders = len(courier_orders)
    if num_orders == 0:
        text = f"У вас нет {status_text} заказов."
        reply_kb = await get_courier_kb(text="empty_orders")
        await callback_query.message.edit_text(
            text, reply_markup=reply_kb, disable_notification=True
        )
        return
    elif num_orders == 1:
        keyboard_type = (
            "active_one" if order_type == "active_orders" else "complete_one"
        )
    else:
        keyboard_type = (
            "active_orders" if order_type == "active_orders" else "complete_orders"
        )

    # Формируем текст для каждого заказа
    def format_address(number, address, name, phone, url):
        return (
            f"⦿ <b>Адрес {number}:</b> <a href='{url}'>{address}</a>\n"
            f"<b>Имя:</b> {name if name else '-'}\n"
            f"<b>Телефон:</b> {phone if phone else '-'}\n\n"
        )

    # Сохраняем текст каждого заказа и сам `orders` как словарь
    orders_text = []
    orders_dict = {}  # Храним заказы в виде словаря с ID в качестве ключей
    for order in courier_orders:
        base_info = (
            f"{courier_orders.index(order) + 1}/{len(courier_orders)}\n\n"
            f"<b>Заказ №{order.order_id}</b>\n"
            f"<b>Дата оформления:</b> {order.created_at_moscow_time}\n"
            f"<b>Статус заказа:</b> {order.order_status.value}\n"
            f"---------------------------------------------\n"
            f"<b>Город:</b> {order.order_city}\n\n"
            f"{format_address(1, order.starting_point_a, order.sender_name, order.sender_phone, order.a_url)}"
        )

        if order.destination_point_b:
            base_info += format_address(
                2,
                order.destination_point_b,
                order.receiver_name_1,
                order.receiver_phone_1,
                order.b_url,
            )
        if order.destination_point_c:
            base_info += format_address(
                3,
                order.destination_point_c,
                order.receiver_name_2,
                order.receiver_phone_2,
                order.c_url,
            )
        if order.destination_point_d:
            base_info += format_address(
                4,
                order.destination_point_d,
                order.receiver_name_3,
                order.receiver_phone_3,
                order.d_url,
            )
        if order.destination_point_e:
            base_info += format_address(
                5,
                order.destination_point_e,
                order.receiver_name_4,
                order.receiver_phone_4,
                order.e_url,
            )

        base_info += (
            f"<b>Доставляем:</b> {order.delivery_object if order.delivery_object else '-'}\n\n"
            f"<b>Расстояние:</b> {order.distance_km} км\n"
            f"<b>Стоимость доставки:</b> {order.price_rub}₽\n"
            f"---------------------------------------------\n"
            f"<b>Комментарии:</b> <i>{'*'}{order.comments if order.comments else '...'}</i>\n\n"
            f"⦿⌁⦿ <a href='{order.full_rout}'>Маршрут</a>\n\n"
        )

        orders_text.append(base_info)
        orders_dict[order.order_id] = order  # Сохраняем каждый заказ по его ID

    # Устанавливаем данные для состояния
    counter = 0
    current_order_id = courier_orders[counter].order_id
    await state.update_data(
        orders_text=orders_text,
        orders=orders_dict,
        counter=counter,
        current_order_id=current_order_id,
    )

    # Устанавливаем соответствующую клавиатуру
    reply_kb = await get_courier_kb(text=keyboard_type)
    await callback_query.message.edit_text(
        orders_text[counter],
        reply_markup=reply_kb,
        parse_mode="HTML",
        disable_notification=True,
    )


@couriers_router.callback_query(F.data == "my_statistic")
async def get_courier_statistic(callback_query: CallbackQuery, state: FSMContext):
    courier_tg_id = callback_query.from_user.id

    # Получение статистики курьера из одного вызова
    stats = await order_data.get_order_statistics(courier_tg_id)

    # Вычисление процента успешных доставок
    total_orders = stats["total_orders"]
    completed_orders = stats["completed_orders"]
    success_rate = (completed_orders / total_orders) * 100 if total_orders > 0 else 0

    # Формирование текста сообщения
    text = (
        f"☈ <b>Статистика доставок</b>\n\n"
        f"Всего заказов: {total_orders}\n"
        f"Завершенные заказы: {completed_orders}\n\n"
        f"Самая низкая скорость: {stats['slowest_order_speed']:.2f} км/ч\n"
        f"Самая высокая скорость: {stats['fastest_order_speed']:.2f} км/ч\n"
        f"Средняя скорость: {stats['avg_order_speed']:.2f} км/ч\n\n"
        f"Самая долгая доставка: {stats['longest_order_time']:.2f} мин\n"
        f"Самая быстрая доставка: {stats['fastest_order_time']:.2f} мин\n"
        f"Среднее время доставки: {stats['avg_order_time']:.2f} мин\n\n"
        f"Самое короткое расстояние: {stats['shortest_order_distance']:.2f} км\n"
        f"Самое длинное расстояние: {stats['longest_order_distance']:.2f} км\n"
        f"Среднее расстояние: {stats['avg_order_distance']:.2f} км\n\n"
        f"Минимальная стоимость: {stats['min_price']:.2f} руб.\n"
        f"Максимальная стоимость: {stats['max_price']:.2f} руб.\n"
        f"Средняя стоимость: {stats['avg_price']:.2f} руб.\n\n"
        f"Всего заработано: {stats['total_earn']:.2f} руб.\n\n"
        f"Процент успешных доставок: {success_rate:.2f}%\n"
    )

    reply_kb = await get_courier_kb(text="go_back")

    # Отправка сообщения курьеру
    await callback_query.message.edit_text(
        text, reply_markup=reply_kb, parse_mode="HTML"
    )


@couriers_router.callback_query(F.data == "next_right_mo")
async def on_button_next_my_orders(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    orders_text = data.get("orders_text", [])  # Список текста для каждого заказа
    orders = data.get("orders", {})  # Словарь с полными данными заказов
    counter = data.get("counter", 0)

    # Увеличиваем счетчик и зацикливаем его
    counter = (counter + 1) % len(orders_text) if orders_text else 0

    # Обновляем состояние с новым значением счетчика и ID текущего заказа
    current_order_id = list(orders.keys())[
        counter
    ]  # Получаем ID нового активного заказа
    await state.update_data(counter=counter, current_order_id=current_order_id)

    # Обновляем сообщение с новым заказом
    new_order_info = orders_text[counter] if orders_text else "Нет заказов"
    await callback_query.message.edit_text(
        new_order_info,
        reply_markup=callback_query.message.reply_markup,
        parse_mode="HTML",
    )


@couriers_router.callback_query(F.data == "back_left_mo")
async def on_button_back_my_orders(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    orders_text = data.get("orders_text", [])
    orders = data.get("orders", {})
    counter = data.get("counter", 0)

    # Уменьшаем счетчик и зацикливаем его
    counter = (counter - 1) % len(orders_text) if orders_text else 0

    # Обновляем состояние с новым значением счетчика
    current_order_id = list(orders.keys())[counter]
    await state.update_data(counter=counter, current_order_id=current_order_id)

    # Обновляем сообщение с новым заказом
    new_order_info = orders_text[counter] if orders_text else "Нет заказов"
    await callback_query.message.edit_text(
        new_order_info,
        reply_markup=callback_query.message.reply_markup,
        parse_mode="HTML",
    )


# ------------------------------------------------------------------------------------------------------------------- #
#                                                    ⇣ order_delivered ⇣
# ------------------------------------------------------------------------------------------------------------------- #
@couriers_router.callback_query(F.data == "order_delivered")
async def complete_order(callback_query: CallbackQuery, state: FSMContext):
    handler = MessageHandler(state, callback_query.message.bot)
    data = await state.get_data()
    current_order_id = data.get("current_order_id")  # Получаем ID текущего заказа

    if not current_order_id:
        await callback_query.message.answer(
            "Не удалось найти активный заказ для завершения."
        )
        return

    try:
        # Проверяем текущий статус заказа
        order = await order_data.get_order_by_id(current_order_id)
        if order.order_status != OrderStatus.IN_PROGRESS:
            await callback_query.message.answer(
                f"Заказ №{current_order_id} нельзя завершить, так как он не в статусе выполнения."
            )
            return

        # Обновляем статус заказа на "Завершен" и устанавливаем время завершения в базе данных
        completed_time = datetime.now()  # Текущее время завершения
        await order_data.update_order_status_and_time(
            order_id=current_order_id,
            new_status=OrderStatus.COMPLETED,
            completed_time=completed_time,
        )

        # Получаем данные заказчика для отправки уведомления
        customer_phone = await order_data.get_order_customer_phone(current_order_id)
        customer_tg_id = await user_data.get_user_tg_id_by_phone(customer_phone)

        # Отправляем уведомление заказчику
        notification_text = (
            f"Ваш заказ №{current_order_id} был успешно доставлен курьером!\n"
            f"Спасибо, что воспользовались нашим сервисом.\n\n"
            f"<i>*Сообщение удалится через 15 минут</i>"
        )
        notification_message = await notification_bot.send_message(
            chat_id=customer_tg_id, text=notification_text, parse_mode="HTML"
        )

        # Уведомляем курьера о завершении заказа
        await callback_query.message.answer(
            "Статус заказа обновлен на 'Завершен'. Заказчик уведомлен.",
            parse_mode="HTML",
            disable_notification=False,
        )

        # Удаляем предыдущее сообщение курьера перед отправкой нового
        await handler.delete_previous_message(callback_query.message.chat.id)

        # Устанавливаем состояние курьера в начальное состояние
        await state.set_state(CourierState.default)

        # Удаляем уведомление заказчику через 15 минут
        await asyncio.sleep(900)
        try:
            await notification_bot.delete_message(
                chat_id=customer_tg_id, message_id=notification_message.message_id
            )
        except Exception as e:
            logger.error(f"Ошибка при удалении сообщения заказчику: {e}")

    except ValueError as e:
        await callback_query.answer(str(e), show_alert=True)
    except Exception as e:
        await callback_query.answer("Ошибка при завершении заказа.", show_alert=True)
        logger.error(f"Ошибка при завершении заказа: {e}")


# ------------------------------------------------------------------------------------------------------------------- #
#                                                    ⇣ Payment ⇣
# ------------------------------------------------------------------------------------------------------------------- #


@couriers_router.message(F.text == "/subs")
@couriers_router.callback_query(F.data == "pay_sub")
async def payment_invoice(event: Message | CallbackQuery, state: FSMContext):
    """
    Обрабатывает команду доставить заказ /subs.

    После отправки команды /subs:
    - Переводит пользователя в состояние (`CourierState.default`).
    - Отправляет сообщение c предложением преобрести или продлить подписку с InlineButton для перехода на инвойс.

    Args:
        message (Message): Объект, содержащий информацию о нажатии на кнопку.
        state (FSMContext): Контекст состояния конечного автомата для отслеживания положения в переходах.

    Returns:
        None: Функция не возвращает значение, только отправляет сообщение и изменяет состояние.
    """
    await state.set_state(CourierState.pay)
    handler = MessageHandler(state, event.bot)
    chat_id = event.chat.id if isinstance(event, Message) else event.message.chat.id

    if isinstance(event, Message):
        await handler.delete_previous_message(chat_id)

    prices = [
        LabeledPrice(
            label="Месячная подписка",
            amount=99000,  # Сумма указана в копейках (990 рублей)
        ),
    ]

    provider_token = os.getenv("UKASSA_TEST")
    if not provider_token:
        print("Ошибка: provider_token не найден. Проверьте переменные окружения.")
        return

    # Отправка инвойса пользователю
    new_message = await event.bot.send_invoice(
        chat_id=chat_id,
        title="Подписка Raketa",
        description="Оформите подписку на сервис доставки...",
        payload="Payment through a bot",
        provider_token=provider_token,
        currency="RUB",
        prices=prices,
        max_tip_amount=50000,
        start_parameter="",
        photo_url="https://i.ibb.co/NpQzZyY/subs.jpg",
        photo_width=1200,
        photo_height=720,
        need_name=True,
        need_phone_number=True,
        need_email=True,
        reply_markup=None,
        disable_notification=True,
    )

    await handler.handle_new_message(
        new_message, event if isinstance(event, Message) else event.message
    )


# Обработка подтверждения платежа
@couriers_router.pre_checkout_query()
async def pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    try:
        if (
            pre_checkout_query.currency == "RUB"
            and pre_checkout_query.total_amount == 99000
        ):
            await pre_checkout_query.bot.answer_pre_checkout_query(
                pre_checkout_query.id, ok=True
            )
        else:
            await pre_checkout_query.bot.answer_pre_checkout_query(
                pre_checkout_query.id,
                ok=False,
                error_message="Неверная сумма или валюта",
            )
    except Exception as e:
        await pre_checkout_query.bot.answer_pre_checkout_query(
            pre_checkout_query.id, ok=False, error_message=f"Ошибка: {str(e)}"
        )


# Сообщение об успешной оплате
@couriers_router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def succesful_payment(message: Message, state: FSMContext):
    await state.set_state(CourierState.default)
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)
    photo_title = await get_image_title_courier("success_payment")
    text = f"Cпасибо за подписку!\nСумма: {message.successful_payment.total_amount // 100}{message.successful_payment.currency}"
    reply_kb = await get_courier_kb(text="success_payment")
    new_message = await message.answer_photo(
        photo=photo_title,
        caption=text,
        reply_markup=reply_kb,
        disable_notification=True,
    )
    await handler.handle_new_message(new_message, message)


# ------------------------------------------------------------------------------------------------------------------- #
#                                                    ⇣ Profile ⇣
# ------------------------------------------------------------------------------------------------------------------- #


@couriers_router.message(F.text == "/profile")
async def cmd_profile(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает команду доставить заказ /profile.

    После отправки команды /profile:
    - Переводит пользователя в состояние (`CourierState.default`).
    - Отправляет сообщение c информацией о курьере (имя, номер телефона, город, статус подписки и ее срок).

    Args:
        message (Message): Объект, содержащий информацию о нажатии на кнопку.
        state (FSMContext): Контекст состояния конечного автомата для отслеживания положения в переходах.

    Returns:
        None: Функция не возвращает значение, только отправляет сообщение и изменяет состояние.
    """
    await state.set_state(CourierState.default)
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)

    tg_id = message.from_user.id
    courier_name, courier_phone_number, courier_default_city, subscription_status = (
        await courier_data.get_courier_full_info(tg_id)
    )

    text = (
        f"👤 <b>Профиль курьера</b>\n\n"
        f"Посмотрите или измените данные о себе.\n\n"
        f"<b>Имя:</b> {courier_name}\n"
        f"<b>Номер:</b> {courier_phone_number}\n"
        f"<b>Город:</b> {courier_default_city}\n"
        f"<b>Статус подписки:</b> {subscription_status}\n"
    )

    reply_kb = await get_courier_kb(text="/profile")

    new_message = await message.answer(
        text, reply_markup=reply_kb, disable_notification=True, parse_mode="HTML"
    )
    await handler.handle_new_message(new_message, message)


@couriers_router.callback_query(F.data == "set_my_name")
async def set_name(callback_query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(CourierState.change_Name)
    handler = MessageHandler(state, callback_query.bot)
    text = f"Изменить данные профиля.\n\n" f"<b>Ваше имя:</b>"
    new_message = await callback_query.message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )
    await handler.handle_new_message(new_message, callback_query.message)


@couriers_router.callback_query(F.data == "set_my_phone")
async def set_phone(callback_query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(CourierState.change_Phone)
    handler = MessageHandler(state, callback_query.bot)
    reply_kb = await get_courier_kb(text="phone_number")
    text = f"Изменить данные профиля.\n\n" f"<b>Ваш Телефон:</b>"
    new_message = await callback_query.message.answer(
        text, disable_notification=True, reply_markup=reply_kb, parse_mode="HTML"
    )
    await handler.handle_new_message(new_message, callback_query.message)


@couriers_router.callback_query(F.data == "set_my_city")
async def set_city(callback_query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(CourierState.change_City)
    handler = MessageHandler(state, callback_query.bot)
    text = f"Изменить данные профиля.\n\n" f"<b>Ваш город:</b>"
    new_message = await callback_query.message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )
    await handler.handle_new_message(new_message, callback_query.message)


@couriers_router.message(filters.StateFilter(CourierState.change_Name))
async def change_name(message: Message, state: FSMContext):
    await state.set_state(CourierState.default)
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)

    tg_id = message.from_user.id
    name = message.text

    await courier_data.set_courier_name(
        tg_id, name
    )  # Метод для обновления имени курьера
    text = (
        f"Имя курьера было изменено на {name} 🎉\n\n" f"▼ <b>Выберите действие ...</b>"
    )
    new_message = await message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )

    await handler.handle_new_message(new_message, message)


@couriers_router.message(filters.StateFilter(CourierState.change_Phone))
async def change_phone(message: Message, state: FSMContext):
    await state.set_state(CourierState.default)
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)

    tg_id = message.from_user.id
    phone = message.contact.phone_number

    await courier_data.set_courier_phone(
        tg_id, phone
    )  # Метод для обновления телефона курьера
    text = (
        f"Номер курьера был изменен на {phone} 🎉\n\n" f"▼ <b>Выберите действие ...</b>"
    )
    new_message = await message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )

    await handler.handle_new_message(new_message, message)


@couriers_router.message(filters.StateFilter(CourierState.change_City))
async def change_city(message: Message, state: FSMContext):
    await state.set_state(CourierState.default)
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)

    tg_id = message.from_user.id
    city = message.text

    await courier_data.set_courier_city(
        tg_id, city
    )  # Метод для обновления города курьера
    text = (
        f"Город курьера был изменен на {city} 🎉\n\n" f"▼ <b>Выберите действие ...</b>"
    )
    new_message = await message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )

    await handler.handle_new_message(new_message, message)


# ------------------------------------------------------------------------------------------------------------------- #
#                                                    ⇣ fqs ⇣
# ------------------------------------------------------------------------------------------------------------------- #


@couriers_router.message(F.text == "/faq")
async def cmd_faq(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает команду /faq.

    После отправки команды /faq:
    - Переводит пользователя в состояние (`CourierState.default`).
    - Отправляет сообщение c ссылкой на документ с вопросами и ответами.

    Args:
        message (Message): Объект, содержащий информацию о нажатии на кнопку.
        state (FSMContext): Контекст состояния конечного автомата для отслеживания положения в переходах.

    Returns:
        None: Функция не возвращает значение, только отправляет сообщение и изменяет состояние.
    """
    await state.set_state(CourierState.default)
    handler = MessageHandler(state, message.bot)

    # Логируем попытку удаления предыдущего сообщения
    try:
        await handler.delete_previous_message(message.chat.id)
    except Exception as e:
        logger.error(f"Ошибка при удалении предыдущего сообщения: {e}")

    text = (
        f"🤔 <b>Вопросы и ответы</b>\n\n"
        f"Частые вопросы и ответы на них "
        f"<a href='https://drive.google.com/file/d/1cXYK_FqU7kRpTU9p04dVjcE4vRbmNvMw/view?usp=sharing'>FAQ</a>"
    )

    new_message = await message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )
    await handler.handle_new_message(new_message, message)


@couriers_router.message(F.text == "/rules")
async def cmd_rules(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает команду /rules.

    После отправки команды /rules:
    - Переводит пользователя в состояние (`CourierState.default`).
    - Отправляет сообщение c ссылкой на документ с правилами сервиса.

    Args:
        message (Message): Объект, содержащий информацию о нажатии на кнопку.
        state (FSMContext): Контекст состояния конечного автомата для отслеживания положения в переходах.

    Returns:
        None: Функция не возвращает значение, только отправляет сообщение и изменяет состояние.
    """
    await state.set_state(CourierState.default)
    handler = MessageHandler(state, message.bot)

    # Логируем попытку удаления предыдущего сообщения
    try:
        await handler.delete_previous_message(message.chat.id)
    except Exception as e:
        logger.error(f"Ошибка при удалении предыдущего сообщения: {e}")

    text = (
        f"⚖️ <b>Правила сервиса</b>\n\n"
        f"Начиная использование сервиса, вы соглашаетесь с "
        f"<a href='https://drive.google.com/file/d/1iKhjWckZhn54aYWjDFLQXL46W6J0NhhC/view?usp=sharing'>"
        f"Пользовательским соглашением и правилами использования</a>, а также "
        f"<a href='https://telegram.org/privacy'>Политикой конфиденциальности</a>.\n\n"
        f"<i>*Обращаем внимание, что любые действия, связанные с заказами, "
        f"отправкой или получением посылок, должны соответствовать законодательству "
        f"вашего государства и общепринятым этическим нормам.</i>\n\n"
    )

    new_message = await message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )
    await handler.handle_new_message(new_message, message)


# ------------------------------------------------------------------------------------------------------------------- #
#                                                    ⇣ ai ⇣
# ------------------------------------------------------------------------------------------------------------------- #
@couriers_router.message(F.text == "/ai_support_couriers")
async def cmd_ai_support_couriers(message: Message, state: FSMContext):
    """
    Обрабатывает команду доставить заказ /ai_support_couriers.

    После отправки команды /ai_support_couriers:
    - Переводит пользователя в состояние (`CourierState.default`).
    - Отправляет сообщение c InlineButton кнопкой для перехода на бот поддержки.

    Args:
        message (Message): Объект, содержащий информацию о нажатии на кнопку.
        state (FSMContext): Контекст состояния конечного автомата для отслеживания положения в переходах.

    Returns:
        None: Функция не возвращает значение, только отправляет сообщение и изменяет состояние.
    """


# ------------------------------------------------------------------------------------------------------------------- #
#                                                    ⇣ make order ⇣
# ------------------------------------------------------------------------------------------------------------------- #


@couriers_router.message(F.text == "/make_order")
async def cmd_ai_support_couriers(message: Message, state: FSMContext):
    """
    Обрабатывает команду /make_order.

    После отправки команды /make_order:
    - Переводит пользователя в состояние (`CourierState.default`).
    - Отправляет сообщение c InlineButton кнопкой для перехода на клиентский бот для оформления заказов.

    Args:
        message (Message): Объект, содержащий информацию о нажатии на кнопку.
        state (FSMContext): Контекст состояния конечного автомата для отслеживания положения в переходах.

    Returns:
        None: Функция не возвращает значение, только отправляет сообщение и изменяет состояние.
    """
    await state.set_state(CourierState.default)
    handler = MessageHandler(state, message.bot)

    # Логируем попытку удаления предыдущего сообщения
    try:
        await handler.delete_previous_message(message.chat.id)
    except Exception as e:
        logger.error(f"Ошибка при удалении предыдущего сообщения: {e}")

    reply_kb = await get_courier_kb(text="/make_order")
    # Формируем текст сообщения
    text = "📦 Для оформления заказа, пожалуйста, перейдите в клиентский бот."

    # Отправляем сообщение с кнопкой для перехода на клиентский бот
    new_message = await message.answer(
        text, disable_notification=True, reply_markup=reply_kb
    )

    await handler.handle_new_message(new_message, message)
