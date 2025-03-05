from ._deps import (
    asyncio,
    CommandStart,
    FSMContext,
    ContentType,
    filters,
    Message,
    CallbackQuery,
    OrderStatus,
    MessageHandler,
    CourierState,
    CourierOuterMiddleware,
    datetime,
    PreCheckoutQuery,
    Router,
    moscow_time,
    courier_r,
    courier_fallback,
    courier_data,
    payment_r,
    kb,
    title,
    customer_data,
    order_data,
    rediska,
    cities,
    log,
    F,
    find_closest_city,
)


# ---


courier_r.message.outer_middleware(CourierOuterMiddleware(rediska))
courier_r.callback_query.outer_middleware(CourierOuterMiddleware(rediska))


# ---


@courier_r.message(CommandStart())
async def cmd_start_courier(message: Message, state: FSMContext):
    log.info(f"cmd_start_courier was called!")

    bot_id = message.bot.id
    tg_id = message.from_user.id
    current_state = CourierState.reg_state.state

    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)

    handler = MessageHandler(state, message.bot)
    is_reg = await rediska.is_reg(bot_id, tg_id)

    if is_reg:
        default_state = CourierState.default.state
        await state.set_state(default_state)
        await rediska.set_state(bot_id, tg_id, default_state)
        text = "▼ <b>Выберите действие ...</b>"
        await handler.delete_previous_message(message.chat.id)
        new_message = await message.answer(
            text, parse_mode="HTML", disable_notification=True
        )
        await handler.handle_new_message(new_message, message)
        return

    photo_title = await title.get_title_courier("/start")
    text = (
        "Добро пожаловать в сервис доставки Ракета!\n"
        "Стань частью сообщества, где ты сам управляешь своими доходами и работаешь на своих условиях.\n\n"
        "Почему мы?\n\n"
        "◉ <b>Зарабатывай больше</b>: \n"
        "Ты оплачиваешь только подписку и получаешь 100% прибыли с каждого заказа. Чем больше работаешь, тем больше зарабатываешь.\n\n"
        "◉ <b>Свобода выбора</b>: \n"
        "Твоя работа — на твоих условиях. Бери заказы в любое время и работай так, как удобно тебе.\n\n"
        "◉ <b>Прозрачность</b>: \n"
        "Каждый заработанный рубль — твой. Никаких посредников, штрафов и скрытых условиях.\n\n"
        "Присоединяйся к Ракете и начинай зарабатывать больше уже сегодня!"
    )
    reply_kb = await kb.get_courier_kb("/start")
    await handler.delete_previous_message(message.chat.id)
    new_message = await message.answer_photo(
        photo=photo_title,
        caption=text,
        reply_markup=reply_kb,
        parse_mode="HTML",
        disable_notification=True,
    )
    await handler.handle_new_message(new_message, message)

    log.info(
        f"\n"
        f"- Courier 🚴\n"
        f"- Handler /start\n"
        f"- Courier telegram ID: {tg_id}\n"
        f"- Courier message: {message.text}\n"
        f"- Courier state now: {current_state}"
    )

    log.info(f"cmd_start_courier was successfully done!")


@courier_r.callback_query(F.data == "reg")
async def data_reg_courier(callback_query: CallbackQuery, state: FSMContext):
    log.info(f"data_reg_courier was called!")

    bot_id = callback_query.bot.id
    tg_id = callback_query.from_user.id
    current_state = CourierState.reg_Name.state

    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)

    handler = MessageHandler(state, callback_query.bot)
    text = (
        "Пройдите небольшую регистрацию.\n"
        "Это не займет много времени.\n\n"
        "<b>Как вас зовут?</b>"
    )
    new_message = await callback_query.message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )
    await handler.handle_new_message(new_message, callback_query.message)

    log.info(
        f"\n"
        f"- Courier 🚴\n"
        f"- Handler F.data: {F.data}\n"
        f"- Courier telegram ID: {tg_id}\n"
        f"- Courier message: {callback_query.message.text}\n"
        f"- Courier state now: {current_state}"
    )

    log.info(f"data_reg_courier was successfully done!")


@courier_r.message(filters.StateFilter(CourierState.reg_Name))
async def data_name_courier(message: Message, state: FSMContext):
    log.info(f"data_name_courier was called!")

    handler = MessageHandler(state, message.bot)
    handle_state = await state.get_state()
    bot_id = message.bot.id
    tg_id = message.from_user.id
    courier_name = message.text
    current_state = CourierState.reg_Phone.state

    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)
    is_name_set = await rediska.set_user_name(bot_id, tg_id, courier_name)

    reply_kb = await kb.get_courier_kb("phone_number")
    text = (
        f"Привет, {courier_name}!👋\n\nЧтобы начать работу, пожалуйста, укажите ваш номер телефона для связи.\n\n"
        f"<i>*При регистрации с компьютера нажмите на значок команд рядом с полем ввода.</i>\n\n"
        f"<i>*Отправка номера возможно только по клику на кнопку 'Поделится номером'!</i>\n\n"
        f"<b>Ваш номер:</b>"
    )

    await handler.delete_previous_message(message.chat.id)
    new_message = await message.answer(
        text,
        disable_notification=True,
        reply_markup=reply_kb,
        parse_mode="HTML",
    )
    await handler.handle_new_message(new_message, message)

    log.info(
        f"\n"
        f"- Courier 🚴\n"
        f"- Handler StateFilter: {handle_state}\n"
        f"- Courier telegram ID: {tg_id}\n"
        f"- Courier message: {courier_name}\n"
        f"- Courier state now: {current_state}\n"
        f"- Is name set: {is_name_set}"
    )

    log.info(f"data_name_courier was successfully done!")


