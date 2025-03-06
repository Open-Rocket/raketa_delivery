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
    MessageHandlerState,
    CourierState,
    CourierOuterMiddleware,
    datetime,
    PreCheckoutQuery,
    zlib,
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
from run import customer_bot


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
    log.info(f"cmd_run was called!")

    chat_id = event.chat.id if isinstance(event, Message) else event.message.chat.id
    tg_id = event.from_user.id
    bot_id = event.bot.id
    current_state = CourierState.location.state

    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)

    handler = MessageHandler(state, event.bot)
    reply_kb = await kb.get_courier_kb("/run")

    new_message = await event.bot.send_message(
        chat_id=chat_id,
        text="Пожалуйста, отправьте вашу текущую локацию, чтобы мы могли назначить вам ближайшие заказы.\n\n"
        "<i>*Доступно только с мобильных устройств</i>",
        reply_markup=reply_kb,
        disable_notification=True,
        parse_mode="HTML",
    )

    if isinstance(event, Message):
        await handler.delete_previous_message(chat_id)

    await handler.handle_new_message(
        new_message, event if isinstance(event, Message) else event.message
    )

    log.info(f"cmd_run was successfully done!")


@courier_r.message(
    F.content_type == ContentType.LOCATION, filters.StateFilter(CourierState.location)
)
async def get_location(message: Message, state: FSMContext):
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)

    courier_tg_id = message.from_user.id
    courier_city = await courier_data.get_courier_city(courier_tg_id)
    bot_id = message.bot.id
    my_lon = message.location.longitude
    my_lat = message.location.latitude
    radius_km = 5

    available_orders = await order_data.get_available_orders(my_lat, my_lon, radius_km)

    await state.update_data(available_orders=available_orders)
    await rediska.save_fsm_state(state, bot_id, courier_tg_id)

    city_orders = await order_data.get_pending_orders_in_city(courier_city)

    text = (
        f"<b>📋 Заказы</b>\n\n"
        f"Всего заказов в городе <b>{courier_city}</b>: <b>{len(city_orders)}</b>\n"
        f"Заказов рядом с вами: <b>{len(available_orders)}</b>\n\n"
        f"🔍 Хотите посмотреть заказы рядом?"
    )

    reply_kb = await kb.get_courier_kb("near_orders")

    new_message = await message.answer(
        text, reply_markup=reply_kb, disable_notification=True, parse_mode="HTML"
    )

    await handler.handle_new_message(new_message, message)

    log.info(
        f"Курьер {courier_tg_id} получил информацию о {len(available_orders)} заказах в радиусе и {len(city_orders)} в городе."
    )


@courier_r.callback_query(F.data == "show_nearby_orders")
async def show_nearby_orders(callback_query: CallbackQuery, state: FSMContext):

    data = await state.get_data()
    tg_id = callback_query.from_user.id
    bot_id = callback_query.bot.id
    available_orders = data.get("available_orders", {})

    if not available_orders or not isinstance(available_orders, dict):
        log.warning(f"Некорректный формат available_orders: {available_orders}")
        await callback_query.answer(
            "Нет доступных заказов в вашем радиусе или данные устарели.",
            show_alert=True,
        )
        return

    orders_data = {}
    order_ids = list(available_orders.keys())
    for index, order_id in enumerate(order_ids, start=1):
        order_forma = available_orders[order_id]["text"]
        order_text = (
            f"<b>{index}/{len(available_orders)}</b>\n"
            f"<b>Заказ: №{order_id}</b>\n"
            f"---------------------------------------------\n\n"
            f"{order_forma}"
        )
        orders_data[order_id] = {"text": order_text, "index": index}

    await state.clear()
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

    await callback_query.message.edit_text(
        orders_data[first_order_id]["text"],
        reply_markup=reply_markup,
        parse_mode="HTML",
    )

    log.info(f"Курьер {tg_id} получил список доступных заказов рядом.")


