from ._deps import (
    asyncio,
    CommandStart,
    FSMContext,
    ContentType,
    ReplyKeyboardRemove,
    filters,
    Message,
    CallbackQuery,
    OrderStatus,
    CourierState,
    CourierOuterMiddleware,
    PreCheckoutQuery,
    LabeledPrice,
    zlib,
    Time,
    handler,
    courier_r,
    courier_fallback,
    courier_data,
    payment_r,
    kb,
    title,
    courier_bot,
    courier_bot_id,
    order_data,
    rediska,
    cities,
    payment_provider,
    log,
    F,
    find_closest_city,
    customer_bot,
)


# ---
# ---


courier_r.message.outer_middleware(CourierOuterMiddleware(rediska))
courier_r.callback_query.outer_middleware(CourierOuterMiddleware(rediska))


# ---
# ---


@courier_r.message(CommandStart())
async def cmd_start_courier(message: Message, state: FSMContext):

    current_state = CourierState.reg_state.state
    tg_id = message.from_user.id
    chat_id = message.chat.id

    is_reg = await rediska.is_reg(courier_bot_id, tg_id)

    if is_reg:
        current_state = CourierState.default.state
        text = "▼ <b>Выберите действие ...</b>"
        new_message = await message.answer(
            text, parse_mode="HTML", disable_notification=True
        )
    else:
        current_state = CourierState.reg_state.state
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
        new_message = await message.answer_photo(
            photo=photo_title,
            caption=text,
            reply_markup=reply_kb,
            parse_mode="HTML",
            disable_notification=True,
        )

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)

    await handler.catch(
        bot=courier_bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=message,
        delete_previous=True,
    )


@courier_r.callback_query(F.data == "reg")
async def data_reg_courier(callback_query: CallbackQuery, state: FSMContext):

    await callback_query.answer("✍️ Регистрация", show_alert=False)

    current_state = CourierState.reg_Name.state
    tg_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)

    text = (
        "Пройдите небольшую регистрацию.\n"
        "Это не займет много времени.\n\n"
        "<b>Как вас зовут?</b>"
    )
    new_message = await callback_query.message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )

    await handler.catch(
        bot=courier_bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=callback_query.message,
        delete_previous=False,
    )


@courier_r.message(filters.StateFilter(CourierState.reg_Name))
async def data_name_courier(message: Message, state: FSMContext):

    current_state = CourierState.reg_Phone.state
    tg_id = message.from_user.id
    chat_id = message.chat.id
    courier_name = message.text

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)
    _ = await rediska.set_name(courier_bot_id, tg_id, courier_name)

    reply_kb = await kb.get_courier_kb("phone_number")
    text = (
        f"Привет, {courier_name}!👋\n\nЧтобы начать работу, пожалуйста, укажите ваш номер телефона для связи.\n\n"
        f"<i>*При регистрации с компьютера нажмите на значок команд рядом с полем ввода.</i>\n\n"
        f"<i>*Отправка номера возможно только по клику на кнопку 'Поделится номером'!</i>\n\n"
        f"<b>Ваш номер:</b>"
    )

    new_message = await message.answer(
        text,
        disable_notification=True,
        reply_markup=reply_kb,
        parse_mode="HTML",
    )

    await handler.catch(
        bot=courier_bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=message,
        delete_previous=True,
    )


@courier_r.message(filters.StateFilter(CourierState.reg_Phone))
async def data_phone_courier(message: Message, state: FSMContext):

    current_state = CourierState.reg_City.state
    tg_id = message.from_user.id
    chat_id = message.chat.id
    courier_phone = message.contact.phone_number

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)
    _ = await rediska.set_phone(courier_bot_id, tg_id, courier_phone)

    text = (
        f"Последний шаг!\n\n"
        f"Чтобы сделать заказы максимально удобными, пожалуйста, укажите город, где вы будете работать.\n\n"
        f"<b>Ваш город:</b>"
    )

    new_message = await message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )

    await handler.catch(
        bot=courier_bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=message,
        delete_previous=True,
    )


@courier_r.message(filters.StateFilter(CourierState.reg_City))
async def data_city_courier(message: Message, state: FSMContext):

    current_state = CourierState.reg_tou.state
    tg_id = message.from_user.id
    chat_id = message.chat.id
    russian_cities = await cities.get_cities()
    city, _ = await find_closest_city(message.text, russian_cities)

    if not city:
        text = f"Введите корректное название города!\n<b>Ваш город:</b>"

        new_message = await message.answer(
            text, disable_notification=True, parse_mode="HTML"
        )

        log.info(f"city name was uncorrectable: {city}\n" f"text message: {text}\n")

        return

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)

    _ = await rediska.set_city(courier_bot_id, tg_id, city)

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

    new_message = await message.answer(
        text, reply_markup=reply_kb, disable_notification=True, parse_mode="HTML"
    )

    await handler.catch(
        bot=courier_bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=message,
        delete_previous=True,
    )