@courier_r.message(filters.StateFilter(CourierState.reg_Phone))
async def data_phone_courier(message: Message, state: FSMContext):
    log.info(f"data_phone_courier was called!")

    handler = MessageHandler(state, message.bot)
    handle_state = await state.get_state()
    bot_id = message.bot.id
    tg_id = message.from_user.id
    courier_phone = message.contact.phone_number
    current_state = CourierState.reg_City.state

    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)
    is_phone_set = await rediska.set_user_phone(bot_id, tg_id, courier_phone)

    text = (
        f"Последний шаг!\n\n"
        f"Чтобы сделать заказы максимально удобными, пожалуйста, укажите город, где вы будете работать.\n\n"
        f"<b>Ваш город:</b>"
    )

    await handler.delete_previous_message(message.chat.id)
    new_message = await message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )
    await handler.handle_new_message(new_message, message)

    log.info(
        f"\n"
        f"- Courier 🚴\n"
        f"- Handler StateFilter: {handle_state}\n"
        f"- Courier telegram ID: {tg_id}\n"
        f"- Courier message: {courier_phone}\n"
        f"- Courier state now: {current_state}\n"
        f"- Is phone set: {is_phone_set}"
    )

    log.info(f"data_phone_courier was successfully done!")


@courier_r.message(filters.StateFilter(CourierState.reg_City))
async def data_city_courier(message: Message, state: FSMContext):
    log.info(f"data_city_courier was called!")

    handler = MessageHandler(state, message.bot)
    handle_state = await state.get_state()
    bot_id = message.bot.id
    tg_id = message.from_user.id
    russian_cities = await cities.get_cities()
    city, score = await find_closest_city(message.text, russian_cities)

    if not city:
        text = f"Введите корректное название города!\n<b>Ваш город:</b>"

        new_message = await message.answer(
            text, disable_notification=True, parse_mode="HTML"
        )

        log.info(f"city name was uncorrectable: {city}\n" f"text message: {text}\n")

        await handler.delete_previous_message(message.chat.id)
        await handler.handle_new_message(new_message, message)

        return

    current_state = CourierState.reg_tou.state

    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)
    is_city_set = await rediska.set_user_city(bot_id, tg_id, city)

    reply_kb = await kb.get_courier_kb("accept_tou")
    text = (
        f"Начиная использование сервиса, вы соглашаетесь с "
        f"<a href='https://drive.google.com/file/d/1iKhjWckZhn54aYWjDFLQXL46W6J0NhhC/view?usp=sharing'>"
        f"Пользовательским соглашением и правилами использования</a>, а также "
        f"<a href='https://telegram.org/privacy'>Политикой конфиденциальности</a>.\n\n"
        f"<i>*Обращаем внимание, что любые действия, связанные с заказами, "
        f"отправкой или получением посылок, должны соответствовать законодательству "
        f"вашего государства и общепринятым этическим нормам.</i>\n\n"
    )
    await handler.delete_previous_message(message.chat.id)
    new_message = await message.answer(
        text, reply_markup=reply_kb, disable_notification=True, parse_mode="HTML"
    )
    await handler.handle_new_message(new_message, message)

    log.info(
        f"\n"
        f"- Courier 🚴\n"
        f"- Handler StateFilter: {handle_state}\n"
        f"- Courier telegram ID: {tg_id}\n"
        f"- Courier city: {city}, score: {score}\n"
        f"- Courier state now: {current_state}\n"
        f"- Is city set: {is_city_set}"
    )

    log.info(f"data_city_courier was successfully done!")