@courier_r.callback_query(F.data.in_({"next_right", "back_left"}))
async def handle_order_available_navigation(
    callback_query: CallbackQuery, state: FSMContext
):
    log.info("handle_order_available_navigation вызван!")

    tg_id = callback_query.from_user.id
    bot_id = callback_query.bot.id

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
    else:
        new_index = (current_index - 1) % total_orders

    new_order_id = order_ids[new_index]
    await state.update_data(current_index=new_index, current_order_id=new_order_id)
    await rediska.save_fsm_state(state, bot_id, tg_id)

    log.info(
        f"Переключение на заказ {new_index + 1}/{total_orders}, order_id={new_order_id}"
    )

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
    handler = MessageHandler(state, callback_query.message.bot)
    data = await state.get_data()
    order_ids = data.get("order_ids", [])
    current_order_id = data.get("current_order_id")
    courier_tg_id = callback_query.from_user.id
    bot_id = callback_query.bot.id

    if not order_ids:
        await callback_query.answer("Заказы не найдены.", show_alert=True)
        return

    if current_order_id not in order_ids:
        await callback_query.answer("Неверный order_id для заказа.", show_alert=True)
        return

    log.info(f"Курьер {courier_tg_id} принял заказ с ID: {current_order_id}.")

    try:
        is_assigned = await order_data.assign_courier_to_order(
            order_id=current_order_id, courier_tg_id=courier_tg_id
        )

        if not is_assigned:
            await callback_query.message.answer(
                "К сожалению, заказ уже был принят другим курьером.", parse_mode="HTML"
            )
            return

        await order_data.update_order_status(
            order_id=current_order_id, new_status=OrderStatus.IN_PROGRESS
        )

        customer_tg_id = await order_data.get_customer_tg_id(current_order_id)
        await customer_bot.send_message(
            chat_id=customer_tg_id,
            text=f"Ваш заказ №{current_order_id} был принят курьером!",
            parse_mode="HTML",
        )

        order_ids.remove(current_order_id)

        new_message = await callback_query.message.answer(
            f"<b>✅ Заказ №{current_order_id} принят!</b>", parse_mode="HTML"
        )

        await state.update_data(
            order_ids=order_ids,
            current_order_id=None if not order_ids else order_ids[0],
        )
        await rediska.save_fsm_state(state, bot_id, courier_tg_id)

        await handler.handle_new_message(new_message, callback_query.message)

        await asyncio.sleep(900)
        try:
            await customer_bot.delete_message(
                chat_id=customer_tg_id, message_id=new_message.message_id
            )
        except Exception as e:
            log.error(f"Ошибка при удалении сообщения: {e}")

    except Exception as e:
        log.error(f"Ошибка при принятии заказа {current_order_id}: {e}")
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
        f"✎  <b>Мои заказы</b>\n\n"
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


@courier_r.callback_query(F.data.in_({"active_orders", "completed_orders"}))
async def get_orders(callback_query: CallbackQuery, state: FSMContext):
    log.info(f"get_orders was called! Callback data: {callback_query.data}")

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
        log.info(f"Нет {status_text} заказов для пользователя tg_id={tg_id}")
        await callback_query.answer(
            f"У вас нет {status_text} заказов.",
            disable_notification=True,
            show_alert=True,
        )
        log.info(f"Конец выполнения get_orders: заказов не найдено")
        return

    first_order_id = list(orders_data.keys())[0]
    await state.update_data(
        orders_data=orders_data, counter=0, current_order_id=first_order_id
    )
    await rediska.save_fsm_state(state, bot_id, tg_id)

    if callback_query.data == "active_orders":
        reply_kb = await kb.get_courier_kb(
            "active_one" if len(orders_data) == 1 else "active_orders"
        )
    else:
        reply_kb = await kb.get_courier_kb(
            "one_my_order" if len(orders_data) == 1 else "completed_orders"
        )

    log.info(f"Отображение первого заказа: total_orders={len(orders_data)}")
    await callback_query.message.edit_text(
        orders_data[first_order_id]["text"],
        reply_markup=reply_kb,
        disable_notification=True,
        parse_mode="HTML",
    )
    log.info(f"get_orders was successfully done!")