@courier_r.callback_query(F.data == "accept_tou")
async def courier_accept_tou(callback_query: CallbackQuery, state: FSMContext):

    current_state = CourierState.default.state
    tg_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id

    accept_tou = (
        "Пользовательское соглашение и правила использования сервиса - Принимаю"
    )

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)
    await rediska.set_tou(courier_bot_id, tg_id, accept_tou)
    await rediska.set_reg(courier_bot_id, tg_id, True)

    courier_name, courier_phone, courier_city, tou = await rediska.get_user_info(
        courier_bot_id, tg_id
    )
    _ = await courier_data.set_courier(
        tg_id,
        courier_name,
        courier_phone,
        courier_city,
        tou,
    )

    _ = await courier_data.update_courier_subscription(tg_id, days=30)

    reply_kb = await kb.get_courier_kb("super_go")
    text = (
        "Вы успешно зарегистрировались! 🎉\n\n"
        "Как новый курьер, вы получаете 30-дневный бесплатный период! 🚀 \n"
        "Это отличный шанс попробовать все на практике без затрат! 🤑 \n"
        "Работайте в удобное время, получайте заказы и зарабатывайте без платы за подписку! 💸 \n"
        "Оцените все преимущества нашего сервиса и начните зарабатывать прямо сейчас! ✨"
    )

    new_message = await callback_query.message.answer(
        text,
        reply_markup=reply_kb,
        disable_notification=True,
        parse_mode="HTML",
    )

    await callback_query.answer("✅ Принято", show_alert=False)

    await handler.catch(
        bot=courier_bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=callback_query.message,
        delete_previous=False,
    )


@courier_r.callback_query(F.data == "super_go")
async def courier_super_go(callback_query: CallbackQuery, state: FSMContext):

    await callback_query.answer("⭐️⭐️⭐️", show_alert=False)

    current_state = CourierState.default.state
    tg_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    moscow_time = await Time.get_moscow_time()

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)

    courier_name, courier_phone, courier_city, end_date = (
        await courier_data.get_courier_full_info(tg_id)
    )

    if end_date and end_date >= moscow_time:
        remaining_days = (end_date - moscow_time).days
        subscription_status = (
            f"<b>Подписка:</b> Активна 🚀\n\n"
            f"📅 Действует до: {end_date.strftime('%d.%m.%Y')}\n"
            f"🕒 Осталось дней: {remaining_days}\n\n"
        )
    else:
        subscription_status = "<b>Подписка:</b> Не активна\n\n"

    text = (
        f"Имя: {courier_name}\n"
        f"Номер: {courier_phone}\n"
        f"Город: {courier_city}\n"
        f"{subscription_status}"
        f"▼ <b>Выберите действие ...</b>"
    )
    new_message = await callback_query.message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )

    await handler.catch(
        bot=courier_bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=callback_query.message,
        delete_previous=False,
    )


# ---
# ---


@courier_r.message(F.text == "/run")
@courier_r.callback_query(F.data == "lets_go")
async def cmd_run(event: Message | CallbackQuery, state: FSMContext):

    current_state = CourierState.location.state
    chat_id = event.chat.id if isinstance(event, Message) else event.message.chat.id
    tg_id = event.from_user.id
    current_active_orders_count = await courier_data.get_courier_active_orders_count(
        tg_id
    )

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)

    reply_kb = await kb.get_courier_kb("/run")

    if current_active_orders_count < 2:

        new_message = await event.bot.send_message(
            chat_id=chat_id,
            text="Пожалуйста, отправьте вашу текущую локацию, чтобы мы могли назначить вам ближайшие заказы.\n\n"
            "<i>*Доступно только с мобильных устройств</i>",
            reply_markup=reply_kb,
            disable_notification=True,
            parse_mode="HTML",
        )
    else:

        new_message = await event.bot.send_message(
            chat_id=chat_id,
            text="Вы уже выполняете максимальное количество заказов.\n\n"
            "Пожалуйста, завершите текущие заказы, чтобы начать новые.",
            disable_notification=True,
            parse_mode="HTML",
        )

    delete_previous = False

    if isinstance(event, CallbackQuery):
        delete_previous = False
        await event.answer("🚀 Начать работу", show_alert=False)
    else:
        delete_previous = True

    await handler.catch(
        bot=courier_bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=None if isinstance(event, CallbackQuery) else event,
        delete_previous=delete_previous,
    )