@courier_r.callback_query(F.data == "accept_tou")
async def courier_accept_tou(callback_query: CallbackQuery, state: FSMContext):
    log.info(f"courier_accept_tou was called!")

    handler = MessageHandler(state, callback_query.bot)
    bot_id = callback_query.bot.id
    tg_id = callback_query.from_user.id
    current_state = CourierState.default.state

    accept_tou = (
        "Пользовательское соглашение и правила использования сервиса - Принимаю"
    )

    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)
    await rediska.set_user_tou(bot_id, tg_id, accept_tou)
    await rediska.set_reg(bot_id, tg_id, True)

    courier_name, courier_phone, courier_city, tou = await rediska.get_user_info(
        bot_id, tg_id
    )

    is_new_courier_add = await courier_data.set_courier(
        tg_id, courier_name, courier_phone, courier_city, tou
    )

    text = (
        "Вы успешно зарегистрировались! 🎉\n\n"
        f"Имя: {courier_name}\n"
        f"Номер: {courier_phone}\n"
        f"Город: {courier_city}\n\n"
        f"▼ <b>Выберите действие ...</b>"
    )
    new_message = await callback_query.message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )
    await handler.handle_new_message(new_message, callback_query.message)

    log.info(
        f"\n"
        f"- Courier 🚴\n"
        f"- Handler F.data: {F.data}\n"
        f"- Courier telegram ID: {tg_id}\n"
        f"- Courier click: {accept_tou}\n"
        f"- Courier state now: {current_state}\n"
        f"- Is new courier add: {is_new_courier_add}"
    )

    log.info(f"courier_accept_tou was successfully done!")


# ---


@courier_r.message(F.text == "/run")
@courier_r.callback_query(F.data == "lets_go")
async def cmd_run(event: Message | CallbackQuery, state: FSMContext):
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
    reply_kb = await kb.get_courier_kb(text="/run")

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


@courier_r.message(
    F.content_type == ContentType.LOCATION, filters.StateFilter(CourierState.location)
)
async def get_location(message: Message, state: FSMContext):
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)

    courier_tg_id = message.from_user.id
    my_lon = message.location.longitude
    my_lat = message.location.latitude
    radius_km = 5

    # Получаем доступные заказы
    available_orders = await order_data.get_available_orders(
        courier_tg_id, my_lat, my_lon, radius_km=radius_km
    )

    orders = []
    order_ids = []

    for index, order in enumerate(available_orders, start=1):
        order_ids.append(order.order_id)

        order_forma = (
            f"<b>{index}/{len(available_orders)}</b>\n"
            f"<b>Заказ: №{order.order_id}</b>\n"
            f"---------------------------------------------\n\n"
            f"<b>Город:</b> {order.order_city}\n\n"
            f"<b>Заказчик:</b> {order.customer_name}\n"
            f"<b>Телефон:</b> <i>*Доступен после принятия.</i>\n\n"
            f"⦿ <b>Адрес 1:</b> <a href='{order.a_url}'>{order.starting_point_a}</a>\n"
        )

        if order.destination_point_b:
            order_forma += f"⦿ <b>Адрес 2:</b> <a href='{order.b_url}'>{order.destination_point_b}</a>\n"
        if order.destination_point_c:
            order_forma += f"⦿ <b>Адрес 3:</b> <a href='{order.c_url}'>{order.destination_point_c}</a>\n"

        order_forma += (
            f"\n<b>Доставляем:</b> {order.delivery_object if order.delivery_object else '...'}\n"
            f"<b>Расстояние:</b> {order.distance_km} км\n"
            f"<b>Стоимость доставки:</b> {order.price_rub}₽\n\n"
            f"<b>Описание:</b> {order.description if order.description else '...'}\n\n"
            f"---------------------------------------------\n"
            f"• Принимайте оплату наличными или переводом.\n\n"
            f"<a href='{order.full_rout}'>Маршрут доставки</a>\n\n"
        )

        orders.append(order_forma)

    if not orders:
        await asyncio.sleep(1)
        new_message = await message.answer(
            "Нет доступных заказов в вашем радиусе.", disable_notification=True
        )
        await handler.handle_new_message(new_message, message)
        return

    counter = 0
    await state.update_data(orders=orders, order_ids=order_ids, counter=counter)

    # Логируем перед отправкой
    log.info(
        f"Курьер {courier_tg_id} видит {len(orders)} доступных заказов. Показан первый заказ с индексом {counter}."
    )

    reply_kb = await kb.get_courier_kb(
        text="one_order" if len(orders) == 1 else "available_orders"
    )

    await asyncio.sleep(1)
    handler = MessageHandler(state, message.bot)
    new_message = await message.answer(
        orders[counter],
        reply_markup=reply_kb,
        parse_mode="HTML",
        disable_notification=True,
    )
    await handler.handle_new_message(new_message, message)

    # Логируем, что сообщение отправлено
    log.info(f"Курьер {courier_tg_id} получил сообщение о первом заказе.")


