import asyncio

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.enums import ContentType
from aiogram import filters

from app.c_pack.c_middlewares import OuterMiddleware, InnerMiddleware
from app.c_pack.c_states import CourierState, CourierRegistration
from app.common.message_handler import MessageHandler
from app.common.titles import get_image_title_courier
from app.common.titles import get_image_title_courier
from app.c_pack.c_kb import get_courier_kb
from app.database.models import OrderStatus

from app.database.requests import courier_data, order_data

from datetime import datetime

couriers_router = Router()

couriers_router.message.outer_middleware(OuterMiddleware())
couriers_router.callback_query.outer_middleware(OuterMiddleware())

couriers_router.message.middleware(InnerMiddleware())
couriers_router.callback_query.middleware(InnerMiddleware())


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
        new_message = await message.answer(text, parse_mode="HTML", disable_notification=True)
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

        new_message = await message.answer_photo(photo=photo_title,
                                                 caption=text,
                                                 reply_markup=reply_kb,
                                                 parse_mode="HTML",
                                                 disable_notification=True)
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
    new_message = await callback_query.message.answer(text, disable_notification=True, parse_mode="HTML")
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
        text = (
            "Слишком длинное имя!\n\n"
            "<b>Введите имя еще раз:</b>"
        )
        msg = await message.answer(text, disable_notification=True, parse_mode="HTML")
    else:
        await state.update_data(name=courier_name)
        await state.set_state(CourierRegistration.phone_number)

        reply_kb = await get_courier_kb(text="phone_number")  # кнопка для ввода номера телефона
        text = (
            f"Привет, {courier_name}!👋\n\n"
            "Чтобы начать работу, пожалуйста, укажите ваш номер телефона для связи.\n\n"
            "<b>Ваш номер:</b>"
        )
        msg = await message.answer(text, disable_notification=True, reply_markup=reply_kb, parse_mode="HTML")

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
    new_message = await message.answer(text, reply_markup=reply_kb, disable_notification=True, parse_mode="HTML")
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
    name = data.get('name')
    phone_number = data.get('phone_number')
    city = data.get('city')
    accept_tou = "Пользовательское соглашение и правила использования сервиса - Принимаю"

    registration_date = datetime.now().isoformat()  # Используем ISO формат для даты

    # Сохраняем информацию в БД
    await courier_data.set_courier_info(tg_id, name, phone_number, city, accept_tou, registration_date)

    await state.set_state(CourierState.default)

    text = (f"Вы успешно зарегистрировались! 🎉\n\n"
            f"Имя: {name}\n"
            f"Номер: {phone_number}\n"
            f"Город: {city}\n\n"
            f"▼ <b>Выберите действие ...</b>"
            )

    new_message = await callback_query.message.answer(text, disable_notification=True, parse_mode="HTML")
    await handler.handle_new_message(new_message, callback_query.message)


# ------------------------------------------------------------------------------------------------------------------- #
#                                                    ⇣ Get orders ⇣
# ------------------------------------------------------------------------------------------------------------------- #

# run
@couriers_router.message(F.text == "/run")
async def cmd_run(message: Message, state: FSMContext) -> None:
    """
        Обрабатывает команду доставить заказ /run.

        После отправки команды /run:
        - Переводит пользователя в состояние (`CourierState.location`).
        - Отправляет сообщение c просьбой поделиться локацией и KeyboardButton(send location).

        Args:
            message (Message): Объект, содержащий информацию о нажатии на кнопку.
            state (FSMContext): Контекст состояния конечного автомата для отслеживания положения в переходах.

        Returns:
            None: Функция не возвращает значение, только отправляет сообщение и изменяет состояние.
    """

    # handler = MessageHandler(state, message.bot)
    # await handler.delete_previous_message(message.chat.id)
    await state.set_state(CourierState.location)
    reply_kb = await get_courier_kb(text="/run")

    new_message = await message.answer(
        "Пожалуйста, отправьте вашу текущую локацию, чтобы мы могли назначить вам ближайшие заказы.",
        reply_markup=reply_kb, disable_notification=True)
    # await handler.handle_new_message(new_message, message)