@courier_r.message(
    F.content_type == ContentType.LOCATION,
    filters.StateFilter(CourierState.location),
)
async def get_location(message: Message, state: FSMContext):

    current_state = CourierState.default.state

    tg_id = message.from_user.id
    chat_id = message.chat.id

    courier_tg_id = message.from_user.id
    courier_city = await courier_data.get_courier_city(courier_tg_id)

    my_lon = message.location.longitude
    my_lat = message.location.latitude
    radius_km = 5

    available_orders = await order_data.get_available_orders(my_lat, my_lon, radius_km)

    await state.set_state(current_state)
    await state.update_data(available_orders=available_orders)
    await rediska.set_state(courier_bot_id, tg_id, current_state)
    await rediska.save_fsm_state(state, courier_bot_id, courier_tg_id)

    city_orders = await order_data.get_pending_orders_in_city(courier_city)

    text = (
        f"<b>📋 Заказы</b>\n\n"
        f"Всего заказов в городе <b>{courier_city}</b>: <b>{len(city_orders)}</b>\n"
        f"Заказов рядом с вами: <b>{len(available_orders)}</b>\n\n"
        f"🔍 Хотите посмотреть заказы рядом?"
    )

    reply_markup = await kb.get_courier_orders_near_kb(
        available_orders=len(available_orders)
    )

    new_message = await message.answer(
        text,
        reply_markup=reply_markup,
        disable_notification=True,
        parse_mode="HTML",
    )

    await handler.catch(
        bot=courier_bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=message,
        delete_previous=True,
    )


@courier_r.callback_query(F.data == "show_nearby_orders")
async def show_nearby_orders(callback_query: CallbackQuery, state: FSMContext):

    current_state = CourierState.available_orders.state
    data = await state.get_data()
    tg_id = callback_query.from_user.id
    bot_id = callback_query.bot.id
    available_orders = data.get("available_orders", {})

    if not available_orders or not isinstance(available_orders, dict):

        await callback_query.answer(
            "Нет доступных заказов в вашем радиусе.",
            show_alert=True,
        )

    else:
        len_available_orders = len(available_orders)
        orders_data = {}
        order_ids = list(available_orders.keys())
        for index, order_id in enumerate(order_ids, start=1):
            order_forma = available_orders[order_id]["text"]
            order_text = (
                f"<b>{index}/{len_available_orders}</b>\n"
                f"<b>Заказ: №{order_id}</b>\n"
                f"---------------------------------------------\n\n"
                f"{order_forma}"
            )
            orders_data[order_id] = {"text": order_text, "index": index}

        await state.set_state(current_state)
        await state.update_data(
            orders_data=orders_data,
            order_ids=order_ids,
            current_index=0,
            current_order_id=order_ids[0],
        )
        await rediska.save_fsm_state(state, bot_id, tg_id)

        first_order_id = order_ids[0]
        reply_markup = await kb.get_courier_kb(
            "one_order" if len(order_ids) == 1 else "available_orders"
        )

        await callback_query.answer(
            f"📍 Заказы рядом {len_available_orders}", show_alert=False
        )

        await callback_query.message.edit_text(
            orders_data[first_order_id]["text"],
            reply_markup=reply_markup,
            parse_mode="HTML",
        )


@courier_r.callback_query(F.data.in_({"next_right", "back_left"}))
async def handle_order_available_navigation(
    callback_query: CallbackQuery, state: FSMContext
):

    current_state = CourierState.available_orders.state
    tg_id = callback_query.from_user.id
    data = await state.get_data()
    orders_data = data.get("orders_data", {})
    order_ids = list(orders_data.keys())
    current_index = data.get("current_index", 0)

    if not orders_data or not order_ids:
        log.warning(f"❌ Нет доступных заказов.")
        await callback_query.answer("Нет доступных заказов.", show_alert=True)
        return

    total_orders = len(orders_data)

    if callback_query.data == "next_right":
        new_index = (current_index + 1) % total_orders
        await callback_query.answer(
            f"{new_index+1}/{total_orders} ⏩", show_alert=False
        )

    else:
        new_index = (current_index - 1) % total_orders
        await callback_query.answer(
            f"⏪ {new_index+1}/{total_orders}", show_alert=False
        )

    new_order_id = order_ids[new_index]
    await state.set_state(current_state)
    await state.update_data(current_index=new_index, current_order_id=new_order_id)
    await rediska.set_state(courier_bot_id, tg_id, current_state)
    await rediska.save_fsm_state(state, courier_bot_id, tg_id)

    reply_markup = await kb.get_courier_kb(
        "available_orders" if total_orders > 1 else "one_order"
    )

    await callback_query.message.edit_text(
        orders_data[new_order_id]["text"],
        reply_markup=reply_markup,
        parse_mode="HTML",
    )