@courier_r.callback_query(
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


@courier_r.callback_query(
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


@courier_r.callback_query(F.data == "accept_order")
async def accept_order(callback_query: CallbackQuery, state: FSMContext):
    # Получаем текущие данные состояния
    data = await state.get_data()
    order_ids = data.get("order_ids", [])
    counter = data.get("counter", 0)
    courier_tg_id = callback_query.from_user.id

    # Логирование данных перед обработкой
    log.info(f"Курьер {courier_tg_id} нажал на кнопку 'Принять заказ'.")
    log.info(f"Заказов найдено: {len(order_ids)}, текущий индекс: {counter}")

    # Проверка наличия заказов
    if not order_ids:
        log.warning(f"Курьер {courier_tg_id} не имеет доступных заказов.")
        await callback_query.answer("Заказы не найдены.", show_alert=True)
        return

    # Проверка на правильность индекса
    if counter >= len(order_ids):
        log.warning(
            f"Курьер {courier_tg_id} передал неверный индекс для заказа: {counter}."
        )
        await callback_query.answer("Неверный индекс для заказа.", show_alert=True)
        return

    order_id = order_ids[counter]
    log.info(f"Курьер {courier_tg_id} принял заказ с ID: {order_id}.")

    try:
        # Назначаем курьера к заказу
        log.info(f"Назначаем курьера {courier_tg_id} на заказ с ID {order_id}.")
        await order_data.assign_courier_to_order(
            order_id=order_id, courier_tg_id=courier_tg_id
        )

        # Обновляем статус заказа на "В работе"
        log.info(f"Обновляем статус заказа {order_id} на 'В работе'.")
        await order_data.update_order_status(
            order_id=order_id, new_status=OrderStatus.IN_PROGRESS
        )

        # Получаем номер телефона заказчика
        customer_phone = await order_data.get_order_customer_phone(order_id)
        log.info(
            f"Получен номер телефона заказчика для заказа {order_id}: {customer_phone}"
        )

        # Получаем tg_id по номеру телефона
        customer_tg_id = await customer_data.get_user_tg_id_by_phone(customer_phone)
        log.info(f"Получен tg_id заказчика: {customer_tg_id}")

        # Отправляем уведомление заказчику
        notification_text = (
            f"Ваш заказ №{order_id} был принят курьером!\n"
            f"Подробности смотрите в Моих заказах\n\n"
            f"<i>*Сообщение удалится через 15 минут</i>"
        )
        notification_message = await customer_bot.send_message(
            chat_id=customer_tg_id, text=notification_text, parse_mode="HTML"
        )
        log.info(
            f"Отправлено уведомление заказчику {customer_tg_id} о принятии заказа."
        )

        # Уведомляем курьера о принятии заказа
        new_message = await callback_query.message.answer(
            "Заказ принят. Вы закреплены за этим заказом.",
            parse_mode="HTML",
            disable_notification=False,
        )
        log.info(f"Уведомление курьеру {courier_tg_id}: 'Заказ принят'.")

        # Обновляем состояние
        await state.set_state(CourierState.default)

        handler = MessageHandler(state, callback_query.message.bot)
        await handler.handle_new_message(new_message, callback_query.message)

        # Удаляем уведомление спустя 1 час
        await asyncio.sleep(900)  # Ожидаем 15 минут
        try:
            await customer_bot.delete_message(
                chat_id=customer_tg_id, message_id=notification_message.message_id
            )
            log.info(
                f"Удалено уведомление для заказчика {customer_tg_id} с ID сообщения {notification_message.message_id}."
            )
        except Exception as e:
            log.error(f"Ошибка при удалении сообщения: {e}")

    except ValueError as e:
        log.error(f"ValueError при принятии заказа {order_id}: {e}")
        await callback_query.answer(str(e), show_alert=True)
    except Exception as e:
        log.error(f"Ошибка при принятии заказа {order_id}: {e}")
        await callback_query.answer("Ошибка при принятии заказа.", show_alert=True)


# ---


@courier_r.message(F.text == "/my_orders")
@courier_r.callback_query(F.data == "back_myOrders")
async def handle_my_orders(event, state: FSMContext):
    log.info(f"handle_my_orders was called!")

    is_callback = isinstance(event, CallbackQuery)
    tg_id = event.from_user.id
    chat_id = event.message.chat.id if is_callback else event.chat.id
    bot = event.bot
    bot_id = event.bot.id
    current_state = CourierState.myOrders.state

    if not is_callback:
        handler = MessageHandler(state, bot)
        await handler.delete_previous_message(chat_id)

    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)

    active_count = len(await order_data.get_active_orders(tg_id))
    completed_count = len(await order_data.get_completed_orders(tg_id))

    reply_kb = await kb.get_courier_orders_kb(active_count, completed_count)
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

    if not is_callback:
        handler = MessageHandler(state, bot)
        await handler.handle_new_message(new_message, event)
    else:
        await event.answer()

    log.info(
        f"\n"
        f"- Courier 🚴\n"
        f"- Courier telegram ID: {tg_id}\n"
        f"- Courier event info: {event.data if is_callback else event.text}\n"
        f"- Courier state now: {current_state}\n"
    )

    log.info(f"handle_my_orders was successfully done!")


@courier_r.callback_query(
    F.data.in_(
        {
            "active_orders",
            "completed_orders",
        }
    )
)
async def get_orders(callback_query: CallbackQuery, state: FSMContext):
    log.info(f"get_orders was called!")

    data = await state.get_data()

    if callback_query.data in {"next_right_mo", "back_left_mo"}:
        counter = data.get("counter", 0)
        orders_data = data.get("orders_data", [])

        if not orders_data:
            log.warning("Нет доступных заказов для переключения")
            await callback_query.answer("Нет доступных заказов.", show_alert=True)
            return

        total_orders = len(orders_data)
        counter = (
            (counter + 1) % total_orders
            if callback_query.data == "next_right_mo"
            else (counter - 1) % total_orders
        )
        await state.update_data(counter=counter)

        log.info(f"Переключение заказа: counter={counter}, total_orders={total_orders}")
        await callback_query.message.edit_text(
            orders_data[counter][0],
            reply_markup=await kb.get_courier_kb("one_my_order"),
            disable_notification=True,
            parse_mode="HTML",
        )
        log.info(
            f"Конец выполнения get_orders: успешно переключен заказ #{counter + 1}"
        )
        return

    order_status_mapping = {
        "active_orders": (
            order_data.get_active_orders,
            CourierState.myOrders_active,
            "активных",
        ),
        "completed_orders": (
            order_data.get_completed_orders,
            CourierState.myOrders_completed,
            "завершённых",
        ),
    }

    get_orders_func, state_status, status_text = order_status_mapping.get(
        callback_query.data, (None, None, "")
    )
    if not get_orders_func:
        log.error(f"Неизвестный тип заказа: {callback_query.data}")
        await callback_query.answer("Ошибка запроса заказов.", show_alert=True)
        return

    tg_id = callback_query.from_user.id
    bot_id = callback_query.bot.id
    current_status = state_status if state_status else CourierState.default.state
    courier_orders = await get_orders_func(tg_id)

    await state.set_state(state_status)
    await rediska.set_state(bot_id, tg_id, current_status)
    await rediska.save_fsm_state(state, bot_id, tg_id)

    orders_data = []
    for index, order in enumerate(courier_orders, start=1):
        order_forma = (
            f"<b>{index}/{len(courier_orders)}</b>\n"
            f"<b>Заказ: №{order.order_id}</b>\n"
            f"---------------------------------------------\n"
            f"<b>Город:</b> {order.order_city}\n\n"
            f"<b>Заказчик:</b> {order.customer_name if order.customer_name else '-'}\n"
            f"<b>Телефон:</b> {order.customer_phone if order.customer_phone else '-'}\n\n"
            f"⦿ <b>Адрес 1:</b> <a href='{order.a_url}'>{order.starting_point_a}</a>\n"
        )

        delivery_points = [
            (order.destination_point_b, order.b_url),
            (order.destination_point_c, order.c_url),
            (order.destination_point_d, order.d_url),
            (order.destination_point_e, order.e_url),
        ]

        for i, (point, url) in enumerate(delivery_points, start=2):
            if point:
                order_forma += f"⦿ <b>Адрес {i}:</b> <a href='{url}'>{point}</a>\n"

        order_forma += (
            f"\n<b>Доставляем:</b> {order.delivery_object if order.delivery_object else '...'}\n"
            f"<b>Расстояние:</b> {order.distance_km} км\n"
            f"<b>Стоимость доставки:</b> {order.price_rub}₽\n\n"
            f"<b>Описание:</b> {order.description if order.description else '...'}\n\n"
            f"---------------------------------------------\n"
            f"• Принимайте оплату наличными или переводом.\n\n"
            f"⦿ <a href='{order.full_rout}'>Маршрут доставки</a>\n"
        )

        orders_data.append((order_forma, order.order_id))

    if not orders_data:
        log.info(f"Нет {status_text} заказов для пользователя tg_id={tg_id}")
        await callback_query.message.edit_text(
            f"У вас нет {status_text} заказов.",
            reply_markup=await kb.get_courier_kb("one_my_order"),
            disable_notification=True,
        )
        log.info(f"Конец выполнения get_orders: заказов не найдено")
        return

    await state.update_data(orders_data=orders_data, counter=0)
    reply_kb = await kb.get_courier_kb(
        "one_my_order" if len(orders_data) == 1 else callback_query.data
    )

    log.info(f"Отображение первого заказа: total_orders={len(orders_data)}")
    await callback_query.message.edit_text(
        orders_data[0][0],
        reply_markup=reply_kb,
        disable_notification=True,
        parse_mode="HTML",
    )

    log.info(f"get_orders was successfully done!")


@courier_r.callback_query(F.data.in_({"next_right_mo", "back_left_mo"}))
async def handle_order_navigation(callback_query: CallbackQuery, state: FSMContext):
    log.info("handle_order_navigation was called!")

    data = await state.get_data()
    orders_data = data.get("orders_data", [])
    counter = data.get("counter", 0)

    if not orders_data:
        log.warning("Нет доступных заказов для переключения")
        await callback_query.answer("Нет доступных заказов.", show_alert=True)
        return

    total_orders = len(orders_data)
    counter = (
        (counter + 1) % total_orders
        if callback_query.data == "next_right_mo"
        else (counter - 1) % total_orders
    )

    await state.update_data(counter=counter, current_order_id=orders_data[counter][1])

    await callback_query.message.edit_text(
        orders_data[counter][0],
        reply_markup=callback_query.message.reply_markup,
        parse_mode="HTML",
    )

    log.info(f"Переключение на заказ #{counter + 1}/{total_orders}")


# ---


@courier_r.callback_query(F.data == "order_delivered")
async def complete_order(callback_query: CallbackQuery, state: FSMContext):
    handler = MessageHandler(state, callback_query.message.bot)
    data = await state.get_data()
    current_order_id = data.get("current_order_id")

    # log.info(f"Состояние перед завершением заказа: {data}")
    log.info(f"current_order_id: {current_order_id}")

    # Проверка наличия активного заказа
    if not current_order_id:
        await callback_query.message.answer(
            "Не удалось найти активный заказ для завершения."
        )
        return

    try:
        # Загружаем АКТУАЛЬНЫЙ статус заказа без кэша
        order = await order_data.get_order_by_id(current_order_id)
        log.info(
            f"Попытка завершить заказ {current_order_id}, его статус: {order.order_status}"
        )

        # Проверка, что заказ ещё в процессе выполнения
        if order.order_status != OrderStatus.IN_PROGRESS:
            await callback_query.message.answer(
                f"Заказ №{current_order_id} уже завершён или находится в другом статусе. Статус: {order.order_status}.",
                parse_mode="HTML",
            )
            return

        # Обновляем статус заказа
        completed_time = datetime.now()
        await order_data.update_order_status_and_time(
            order_id=current_order_id,
            new_status=OrderStatus.COMPLETED,
            completed_time=completed_time,
        )

        # Получаем данные заказчика
        customer_phone = await order_data.get_order_customer_phone(current_order_id)
        customer_tg_id = await customer_data.get_user_tg_id_by_phone(customer_phone)

        # Уведомляем заказчика
        notification_text = (
            f"Ваш заказ №{current_order_id} был успешно доставлен курьером!\n"
            f"Спасибо, что воспользовались нашим сервисом.\n\n"
            f"<i>*Сообщение удалится через 15 минут</i>"
        )
        notification_message = await customer_bot.send_message(
            chat_id=customer_tg_id, text=notification_text, parse_mode="HTML"
        )

        # Уведомляем курьера
        await callback_query.message.answer(
            f"Статус заказа №{current_order_id} обновлен на 'Завершен'. Заказчик уведомлен.",
            parse_mode="HTML",
            disable_notification=False,
        )

        # Удаляем предыдущее сообщение курьера
        await handler.delete_previous_message(callback_query.message.chat.id)

        # Устанавливаем состояние курьера в начальное состояние
        await state.set_state(CourierState.default)

        # Удаляем уведомление заказчику через 15 минут
        await asyncio.sleep(900)
        try:
            await customer_bot.delete_message(
                chat_id=customer_tg_id, message_id=notification_message.message_id
            )
        except Exception as e:
            log.error(f"Ошибка при удалении сообщения заказчику: {e}")

    except ValueError as e:
        await callback_query.answer(str(e), show_alert=True)
    except Exception as e:
        await callback_query.answer("Ошибка при завершении заказа.", show_alert=True)
        log.error(f"Ошибка при завершении заказа: {e}")


# ---


@courier_r.message(F.text == "/profile")
async def cmd_profile(message: Message, state: FSMContext):
    log.info(f"cmd_profile was called!")

    handler = MessageHandler(state, message.bot)
    bot_id = message.bot.id
    tg_id = message.from_user.id
    current_state = CourierState.default.state

    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)

    courier_name, courier_phone, courier_city, subscription_status = (
        await courier_data.get_courier_full_info(tg_id)
    )

    text = (
        f"👤 <b>Профиль курьера</b>\n\n"
        f"Посмотрите или измените данные о себе.\n\n"
        f"<b>Имя:</b> {courier_name}\n"
        f"<b>Номер:</b> {courier_phone}\n"
        f"<b>Город:</b> {courier_city}\n"
        f"<b>Статус подписки:</b> {subscription_status}\n"
    )

    reply_kb = await kb.get_courier_kb("/profile")

    await handler.delete_previous_message(message.chat.id)

    new_message = await message.answer(
        text, reply_markup=reply_kb, disable_notification=True, parse_mode="HTML"
    )
    await handler.handle_new_message(new_message, message)

    log.info(
        f"\n"
        f"- Courier 🚴\n"
        f"- Handler F.text: {F.text}\n"
        f"- Courier telegram ID: {tg_id}\n"
        f"- Courier state now: {current_state}\n"
    )

    log.info(f"cmd_profile was successfully done!")