# Location
@couriers_router.message(F.content_type == ContentType.LOCATION, filters.StateFilter(CourierState.location))
async def get_location(message: Message, state: FSMContext) -> None:
    courier_tg_id = message.from_user.id
    my_lon = message.location.longitude
    my_lat = message.location.latitude
    radius_km = 5

    available_orders = await order_data.get_available_orders(courier_tg_id, my_lat, my_lon, radius_km=radius_km)

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
            base_info += format_address(2, order.destination_point_b, order.receiver_name_1, order.receiver_phone_1,
                                        order.b_url)
        if order.destination_point_c:
            base_info += format_address(3, order.destination_point_c, order.receiver_name_2, order.receiver_phone_2,
                                        order.c_url)
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
        await message.answer("Спасибо! Локация получена.", reply_markup=ReplyKeyboardRemove())
        await asyncio.sleep(1)
        await message.answer("Нет доступных заказов в вашем радиусе.", disable_notification=True)
        return

    # Сохраняем заказы и идентификаторы заказов
    counter = 0
    await state.update_data(orders=orders, order_ids=order_ids, counter=counter)

    # Отправляем первый заказ
    reply_kb = await get_courier_kb(text="one_order" if len(orders) == 1 else "available_orders")
    await message.answer("Спасибо! Локация получена.",
                         disable_notification=True,
                         reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(1)
    handler = MessageHandler(state, message.bot)
    new_message = await message.answer(orders[counter], reply_markup=reply_kb, parse_mode="HTML",
                                       disable_notification=True)
    await handler.handle_new_message(new_message, message)


@couriers_router.callback_query(F.data == "next_right", filters.StateFilter(CourierState.location))
async def on_button_next(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    orders = data.get("orders")
    counter = data.get("counter", 0)

    counter = (counter + 1) % len(orders)
    await state.update_data(counter=counter)
    await callback_query.message.edit_text(orders[counter], reply_markup=callback_query.message.reply_markup,
                                           parse_mode="HTML")


@couriers_router.callback_query(F.data == "back_left", filters.StateFilter(CourierState.location))
async def on_button_back(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    orders = data.get("orders")
    counter = data.get("counter", 0)

    counter = (counter - 1) % len(orders)
    await state.update_data(counter=counter)
    await callback_query.message.edit_text(orders[counter], reply_markup=callback_query.message.reply_markup,
                                           parse_mode="HTML")


@couriers_router.callback_query(F.data == "accept_order")
async def accept_order(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    order_ids = data.get("order_ids", [])
    counter = data.get("counter", 0)  # Текущий индекс заказа
    courier_tg_id = callback_query.from_user.id

    # handler = MessageHandler(state, callback_query.message.bot)
    # await handler.delete_previous_message(callback_query.message.chat.id)
    if not order_ids:
        await callback_query.answer("Ошибка: заказы не найдены.", show_alert=True)
        return

    order_id = order_ids[counter]  # `order_id` текущего заказа

    try:
        # Назначаем курьера к заказу
        await order_data.assign_courier_to_order(order_id=order_id, courier_tg_id=courier_tg_id)

        # Обновляем статус заказа на "В работе" (или другой необходимый статус)
        await order_data.update_order_status(order_id=order_id, new_status=OrderStatus.IN_PROGRESS)

        await callback_query.message.answer("Заказ успешно принят!")

        # Обновляем интерфейс
        await callback_query.message.answer("Заказ принят. Вы закреплены за этим заказом.", parse_mode="HTML",
                                            show_alert=True)
    except ValueError as e:
        await callback_query.answer(str(e), show_alert=True)
    except Exception as e:
        await callback_query.answer("Ошибка при принятии заказа.", show_alert=True)
        print(f"Ошибка при принятии заказа: {e}")


# ------------------------------------------------------------------------------------------------------------------- #
#                                                    ⇣ Get orders ⇣
# ------------------------------------------------------------------------------------------------------------------- #
@couriers_router.message(F.text == "/my_orders")
@couriers_router.callback_query(F.data == "back_myOrders")
async def cmd_my_orders(event, state: FSMContext) -> None:
    """
        Обрабатывает команду отображения заказов курьера /my_orders , back_myOrders.

        После отправки команды /my_orders или back_myOrders:
        - Переводит пользователя в состояние (`CourierState.myOrders`).
        - Отправляет курьеру сообщение меню со всеми его заказами и статистикой их выполнения

        Args:
            event: Объект, содержащий информацию о нажатии на кнопку.
            state (FSMContext): Контекст состояния конечного автомата для отслеживания положения в переходах.

        Returns:
            None: Функция не возвращает значение, только отправляет сообщение и изменяет состояние.
    """


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


@couriers_router.message(F.text == "/subs")
async def cmd_subs(message: Message, state: FSMContext) -> None:
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


@couriers_router.message(F.text == "/faq")
async def cmd_faq(message: Message, state: FSMContext) -> None:
    """
        Обрабатывает команду доставить заказ /faq.

        После отправки команды /faq:
        - Переводит пользователя в состояние (`CourierState.default`).
        - Отправляет сообщение c ссылкой на документ с вопросами и ответами.

        Args:
            message (Message): Объект, содержащий информацию о нажатии на кнопку.
            state (FSMContext): Контекст состояния конечного автомата для отслеживания положения в переходах.

        Returns:
            None: Функция не возвращает значение, только отправляет сообщение и изменяет состояние.
    """


@couriers_router.message(F.text == "/rules")
async def cmd_rules(message: Message, state: FSMContext) -> None:
    """
        Обрабатывает команду доставить заказ /rules.

        После отправки команды /rules:
        - Переводит пользователя в состояние (`CourierState.default`).
        - Отправляет сообщение c ссылкой на документ с вопросами и правилами сервиса.

        Args:
            message (Message): Объект, содержащий информацию о нажатии на кнопку.
            state (FSMContext): Контекст состояния конечного автомата для отслеживания положения в переходах.

        Returns:
            None: Функция не возвращает значение, только отправляет сообщение и изменяет состояние.
    """


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


@couriers_router.message(F.text == "/make_order")
async def cmd_ai_support_couriers(message: Message, state: FSMContext):
    """
        Обрабатывает команду доставить заказ /make_order.

        После отправки команды /make_order:
        - Переводит пользователя в состояние (`CourierState.default`).
        - Отправляет сообщение c InlineButton кнопкой для перехода на клиентский бот для оформления заказов.

        Args:
            message (Message): Объект, содержащий информацию о нажатии на кнопку.
            state (FSMContext): Контекст состояния конечного автомата для отслеживания положения в переходах.

        Returns:
            None: Функция не возвращает значение, только отправляет сообщение и изменяет состояние.
    """