@courier_r.callback_query(F.data.in_({"next_right_mo", "back_left_mo"}))
async def handle_order_navigation(callback_query: CallbackQuery, state: FSMContext):
    log.info("handle_order_navigation was called!")

    data = await state.get_data()
    orders_data = data.get("orders_data", {})
    current_order_id = data.get("current_order_id")

    tg_id = callback_query.from_user.id
    bot_id = callback_query.bot.id

    if not orders_data or not current_order_id:
        log.warning("Нет доступных заказов для переключения")
        await callback_query.answer("Нет доступных заказов.", show_alert=True)
        return

    total_orders = len(orders_data)

    order_ids = list(orders_data.keys())

    current_index = order_ids.index(current_order_id)
    if callback_query.data == "next_right_mo":
        new_index = (current_index + 1) % total_orders
    else:
        new_index = (current_index - 1) % total_orders

    next_order_id = order_ids[new_index]

    await state.update_data(current_order_id=next_order_id, counter=new_index)
    await rediska.save_fsm_state(state, bot_id, tg_id)

    await callback_query.message.edit_text(
        orders_data[next_order_id]["text"],
        reply_markup=callback_query.message.reply_markup,
        parse_mode="HTML",
    )

    log.info(
        f"Переключение на заказ #{new_index + 1}/{total_orders}, order_id={next_order_id}"
    )


# ---


@courier_r.callback_query(F.data == "order_delivered")
async def complete_order(callback_query: CallbackQuery, state: FSMContext):
    handler = MessageHandler(state, callback_query.message.bot)
    data = await state.get_data()
    current_order_id = data.get("current_order_id")

    log.info(f"data: {data}")
    log.info(f"current_order_id: {current_order_id}")

    if not current_order_id:
        await callback_query.message.answer(
            "Не удалось найти активный заказ для завершения."
        )
        return

    try:

        order = await order_data.get_order_by_id(current_order_id)
        log.info(
            f"Попытка завершить заказ {current_order_id}, его статус: {order.order_status}"
        )

        if order.order_status != OrderStatus.IN_PROGRESS:
            await callback_query.message.answer(
                f"Заказ №{current_order_id} уже завершён или находится в другом статусе. Статус: {order.order_status}.",
                parse_mode="HTML",
            )
            return

        completed_time = datetime.now()
        await order_data.update_order_status_and_time(
            order_id=current_order_id,
            new_status=OrderStatus.COMPLETED,
            completed_time=completed_time,
        )

        customer_tg_id = await order_data.get_customer_tg_id(order.order_id)

        notification_text = (
            f"Ваш заказ №{current_order_id} был успешно доставлен курьером!\n"
            f"Спасибо, что воспользовались нашим сервисом.\n\n"
            f"<i>*Сообщение удалится через 15 минут</i>"
        )
        notification_message = await customer_bot.send_message(
            chat_id=customer_tg_id, text=notification_text, parse_mode="HTML"
        )

        await callback_query.message.answer(
            f"Статус заказа №{current_order_id} обновлен на 'Завершен'. Заказчик уведомлен.",
            parse_mode="HTML",
            disable_notification=False,
        )

        await handler.delete_previous_message(callback_query.message.chat.id)

        await state.set_state(CourierState.default)

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


@courier_r.message(F.text == "/make_order")
async def cmd_make_order(message: Message, state: FSMContext):
    log.info(f"cmd_make_order was called!")

    handler = MessageHandler(state, message.bot)
    bot_id = message.bot.id
    tg_id = message.from_user.id
    current_state = CourierState.default.state

    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)

    text = (
        f"📦 <b>Оформить заказ</b>\n\n"
        f"⦿ Сделать заказ у нас — это просто и удобно!\n"
        f"⦿ Наслаждайтесь удобством и скоростью нашего сервиса!"
    )
    reply_kb = await kb.get_courier_kb("/make_order")

    await handler.delete_previous_message(message.chat.id)

    new_message = await message.answer(
        text,
        reply_markup=reply_kb,
        disable_notification=True,
        parse_mode="HTML",
    )

    await handler.handle_new_message(new_message, message)

    log.info(
        f"\n"
        f"- Courier 🧍\n"
        f"- Handler F.text: {F.text}\n"
        f"- Courier telegram ID: {tg_id}\n"
        f"- Courier state now: {current_state}\n"
    )

    log.info(f"cmd_make_order was successfully done!")


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