@courier_r.callback_query(F.data == "set_my_name")
async def set_name(callback_query: CallbackQuery, state: FSMContext):
    log.info(f"set_name was called!")

    handler = MessageHandler(state, callback_query.bot)
    bot_id = callback_query.bot.id
    tg_id = callback_query.from_user.id
    current_state = CourierState.change_Name.state

    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)

    text = f"Изменить данные профиля.\n\n" f"<b>Ваше имя:</b>"
    new_message = await callback_query.message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )
    await handler.handle_new_message(new_message, callback_query.message)

    log.info(
        f"\n"
        f"- Courier 🚴\n"
        f"- Handler F.data: {F.data}\n"
        f"- Courier telegram ID: {tg_id}\n"
        f"- Courier state now: {current_state}\n"
    )

    log.info(f"set_name was successfully done!")


@courier_r.callback_query(F.data == "set_my_phone")
async def set_phone(callback_query: CallbackQuery, state: FSMContext):
    log.info(f"set_phone was called!")

    handler = MessageHandler(state, callback_query.bot)
    bot_id = callback_query.bot.id
    tg_id = callback_query.from_user.id
    current_state = CourierState.change_Phone.state

    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)

    reply_kb = await kb.get_courier_kb("phone_number")
    text = f"Изменить данные профиля.\n\n" f"<b>Ваш Телефон:</b>"
    new_message = await callback_query.message.answer(
        text, disable_notification=True, reply_markup=reply_kb, parse_mode="HTML"
    )
    await handler.handle_new_message(new_message, callback_query.message)

    log.info(
        f"\n"
        f"- Courier 🚴\n"
        f"- Handler F.data: {F.data}\n"
        f"- Courier telegram ID: {tg_id}\n"
        f"- Courier state now: {current_state}\n"
    )

    log.info(f"set_phone was successfully done!")