@courier_r.callback_query(F.data == "accept_order")
async def accept_order(callback_query: CallbackQuery, state: FSMContext):

    current_state = CourierState.default.state
    data = await state.get_data()
    order_ids: list = data.get("order_ids", [])
    current_order_id = int(data.get("current_order_id"))
    tg_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)

    if not order_ids:
        await callback_query.answer("Заказы не найдены.", show_alert=True)
        return

    if current_order_id not in order_ids:
        await callback_query.answer("Неверный id для заказа.", show_alert=False)
        return

    try:

        is_assigned = await order_data.assign_courier_to_order(
            order_id=current_order_id,
            tg_id=tg_id,
        )

        if not is_assigned:
            await callback_query.message.answer(
                "К сожалению, заказ уже был принят другим курьером.", parse_mode="HTML"
            )
            return

        await order_data.update_order_status_and_started_time(
            order_id=current_order_id,
            new_status=OrderStatus.IN_PROGRESS,
        )

        customer_tg_id = await order_data.get_customer_tg_id(current_order_id)
        await customer_bot.send_message(
            chat_id=customer_tg_id,
            text=f"Ваш заказ №{current_order_id} был принят курьером!",
            parse_mode="HTML",
        )

        order_ids.remove(current_order_id)

        text = (
            f"<b>✅ Заказ №{current_order_id} принят!</b>\n\n"
            f"<i>*Подробности в меню</i> <b>Мои заказы</b>\n"
        )

        new_message = await callback_query.message.answer(text=text, parse_mode="HTML")

        await state.update_data(
            order_ids=order_ids,
            current_order_id=None if not order_ids else order_ids[0],
        )
        await rediska.save_fsm_state(state, courier_bot_id, tg_id)

        await courier_data.change_order_active_count(tg_id, count=1)

        await handler.catch(
            bot=courier_bot,
            chat_id=chat_id,
            user_id=tg_id,
            new_message=new_message,
            current_message=callback_query.message,
            delete_previous=False,
        )

        await callback_query.answer("✅ Заказ принят", show_alert=False)

    except Exception as e:
        log.error(f"Ошибка при принятии заказа {current_order_id}: {e}")
        await callback_query.answer("Ошибка при принятии заказа.", show_alert=True)


# ---
# ---


@courier_r.message(F.text == "/my_orders")
@courier_r.callback_query(F.data == "back_myOrders")
async def cmd_my_orders(event: Message | CallbackQuery, state: FSMContext):

    current_state = CourierState.myOrders.state
    is_callback = isinstance(event, CallbackQuery)
    tg_id = event.from_user.id
    chat_id = event.message.chat.id if is_callback else event.chat.id

    if is_callback:
        await event.answer("🔙 Назад", show_alert=False)

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)

    active_count = len(await order_data.get_active_orders(tg_id))
    completed_count = len(await order_data.get_completed_orders(tg_id))

    reply_markup = await kb.get_courier_orders_kb(active_count, completed_count)
    text = (
        f"✎  <b>Мои заказы</b>\n\n"
        f"Здесь вы можете посмотреть статус ваших заказов, "
        f"а также статистику их выполнения.\n\n"
        f"<b>Статус ваших заказов:</b>"
    )

    new_message = (
        await event.message.edit_text(
            text,
            reply_markup=reply_markup,
            disable_notification=True,
            parse_mode="HTML",
        )
        if is_callback
        else await event.answer(
            text,
            reply_markup=reply_markup,
            disable_notification=True,
            parse_mode="HTML",
        )
    )

    await handler.catch(
        bot=courier_bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=None if isinstance(event, CallbackQuery) else event,
        delete_previous=False if is_callback else True,
    )