@courier_r.callback_query(F.data == "set_my_city")
async def set_city(callback_query: CallbackQuery, state: FSMContext):
    log.info(f"set_city was called!")

    handler = MessageHandler(state, callback_query.bot)
    bot_id = callback_query.bot.id
    tg_id = callback_query.from_user.id
    current_state = CourierState.change_City.state

    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)

    text = f"Изменить данные профиля.\n\n" f"<b>Ваш город:</b>"
    new_message = await callback_query.message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )
    await handler.handle_new_message(new_message, callback_query.message)

    log.info(
        f"\n"
        f"- Courier 🚴\n"
        f"- Handler F.data: {F.data}\n"
        f"- Courier telegram ID: {tg_id}\n"
        f"- Courier state now: {current_state}\n"
    )

    log.info(f"set_city was successfully done!")


# ---


@courier_r.message(filters.StateFilter(CourierState.change_Name))
async def change_name(message: Message, state: FSMContext):
    log.info(f"change_name was called!")

    handler = MessageHandler(state, message.bot)
    bot_id = message.bot.id
    tg_id = message.from_user.id
    name = message.text
    current_state = CourierState.default.state

    new_name_was_set = await courier_data.update_courier_name(tg_id, name)
    new_name_was_set_redis = await rediska.set_user_name(bot_id, tg_id, name)
    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)

    log.info(f"new_name_was_set_redis: {new_name_was_set_redis}")
    text = (
        f"Имя курьера было изменено на {name} 🎉\n\n" f"▼ <b>Выберите действие ...</b>"
    )

    await handler.delete_previous_message(message.chat.id)

    new_message = await message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )

    await handler.handle_new_message(new_message, message)

    log.info(
        f"\n"
        f"- Courier 🚴\n"
        f"- Courier telegram ID: {tg_id}\n"
        f"- Courier message: {message.text}\n"
        f"- Courier state now: {current_state}\n"
        f"- new_name_was_set: {new_name_was_set}\n"
    )

    log.info(f"change_name was successfully done!")


@courier_r.message(filters.StateFilter(CourierState.change_Phone))
async def change_phone(message: Message, state: FSMContext):
    log.info(f"change_phone was called!")

    handler = MessageHandler(state, message.bot)
    bot_id = message.bot.id
    tg_id = message.from_user.id
    phone = message.contact.phone_number
    current_state = CourierState.default.state

    new_phone_was_set = await courier_data.update_courier_phone(tg_id, phone)
    new_phone_was_set_redis = await rediska.set_user_phone(bot_id, tg_id, phone)
    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)

    log.info(f"new_phone_was_set_redis: {new_phone_was_set_redis}")

    text = (
        f"Номер курьера был изменен на {phone} 🎉\n\n" f"▼ <b>Выберите действие ...</b>"
    )

    await handler.delete_previous_message(message.chat.id)

    new_message = await message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )

    await handler.handle_new_message(new_message, message)

    log.info(
        f"\n"
        f"- Courier 🚴\n"
        f"- Courier telegram ID: {tg_id}\n"
        f"- Courier message: {message.text}\n"
        f"- Courier state now: {current_state}\n"
        f"- new_phone_was_set: {new_phone_was_set}\n"
    )

    log.info(f"change_phone was successfully done!")


@courier_r.message(filters.StateFilter(CourierState.change_City))
async def change_city(message: Message, state: FSMContext):
    log.info(f"change_city was called!")

    handler = MessageHandler(state, message.bot)
    bot_id = message.bot.id
    tg_id = message.from_user.id
    russian_cities = await cities.get_cities()
    city, score = await find_closest_city(message.text, russian_cities)

    if not city:
        text = f"Введите корректное название города!\n<b>Ваш город:</b>"

        new_message = await message.answer(
            text, disable_notification=True, parse_mode="HTML"
        )

        log.info(f"city name was uncorrectable: {city}\n" f"text message: {text}\n")

        await handler.delete_previous_message(message.chat.id)
        await handler.handle_new_message(new_message, message)

        return

    current_state = CourierState.default.state

    new_city_was_set = await courier_data.update_courier_city(tg_id, city)
    new_city_was_set_redis = await rediska.set_user_city(bot_id, tg_id, city)
    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)

    log.info(f"new_city_was_set_redis: {new_city_was_set_redis}")

    text = (
        f"Город курьера был изменен на {city} 🎉\n\n" f"▼ <b>Выберите действие ...</b>"
    )

    await handler.delete_previous_message(message.chat.id)

    new_message = await message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )

    await handler.handle_new_message(new_message, message)

    log.info(
        f"\n"
        f"- Courier 🚴\n"
        f"- Courier telegram ID: {tg_id}\n"
        f"- Courier message: {message.text}\n"
        f"- Courier state now: {current_state}\n"
        f"- new_city_was_set: {new_city_was_set}\n"
    )

    log.info(f"change_city was successfully done!")