@courier_r.callback_query(F.data.in_({"active_orders", "completed_orders"}))
async def get_my_orders(callback_query: CallbackQuery, state: FSMContext):

    tg_id = callback_query.from_user.id

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

    courier_orders = await get_orders_func(tg_id)

    orders_data = {}
    for index, order in enumerate(courier_orders, start=1):
        try:
            order_forma = (
                zlib.decompress(order.order_forma).decode("utf-8")
                if order.order_forma
                else "-"
            )
        except Exception as e:
            log.error(
                f"Ошибка декодирования order_formа для заказа {order.order_id}: {e}"
            )
            order_forma = "-"

        base_info = (
            f"<b>{index}/{len(courier_orders)}</b>\n"
            f"<b>Заказ: №{order.order_id}</b>\n"
            f"---------------------------------------------\n"
            f"{order_forma}"
        )
        orders_data[order.order_id] = {
            "text": base_info,
            "index": index - 1,
        }

    if not orders_data:
        await callback_query.answer(
            f"У вас нет {status_text} заказов.",
            disable_notification=True,
            show_alert=False,
        )
        return

    else:

        if callback_query.data == "active_orders":
            text_answer = "📋 Активные"
        elif callback_query.data == "completed_orders":
            text_answer = "📋 Завершенные"
        await callback_query.answer(text_answer, show_alert=False)

    first_order_id = list(orders_data.keys())[0]
    await state.update_data(
        orders_data=orders_data,
        counter=0,
        current_order_id=first_order_id,
    )

    await state.set_state(state_status)
    await rediska.save_fsm_state(
        state,
        courier_bot_id,
        tg_id,
    )

    if callback_query.data == "active_orders":
        reply_markup = await kb.get_courier_kb(
            "active_one" if len(orders_data) == 1 else "active_orders"
        )
    else:
        reply_markup = await kb.get_courier_kb(
            "one_my_order" if len(orders_data) == 1 else "completed_orders"
        )

    await callback_query.message.edit_text(
        orders_data[first_order_id]["text"],
        reply_markup=reply_markup,
        disable_notification=True,
        parse_mode="HTML",
    )


@courier_r.callback_query(F.data.in_({"next_right_mo", "back_left_mo"}))
async def handle_order_navigation(callback_query: CallbackQuery, state: FSMContext):

    tg_id = callback_query.from_user.id

    data = await state.get_data()
    orders_data: dict = data.get("orders_data", {})
    current_order_id = data.get("current_order_id")

    if not orders_data or not current_order_id:
        log.warning("Нет доступных заказов для переключения")
        await callback_query.answer("Нет доступных заказов.", show_alert=True)
        return

    total_orders = len(orders_data)

    order_ids = list(orders_data.keys())

    current_index = order_ids.index(current_order_id)
    if callback_query.data == "next_right_mo":
        new_index = (current_index + 1) % total_orders
        await callback_query.answer(
            f"{new_index+1}/{total_orders} ⏩", show_alert=False
        )
    else:
        new_index = (current_index - 1) % total_orders
        await callback_query.answer(
            f"⏪ {new_index+1}/{total_orders}", show_alert=False
        )

    next_order_id = order_ids[new_index]

    await state.update_data(current_order_id=next_order_id, counter=new_index)
    await rediska.save_fsm_state(state, courier_bot_id, tg_id)

    await callback_query.message.edit_text(
        orders_data[next_order_id]["text"],
        reply_markup=callback_query.message.reply_markup,
        parse_mode="HTML",
    )


# ---
# ---