# ---


@courier_r.message(F.text == "/faq")
async def cmd_faq(message: Message, state: FSMContext):
    log.info(f"cmd_faq was called!")

    handler = MessageHandler(state, message.bot)
    bot_id = message.bot.id
    tg_id = message.from_user.id
    current_state = CourierState.default.state

    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)

    text = (
        f"🤔 <b>Вопросы и ответы</b>\n\n"
        f"Частые вопросы и ответы на них "
        f"<a href='https://drive.google.com/file/d/1cXYK_FqU7kRpTU9p04dVjcE4vRbmNvMw/view?usp=sharing'>FAQ</a>"
    )

    await handler.delete_previous_message(message.chat.id)

    new_message = await message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )
    await handler.handle_new_message(new_message, message)

    log.info(
        f"\n"
        f"- Courier 🚴\n"
        f"- Handler F.text: {F.text}\n"
        f"- Courier telegram ID: {tg_id}\n"
        f"- Courier state now: {current_state}\n"
    )

    log.info(f"cmd_faq was successfully done!")


@courier_r.message(F.text == "/rules")
async def cmd_rules(message: Message, state: FSMContext):
    log.info(f"cmd_rules was called!")

    handler = MessageHandler(state, message.bot)
    bot_id = message.bot.id
    tg_id = message.from_user.id
    current_state = CourierState.default.state

    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)

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

    await handler.delete_previous_message(message.chat.id)

    new_message = await message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )
    await handler.handle_new_message(new_message, message)

    log.info(
        f"\n"
        f"- Courier 🚴\n"
        f"- Handler F.text: {F.text}\n"
        f"- Courier telegram ID: {tg_id}\n"
        f"- Courier state now: {current_state}\n"
    )

    log.info(f"cmd_rules was successfully done!")


# ---


@payment_r.message(F.text == "/subs")
@payment_r.callback_query(F.data == "pay_sub")
async def payment_invoice(event: Message | CallbackQuery, state: FSMContext):

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

    if not payment_provider:
        log.info("Ошибка: provider_token не найден. Проверьте переменные окружения.")
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
        photo_url="https://ltdfoto.ru/images/2024/08/31/subs.jpg",
        photo_width=1200,
        photo_height=720,
        need_name=True,
        need_phone_number=True,
        need_email=True,
        reply_markup=None,
    )

    await handler.handle_new_message(
        new_message, event if isinstance(event, Message) else event.message
    )


@payment_r.pre_checkout_query()
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


@payment_r.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: Message, state: FSMContext):
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)
    ttl = await title.get_title_courier("success_payment")
    text = f"Cпасибо за подписку!\nСумма: {message.successful_payment.total_amount // 100}{message.successful_payment.currency}"
    reply_kb = await kb.get_courier_kb(text="success_payment")
    new_message = await message.answer_photo(
        photo=ttl, caption=text, reply_markup=reply_kb
    )
    await handler.handle_new_message(new_message, message)


# ---


@courier_fallback.message()
async def handle_unrecognized_message(message: Message):
    await message.delete()