@courier_r.callback_query(F.data == "order_delivered")
async def complete_order(callback_query: CallbackQuery, state: FSMContext):

    data = await state.get_data()
    current_order_id = data.get("current_order_id")
    tg_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    current_state = CourierState.default.state

    if not current_order_id:
        await callback_query.message.answer(
            "Не удалось найти активный заказ для завершения."
        )
        return

    try:

        order = await order_data.get_order_by_id(current_order_id)

        current_time = await Time.get_moscow_time()

        execution_time_hours = (
            current_time - order.started_at_moscow_time
        ).total_seconds() / 3600
        speed = order.distance_km / execution_time_hours

        AVERAGE_SPEED_KMH = 8
        SPEED_MULTIPLIER = 5

        if speed > AVERAGE_SPEED_KMH * SPEED_MULTIPLIER:
            log.warning(
                f"Заказ {current_order_id} завершён слишком быстро (скорость {speed:.2f} км/ч)"
            )
            await callback_query.answer(
                f"‼️Внимание‼️\n\n"
                f"Вы пытаетесь завершить заказ слишком рано.\n"
                f"Подобные действия рассматриваются как нарушение правил.\n"
                f"При повторных попытках возможны штрафные санкции и блокировка профиля!",
                show_alert=True,
            )
            return

        if order.order_status != OrderStatus.IN_PROGRESS:
            await callback_query.message.answer(
                f"Заказ №{current_order_id} уже завершён или находится в другом статусе. Статус: {order.order_status}.",
                parse_mode="HTML",
            )
            return

        await order_data.update_order_status_and_completed_time(
            order_id=current_order_id,
            new_status=OrderStatus.COMPLETED,
        )
        customer_tg_id = await order_data.get_customer_tg_id(order.order_id)

        notification_text = f"Ваш заказ №{current_order_id} был доставлен курьером!\n"
        notification_message = await customer_bot.send_message(
            chat_id=customer_tg_id, text=notification_text, parse_mode="HTML"
        )

        new_message = await callback_query.message.answer(
            f"<b>✅ Заказ №{current_order_id} доставлен</b>!",
            disable_notification=False,
            parse_mode="HTML",
        )

        await courier_data.change_order_active_count(tg_id, count=-1)
        await state.set_state(current_state)
        await rediska.set_state(courier_bot_id, tg_id, current_state)

        await callback_query.answer("👍 Заказ завершен", show_alert=False)

        await handler.catch(
            bot=courier_bot,
            chat_id=chat_id,
            user_id=tg_id,
            new_message=new_message,
            current_message=callback_query.message,
            delete_previous=False,
        )

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
# ---


@courier_r.message(F.text == "/profile")
async def cmd_profile(message: Message, state: FSMContext):

    current_state = CourierState.default.state
    tg_id = message.from_user.id
    chat_id = message.chat.id
    moscow_time = await Time.get_moscow_time()

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)

    courier_name, courier_phone, courier_city, end_date = (
        await courier_data.get_courier_full_info(tg_id)
    )

    if end_date and end_date >= moscow_time:
        remaining_days = (end_date - moscow_time).days
        subscription_status = f"<b>Подписка:</b> Активна 🚀\n📅 Действует до: {end_date.strftime('%d.%m.%Y')}\n🕒 Осталось дней: {remaining_days}\n\n"
    else:
        subscription_status = "<b>Подписка:</b> Не активна\n\n"

    text = (
        f"👤 <b>Профиль курьера</b>\n\n"
        f"Посмотрите или измените данные о себе.\n\n"
        f"<b>Имя:</b> {courier_name}\n"
        f"<b>Номер:</b> {courier_phone}\n"
        f"<b>Город:</b> {courier_city}\n\n"
        f"{subscription_status}"
    )

    reply_kb = await kb.get_courier_kb("/profile")

    new_message = await message.answer(
        text,
        reply_markup=reply_kb,
        disable_notification=True,
        parse_mode="HTML",
    )
    await handler.catch(
        bot=courier_bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=message,
        delete_previous=True,
    )


@courier_r.callback_query(F.data == "set_my_name")
async def set_name(callback_query: CallbackQuery, state: FSMContext):

    await callback_query.answer("Изменить имя:", show_alert=False)

    current_state = CourierState.change_Name.state
    tg_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)

    text = f"Изменить данные профиля.\n\n" f"<b>Ваше имя:</b>"
    new_message = await callback_query.message.answer(
        text,
        disable_notification=True,
        parse_mode="HTML",
    )

    await handler.catch(
        bot=courier_bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=callback_query.message,
        delete_previous=False,
    )


@courier_r.callback_query(F.data == "set_my_phone")
async def set_phone(callback_query: CallbackQuery, state: FSMContext):

    await callback_query.answer("Изменить телефон:", show_alert=False)

    current_state = CourierState.change_Phone.state
    tg_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)

    reply_kb = await kb.get_courier_kb("phone_number")
    text = f"Изменить данные профиля.\n\n" f"<b>Ваш Телефон:</b>"
    new_message = await callback_query.message.answer(
        text,
        disable_notification=True,
        reply_markup=reply_kb,
        parse_mode="HTML",
    )

    await handler.catch(
        bot=courier_bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=callback_query.message,
        delete_previous=False,
    )


@courier_r.callback_query(F.data == "set_my_city")
async def set_city(callback_query: CallbackQuery, state: FSMContext):

    await callback_query.answer("Изменить город:", show_alert=False)

    current_state = CourierState.change_City.state
    tg_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)

    text = f"Изменить данные профиля.\n\n" f"<b>Ваш город:</b>"
    new_message = await callback_query.message.answer(
        text,
        disable_notification=True,
        parse_mode="HTML",
    )

    await handler.catch(
        bot=courier_bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=callback_query.message,
        delete_previous=False,
    )


# ---
# ---


@courier_r.message(filters.StateFilter(CourierState.change_Name))
async def change_name(message: Message, state: FSMContext):

    current_state = CourierState.default.state
    tg_id = message.from_user.id
    chat_id = message.chat.id
    name = message.text

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)

    _ = await courier_data.update_courier_name(tg_id, name)
    _ = await rediska.set_name(courier_bot_id, tg_id, name)

    text = (
        f"Имя курьера было изменено на {name} 🎉\n\n" f"▼ <b>Выберите действие ...</b>"
    )

    new_message = await message.answer(
        text,
        disable_notification=True,
        parse_mode="HTML",
    )

    await handler.catch(
        bot=courier_bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=message,
        delete_previous=True,
    )


@courier_r.message(filters.StateFilter(CourierState.change_Phone))
async def change_phone(message: Message, state: FSMContext):

    current_state = CourierState.default.state
    tg_id = message.from_user.id
    chat_id = message.chat.id
    phone = message.contact.phone_number

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)

    _ = await courier_data.update_courier_phone(tg_id, phone)
    _ = await rediska.set_phone(courier_bot_id, tg_id, phone)

    text = f"Номер был изменен на {phone} 🎉\n\n" f"▼ <b>Выберите действие ...</b>"

    new_message = await message.answer(
        text,
        disable_notification=True,
        parse_mode="HTML",
    )

    await handler.catch(
        bot=courier_bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=message,
        delete_previous=True,
    )


@courier_r.message(filters.StateFilter(CourierState.change_City))
async def change_city(message: Message, state: FSMContext):

    current_state = CourierState.default.state
    tg_id = message.from_user.id
    chat_id = message.chat.id

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)

    russian_cities = await cities.get_cities()
    city, _ = await find_closest_city(message.text, russian_cities)

    if not city:
        text = f"Введите корректное название города!\n<b>Ваш город:</b>"

        new_message = await message.answer(
            text,
            disable_notification=True,
            parse_mode="HTML",
        )

    else:

        _ = await courier_data.update_courier_city(tg_id, city)
        _ = await rediska.set_city(courier_bot_id, tg_id, city)

        text = f"Город был изменен на {city} 🎉\n\n" f"▼ <b>Выберите действие ...</b>"

        new_message = await message.answer(
            text,
            disable_notification=True,
            parse_mode="HTML",
        )

    await handler.catch(
        bot=courier_bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=message,
        delete_previous=True,
    )


# ---
# ---


@courier_r.message(F.text == "/faq")
async def cmd_faq(message: Message, state: FSMContext):

    current_state = CourierState.default.state
    tg_id = message.from_user.id
    chat_id = message.chat.id

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)

    text = (
        f"🤔 <b>Вопросы и ответы</b>\n\n"
        f"Частые вопросы и ответы на них "
        f"<a href='https://drive.google.com/file/d/1cXYK_FqU7kRpTU9p04dVjcE4vRbmNvMw/view?usp=sharing'>FAQ</a>"
    )

    new_message = await message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )

    await handler.catch(
        bot=courier_bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=message,
        delete_previous=True,
    )


@courier_r.message(F.text == "/rules")
async def cmd_rules(message: Message, state: FSMContext):

    current_state = CourierState.default.state
    tg_id = message.from_user.id
    chat_id = message.chat.id

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)

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

    await handler.catch(
        bot=courier_bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=message,
        delete_previous=True,
    )


@courier_r.message(F.text == "/make_order")
async def cmd_make_order(message: Message, state: FSMContext):

    current_state = CourierState.default.state
    tg_id = message.from_user.id
    chat_id = message.chat.id

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)

    text = (
        f"📦 <b>Оформить заказ</b>\n\n"
        f"⦿ Сделать заказ у нас — это просто и удобно!\n"
        f"⦿ Наслаждайтесь удобством и скоростью нашего сервиса!"
    )
    reply_kb = await kb.get_courier_kb("/make_order")

    new_message = await message.answer(
        text,
        reply_markup=reply_kb,
        disable_notification=True,
        parse_mode="HTML",
    )

    await handler.catch(
        bot=courier_bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=message,
        delete_previous=True,
    )


# ---
# ---


@courier_r.callback_query(F.data == "my_statistic")
async def get_courier_statistic(callback_query: CallbackQuery, state: FSMContext):

    await callback_query.answer("📊 Статистика", show_alert=False)

    current_state = CourierState.default.state
    tg_id = callback_query.from_user.id

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)

    (
        total_orders,
        completed_orders,
        average_execution_time,
        average_speed,
        total_money_earned,
    ) = await courier_data.get_courier_statistic(tg_id)

    text = (
        f"📊 <b>Ваша статистика</b>\n\n"
        f"Всего заказов: {total_orders}\n"
        f"Завершенные заказы: {completed_orders}\n"
        f"Среднее время выполнения: {average_execution_time / 60:.2f} мин\n"
        f"Средняя скорость: {average_speed:.2f} км/ч\n"
        f"Общая сумма заработка: {total_money_earned} руб.\n"
    )

    reply_kb = await kb.get_courier_kb("go_back")

    await callback_query.message.edit_text(
        text, reply_markup=reply_kb, parse_mode="HTML"
    )


# ---
# ---


@payment_r.message(F.text == "/subs")
@payment_r.callback_query(F.data == "pay_sub")
async def payment_invoice(event: Message | CallbackQuery):

    chat_id = event.chat.id if isinstance(event, Message) else event.message.chat.id
    tg_id = event.from_user.id
    moscow_time = await Time.get_moscow_time()

    if isinstance(event, Message):

        await event.answer("💵 Оформить подписку", show_alert=False)

        await handler._delete_previous_message(
            bot=courier_bot,
            user_id=tg_id,
            chat_id=chat_id,
        )

    _, _, _, end_date = await courier_data.get_courier_full_info(tg_id)

    if end_date and end_date > moscow_time:
        now = moscow_time
        remaining_days = (end_date - now).days

        text = (
            f"🚀 <b>Ваша подписка активна</b>\n\n"
            f"📅 Действует до: {end_date.strftime('%d.%m.%Y')}\n"
            f"🕒 Осталось дней: {remaining_days}\n\n"
            f"Хотите продлить подписку заранее?"
        )

        keyboard = await kb.get_courier_kb("extend_sub")

        new_message = await event.bot.send_message(
            chat_id, text, reply_markup=keyboard, parse_mode="HTML"
        )

        await handler.catch(
            bot=courier_bot,
            chat_id=chat_id,
            user_id=tg_id,
            new_message=new_message,
            current_message=None if isinstance(event, CallbackQuery) else event,
            delete_previous=True,
        )

        return

    await _send_payment_invoice(
        chat_id,
        event,
        tg_id,
    )


@payment_r.callback_query(F.data == "extend_sub")
async def extend_subscription(event: CallbackQuery):

    chat_id = event.message.chat.id
    tg_id = event.from_user.id

    await _send_payment_invoice(
        chat_id,
        event,
        tg_id,
    )


async def _send_payment_invoice(
    chat_id: int,
    event: Message | CallbackQuery,
    tg_id,
):

    prices = [
        LabeledPrice(
            label="Месячная подписка",
            amount=99000,  # 990.00 RUB
        ),
    ]

    if not payment_provider:
        log.error("Ошибка: provider_token не найден. Проверьте переменные окружения.")
        return

    new_message = await event.bot.send_invoice(
        chat_id=chat_id,
        title="Подписка Raketa",
        description="Оформите подписку на сервис доставки...",
        payload="Payment through a bot",
        provider_token=payment_provider,
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
    )

    await handler.catch(
        bot=courier_bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=None,
        delete_previous=True,
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
async def successful_payment(message: Message):

    tg_id = message.from_user.id
    chat_id = message.chat.id

    ttl = await title.get_title_courier("success_payment")
    text = f"Cпасибо за подписку!\nСумма: {message.successful_payment.total_amount // 100}{message.successful_payment.currency}"
    reply_kb = await kb.get_courier_kb("success_payment")
    new_message = await message.answer_photo(photo=ttl, caption=text, reply_kb=reply_kb)

    try:
        is_updated = await courier_data.update_courier_subscription(
            tg_id=tg_id, days=30
        )
        if is_updated:
            log.info(f"Subscription updated successfully for courier {tg_id}.")
        else:
            log.error(f"Failed to update subscription for courier {tg_id}.")
    except Exception as e:
        log.error(f"Error updating subscription for courier {tg_id}: {e}")

    await handler.catch(
        bot=courier_bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=message,
        delete_previous=True,
    )


# ---
# ---


@courier_fallback.message()
async def handle_unrecognized_message(message: Message):
    await message.delete()
