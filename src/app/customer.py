from ._deps import (
    asyncio,
    CommandStart,
    FSMContext,
    ContentType,
    filters,
    Message,
    CallbackQuery,
    OrderStatus,
    CustomerState,
    CustomerOuterMiddleware,
    time,
    zlib,
    handler,
    customer_bot,
    customer_bot_id,
    moscow_time,
    customer_r,
    customer_fallback,
    kb,
    title,
    customer_data,
    order_data,
    recognizer,
    rediska,
    assistant,
    formatter,
    cities,
    log,
    find_closest_city,
    F,
)


# ---


customer_r.message.outer_middleware(CustomerOuterMiddleware(rediska))
customer_r.callback_query.outer_middleware(CustomerOuterMiddleware(rediska))


# ---


@customer_r.message(CommandStart())
async def cmd_start_customer(message: Message, state: FSMContext):

    tg_id = message.from_user.id
    chat_id = message.chat.id
    is_reg = await rediska.is_reg(customer_bot_id, tg_id)

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)

    if is_reg:
        current_state = CustomerState.default.state
        text = "▼ <b>Выберите действие ...</b>"
        new_message = await message.answer(
            text, parse_mode="HTML", disable_notification=True
        )
    else:
        current_state = CustomerState.reg_state.state
        photo_title = await title.get_title_customer("/start")
        text = (
            f"Raketa — современный сервис доставки с минимальными ценами и удобством использования.\n\n"
            f"Почему выбирают нас?\n\n"
            f"◉ Низкие цены:\n"
            f"Наши пешие курьеры находятся рядом с вами, что снижает стоимость и ускоряет доставку.\n\n"
            f"◉ Простота и удобство:\n"
            f"С помощью технологий ИИ вы можете быстро оформить заказ и сразу отправить его на выполнение."
        )
        reply_kb = await kb.get_customer_kb("/start")
        new_message = await message.answer_photo(
            photo=photo_title,
            caption=text,
            reply_markup=reply_kb,
            parse_mode="HTML",
            disable_notification=True,
        )

    await handler.catch(
        bot=customer_bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=message,
        delete_previous=True,
    )


@customer_r.callback_query(F.data == "reg")
async def data_reg_customer(callback_query: CallbackQuery, state: FSMContext):

    current_state = CustomerState.reg_Name.state
    tg_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)

    text = (
        "Пройдите небольшую регистрацию.\n"
        "Это не займет много времени.\n\n"
        "<b>Как вас зовут?</b>"
    )
    new_message = await callback_query.message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )

    await handler.catch(
        bot=customer_bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=callback_query.message,
        delete_previous=False,
    )


@customer_r.message(filters.StateFilter(CustomerState.reg_Name))
async def data_name_customer(message: Message, state: FSMContext):

    current_state = CustomerState.reg_Phone.state
    tg_id = message.from_user.id
    chat_id = message.chat.id
    customer_name = message.text

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)
    _ = await rediska.set_name(customer_bot_id, tg_id, customer_name)

    reply_kb = await kb.get_customer_kb("phone_number")
    text = (
        f"Привет, {customer_name}!👋\n\nЧтобы мы могли быстро оформить заказ и курьер смог связаться с вами "
        f"в случае необходимости, пожалуйста, нажмите на кнопку 'Поделиться номером'!\n\n"
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
        bot=customer_bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=message,
        delete_previous=True,
    )


@customer_r.message(filters.StateFilter(CustomerState.reg_Phone))
async def data_phone_customer(message: Message, state: FSMContext):

    current_state = CustomerState.reg_City.state
    tg_id = message.from_user.id
    chat_id = message.chat.id
    customer_phone = message.contact.phone_number

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)
    _ = await rediska.set_phone(customer_bot_id, tg_id, customer_phone)

    text = (
        f"Последний шаг!\n\n"
        f"Для того чтобы каждый раз не указывать город доставки, "
        f"скажите в каком городе вы будете в основном делать заказы "
        f"и он автоматически будет подставляться.\n\n"
        f"<b>Ваш город:</b>"
    )

    new_message = await message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )

    await handler.catch(
        bot=customer_bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=message,
        delete_previous=True,
    )


@customer_r.message(filters.StateFilter(CustomerState.reg_City))
async def data_city_customer(message: Message, state: FSMContext):

    current_state = CustomerState.reg_tou.state
    tg_id = message.from_user.id
    chat_id = message.chat.id
    russian_cities = await cities.get_cities()
    city, _ = await find_closest_city(message.text, russian_cities)

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)
    _ = await rediska.set_city(customer_bot_id, tg_id, city)

    if not city:
        text = f"Введите корректное название города!\n<b>Ваш город:</b>"

        new_message = await message.answer(
            text, disable_notification=True, parse_mode="HTML"
        )

        log.info(f"city name was uncorrectable: {city}\n" f"text message: {text}\n")

        return

    reply_kb = await kb.get_customer_kb("accept_tou")
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
        bot=customer_bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=message,
        delete_previous=True,
    )


@customer_r.callback_query(F.data == "accept_tou")
async def customer_accept_tou(callback_query: CallbackQuery, state: FSMContext):

    current_state = CustomerState.default.state
    tg_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id

    accept_tou = (
        "Пользовательское соглашение и правила использования сервиса - Принимаю"
    )

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)
    await rediska.set_tou(customer_bot_id, tg_id, accept_tou)
    await rediska.set_reg(customer_bot_id, tg_id, True)

    customer_name, customer_phone, customer_city, tou = await rediska.get_user_info(
        customer_bot_id, tg_id
    )

    _ = await customer_data.set_customer(
        tg_id, customer_name, customer_phone, customer_city, tou
    )

    text = (
        "Вы успешно зарегистрировались! 🎉\n\n"
        f"Имя: {customer_name}\n"
        f"Номер: {customer_phone}\n"
        f"Город: {customer_city}\n\n"
        f"▼ <b>Выберите действие ...</b>"
    )
    new_message = await callback_query.message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )

    await handler.catch(
        bot=customer_bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=callback_query.message,
        delete_previous=False,
    )


# ---


@customer_r.message(F.text == "/order")
async def cmd_order(message: Message, state: FSMContext):

    tg_id = message.from_user.id
    chat_id = message.chat.id
    is_read_info = await rediska.is_read_info(customer_bot_id, tg_id)

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)

    if is_read_info:
        current_state = CustomerState.ai_voice_order.state
        text = (
            "<i>*Вы можете отправить как голосовое сообщение так и текстовое, "
            "заказ будет оформлен в считанные секунды.</i>"
        )
        new_message = await message.answer(
            text=f"{text}\n\nゞ <b>Опишите ваш заказ ...</b>",
            disable_notification=True,
            parse_mode="HTML",
        )

    else:
        current_state = CustomerState.default.state
        photo_title = await title.get_title_customer(message.text)
        reply_kb = await kb.get_customer_kb(message.text)
        text = (
            "◉ Вы можете сделать заказ с помощью текста или голоса, "
            "и наш ИИ ассистент быстро его обработает и передаст курьеру.\n\n"
            "<i>*При записи голосового сообщения или набора текста описывайте заказ так, как вам удобно, "
            "ассистент создаст заявку для вашего заказа.</i>"
        )
        new_message = await message.answer_photo(
            photo=photo_title,
            caption=text,
            reply_markup=reply_kb,
            disable_notification=True,
            parse_mode="HTML",
        )

    await handler.catch(
        bot=customer_bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=message,
        delete_previous=True,
    )


@customer_r.message(F.text == "/profile")
async def cmd_profile(message: Message, state: FSMContext):

    current_state = CustomerState.default.state
    tg_id = message.from_user.id
    chat_id = message.chat.id

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)

    await title.get_title_customer(message.text)
    name, phone, city = await customer_data.get_customer_info(tg_id)

    reply_kb = await kb.get_customer_kb(message.text)
    text = (
        f"👥 <b>Профиль</b>\n\n"
        f"Посмотрите или измените данные о себе.\n\n"
        f"• Номер нужен для связи с курьером.\n"
        f"• Город подставляется в заказ.\n\n"
        f"<i>*При заказе в другом городе укажите его в описании к заказу.</i>\n\n"
        f"<b>Имя:</b> {name} \n"
        f"<b>Номер:</b> {phone}\n"
        f"<b>Город:</b> {city}"
    )

    new_message = await message.answer(
        text, reply_markup=reply_kb, disable_notification=True, parse_mode="HTML"
    )

    await handler.catch(
        bot=customer_bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=message,
        delete_previous=True,
    )


@customer_r.message(F.text == "/faq")
async def cmd_faq(message: Message, state: FSMContext):

    current_state = CustomerState.default.state
    tg_id = message.from_user.id
    chat_id = message.chat.id

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)

    text = (
        f"🤔 <b>Вопросы и ответы</b>\n\n"
        f"Частые вопросы и ответы на них "
        f"<a href='https://drive.google.com/file/d/1cXYK_FqU7kRpTU9p04dVjcE4vRbmNvMw/view?usp=sharing'>FAQ</a>"
    )

    new_message = await message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )

    await handler.catch(
        bot=customer_bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=message,
        delete_previous=True,
    )


@customer_r.message(F.text == "/rules")
async def cmd_rules(message: Message, state: FSMContext):

    current_state = CustomerState.default.state
    tg_id = message.from_user.id
    chat_id = message.chat.id

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)

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
        bot=customer_bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=message,
        delete_previous=True,
    )


@customer_r.message(F.text == "/become_courier")
async def cmd_become_courier(message: Message, state: FSMContext):

    current_state = CustomerState.default.state
    tg_id = message.from_user.id
    chat_id = message.chat.id

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)

    photo_title = await title.get_title_customer("/become_courier")
    text = (
        "⦿ Стать курьером у нас — это отличный способ заработать без комиссии!\n\n"
        "⦿ Работайте в удобное время, выбирайте заказы рядом и получайте бонусы за быструю доставку.\n\n"
        "⦿ Зарабатывайте до 7000₽ в день уже сегодня!"
    )
    reply_kb = await kb.get_customer_kb("/become_courier")

    new_message = await message.answer_photo(
        photo=photo_title,
        caption=text,
        reply_markup=reply_kb,
        disable_notification=True,
    )

    await handler.catch(
        bot=customer_bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=message,
        delete_previous=True,
    )


# ---


@customer_r.callback_query(F.data == "ai_order")
async def data_ai(callback_query: CallbackQuery, state: FSMContext):

    current_state = CustomerState.ai_voice_order.state
    tg_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)
    _ = await rediska.set_read_info(customer_bot_id, tg_id, True)

    text = (
        "<i>*Вы можете отправить как голосовое сообщение так и текстовое, "
        "заказ будет оформлен в считанные секунды.</i>"
    )

    new_message = await callback_query.message.answer(
        text=f"{text}\n\nゞ <b>Опишите ваш заказ ...</b>",
        disable_notification=True,
        parse_mode="HTML",
    )

    await handler.catch(
        bot=customer_bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=callback_query.message,
        delete_previous=False,
    )


# ---


@customer_r.callback_query(F.data == "set_my_name")
async def set_name(callback_query: CallbackQuery, state: FSMContext):

    current_state = CustomerState.change_Name.state
    tg_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)

    text = f"Изменить данные профиля.\n\n" f"<b>Ваше имя:</b>"
    new_message = await callback_query.message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )

    await handler.catch(
        bot=customer_bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=callback_query.message,
        delete_previous=False,
    )


@customer_r.callback_query(F.data == "set_my_phone")
async def set_phone(callback_query: CallbackQuery, state: FSMContext):

    current_state = CustomerState.change_Phone.state
    tg_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)

    reply_kb = await kb.get_customer_kb("phone_number")
    text = f"Изменить данные профиля.\n\n" f"<b>Ваш Телефон:</b>"
    new_message = await callback_query.message.answer(
        text, disable_notification=True, reply_markup=reply_kb, parse_mode="HTML"
    )

    await handler.catch(
        bot=customer_bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=callback_query.message,
        delete_previous=False,
    )


@customer_r.callback_query(F.data == "set_my_city")
async def set_city(callback_query: CallbackQuery, state: FSMContext):

    current_state = CustomerState.change_City.state
    tg_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)

    text = f"Изменить данные профиля.\n\n" f"<b>Ваш город:</b>"
    new_message = await callback_query.message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )

    await handler.catch(
        bot=customer_bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=callback_query.message,
        delete_previous=False,
    )


# ---


@customer_r.message(filters.StateFilter(CustomerState.change_Name))
async def change_name(message: Message, state: FSMContext):

    current_state = CustomerState.default.state
    tg_id = message.from_user.id
    chat_id = message.chat.id
    customer_name = message.text

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)

    _ = await customer_data.update_customer_name(tg_id, customer_name)
    _ = await rediska.set_name(customer_bot_id, tg_id, customer_name)

    text = (
        f"Имя было изменено на {customer_name} 🎉\n\n" f"▼ <b>Выберите действие ...</b>"
    )

    new_message = await message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )

    await handler.catch(
        bot=customer_bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=message,
        delete_previous=True,
    )


@customer_r.message(filters.StateFilter(CustomerState.change_Phone))
async def change_phone(message: Message, state: FSMContext):

    current_state = CustomerState.default.state
    tg_id = message.from_user.id
    chat_id = message.chat.id
    customer_phone = message.contact.phone_number

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)

    _ = await customer_data.update_customer_phone(tg_id, customer_phone)
    _ = await rediska.set_phone(customer_bot_id, tg_id, customer_phone)

    text = (
        f"Номер был изменено на {customer_phone} 🎉\n\n"
        f"▼ <b>Выберите действие ...</b>"
    )

    new_message = await message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )

    await handler.catch(
        bot=customer_bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=message,
        delete_previous=True,
    )


@customer_r.message(filters.StateFilter(CustomerState.change_City))
async def change_city(message: Message, state: FSMContext):

    current_state = CustomerState.default.state
    tg_id = message.from_user.id
    chat_id = message.chat.id

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)

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

        _ = await customer_data.update_customer_city(tg_id, city)
        _ = await rediska.set_city(customer_bot_id, tg_id, city)

        text = f"Город был изменен на {city} 🎉\n\n" f"▼ <b>Выберите действие ...</b>"

        new_message = await message.answer(
            text, disable_notification=True, parse_mode="HTML"
        )

    await handler.catch(
        bot=customer_bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=message,
        delete_previous=True,
    )


# ---


@customer_r.message(F.text == "/my_orders")
@customer_r.callback_query(F.data == "back_myOrders")
async def cmd_my_orders(event: Message | CallbackQuery, state: FSMContext):

    current_state = CustomerState.myOrders.state
    is_callback = isinstance(event, CallbackQuery)
    tg_id = event.from_user.id
    chat_id = event.message.chat.id if is_callback else event.chat.id

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)

    pending_count = len(await order_data.get_pending_orders(tg_id))
    active_count = len(await order_data.get_active_orders(tg_id))
    completed_count = len(await order_data.get_completed_orders(tg_id))

    reply_kb = await kb.get_customer_orders_kb(
        pending_count, active_count, completed_count
    )
    text = (
        f"✎ <b>Мои заказы</b>\n\n"
        f"Здесь вы можете посмотреть статус ваших заказов, "
        f"а также статистику за все время использования нашего сервиса.\n\n"
        f"<b>Статус ваших заказов:</b>"
    )

    new_message = (
        await event.message.edit_text(
            text,
            reply_markup=reply_kb,
            disable_notification=True,
            parse_mode="HTML",
        )
        if is_callback
        else await event.answer(
            text,
            reply_markup=reply_kb,
            disable_notification=True,
            parse_mode="HTML",
        )
    )

    await handler.catch(
        bot=customer_bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=None if isinstance(event, CallbackQuery) else event,
        delete_previous=False if is_callback else True,
    )


@customer_r.callback_query(
    F.data.in_({"pending_orders", "active_orders", "completed_orders"})
)
async def get_my_orders(callback_query: CallbackQuery, state: FSMContext):

    tg_id = callback_query.from_user.id

    order_status_mapping = {
        "pending_orders": (
            order_data.get_pending_orders,
            CustomerState.myOrders_pending,
            "ожидающих",
        ),
        "active_orders": (
            order_data.get_active_orders,
            CustomerState.myOrders_active,
            "активных",
        ),
        "completed_orders": (
            order_data.get_completed_orders,
            CustomerState.myOrders_completed,
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

    customer_orders = await get_orders_func(tg_id)

    orders_data = {}
    for index, order in enumerate(customer_orders, start=1):

        try:
            order_forma = (
                zlib.decompress(order.order_forma).decode("utf-8")
                if order.order_forma
                else "-"
            )
        except Exception as e:
            log.error(
                f"Ошибка декодирования order_forma для заказа {order.order_id}: {e}"
            )
            order_forma = "-"

        base_info = (
            f"<b>{index}/{len(customer_orders)}</b>\n"
            f"<b>Заказ: №{order.order_id}</b>\n"
            f"---------------------------------------------\n"
            f"{order_forma}"
        )
        orders_data[order.order_id] = {"text": base_info, "index": index - 1}

    if not orders_data:

        await callback_query.answer(
            f"У вас нет {status_text} заказов.", show_alert=True
        )
        return

    first_order_id = list(orders_data.keys())[0]
    await state.update_data(
        orders_data=orders_data,
        counter=0,
        current_order_id=first_order_id,
    )

    await state.set_state(state_status)
    await rediska.save_fsm_state(state, customer_bot_id, tg_id)

    if callback_query.data == "pending_orders":
        reply_kb = await kb.get_customer_kb(
            "one_my_pending" if len(orders_data) == 1 else "my_pending"
        )
    else:
        reply_kb = await kb.get_customer_kb(
            "one_my_order" if len(orders_data) == 1 else "my_order"
        )

    await callback_query.message.edit_text(
        orders_data[first_order_id]["text"],
        reply_markup=reply_kb,
        disable_notification=True,
        parse_mode="HTML",
    )


@customer_r.callback_query(F.data.in_({"next_right_mo", "back_left_mo"}))
async def handle_order_navigation(callback_query: CallbackQuery, state: FSMContext):

    tg_id = callback_query.from_user.id
    bot_id = callback_query.bot.id

    data = await state.get_data()
    orders_data = data.get("orders_data", {})
    counter = data.get("counter", 0)

    if not orders_data or not isinstance(orders_data, dict):
        log.warning(
            f"Нет доступных заказов для переключения или неверный формат: {orders_data}"
        )
        await callback_query.answer("Нет доступных заказов.", show_alert=True)
        return

    total_orders = len(orders_data)
    order_ids = list(orders_data.keys())

    counter = (
        (counter + 1) % total_orders
        if callback_query.data == "next_right_mo"
        else (counter - 1) % total_orders
    )

    current_order_id = order_ids[counter]

    await state.update_data(counter=counter, current_order_id=current_order_id)
    await rediska.save_fsm_state(state, bot_id, tg_id)

    try:
        await callback_query.message.edit_text(
            orders_data[current_order_id]["text"],
            reply_markup=callback_query.message.reply_markup,
            parse_mode="HTML",
        )

    except Exception as e:
        log.error(
            f"Ошибка при обновлении текста сообщения для заказа {current_order_id}: {e}"
        )
        await callback_query.answer(
            "Ошибка при обновлении информации о заказе.", show_alert=True
        )


@customer_r.callback_query(F.data == "cancel_my_order")
async def cancel_my_order(callback_query: CallbackQuery, state: FSMContext):
    log.info("cancel_my_order вызван!")

    tg_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id

    data = await state.get_data()
    current_order_id = data.get("current_order_id")

    if not current_order_id:
        log.warning("Не удалось найти current_order_id в состоянии FSM")
        await callback_query.message.answer(
            "Не удалось найти заказ для отмены.", parse_mode="HTML"
        )
        return

    order = await order_data.get_order_by_id(current_order_id)

    if not order:
        log.error(f"Заказ с ID {current_order_id} не найден в базе данных")
        await callback_query.message.answer(
            f"Заказ №{current_order_id} не найден.", parse_mode="HTML"
        )
        return

    if order.order_status != OrderStatus.PENDING:
        log.warning(
            f"Заказ {current_order_id} не в статусе PENDING: {order.order_status}"
        )
        await callback_query.answer(
            f"Заказ №{current_order_id} нельзя отменить, так как он не в статусе ожидания. Текущий статус: {order.order_status}.",
            parse_mode="HTML",
        )
        return

    try:
        is_canceled = await order_data.update_order_status(
            current_order_id, OrderStatus.CANCELLED
        )
        text = (
            f"<b>Заказ №{current_order_id} успешно отменён.</b>\n\n"
            f"<i>*Посмотреть информацию вы можете в своих заказах в пункте</i> <b>Отменённые.</b>\n\n"
            f"▼ <b>Выберите действие ...</b>"
        )
        new_message = await callback_query.message.answer(
            text, disable_notification=True, parse_mode="HTML"
        )

        await state.update_data(canceled_order_id=current_order_id)
        await rediska.save_fsm_state(state, customer_bot_id, tg_id)

        await handler.catch(
            bot=callback_query.bot,
            chat_id=chat_id,
            user_id=tg_id,
            new_message=new_message,
            current_message=callback_query.message,
            delete_previous=False,
        )

        log.info(f"Заказ {current_order_id} отменён, статус: {is_canceled}")
        log.info("cancel_my_order успешно выполнен!")
    except Exception as e:
        log.error(f"Ошибка при отмене заказа {current_order_id}: {e}")
        await callback_query.answer("Ошибка при отмене заказа.", show_alert=True)


# ---


@customer_r.message(
    filters.StateFilter(CustomerState.ai_voice_order),
    F.content_type.in_([ContentType.VOICE, ContentType.TEXT]),
)
async def process_order(message: Message, state: FSMContext):

    wait_message = await message.answer(
        "Заказ обрабатывается, подождите ...", disable_notification=True
    )

    text_msg = None
    start_time = time.perf_counter()

    if message.content_type == ContentType.VOICE:

        recognized_text = await recognizer.get_recognition_text(message)

        if not recognized_text:
            await handle_error_response(message, wait_message, "unrecognized")
            return

        text_msg = recognized_text
    else:
        text_msg = message.text

    try:

        await asyncio.wait_for(
            process_order_logic(text_msg, message, state, wait_message),
            timeout=120,
        )
    except asyncio.TimeoutError:
        await handle_error_response(message, wait_message, "timeout")
        log.error("Error: asyncio.TimeoutError")
    except Exception as e:
        await handle_error_response(message, wait_message, "general")
        log.error(f"Error: {e}")

    execution_time = time.perf_counter() - start_time
    log.info(f"Execution time process_message: {execution_time:.4f} sec")


async def process_order_logic(
    text_msg: str,
    message: Message,
    state: FSMContext,
    wait_message: Message,
):
    log.info("process_order_logic was called!")

    current_state = CustomerState.assistant_run.state
    tg_id = message.from_user.id
    customer_name = await rediska.get_name(customer_bot_id, tg_id)
    customer_phone = await rediska.get_phone(customer_bot_id, tg_id)
    customer_city = await rediska.get_city(customer_bot_id, tg_id)

    try:
        city, addresses, delivery_object, description = await assistant.process_order(
            text_msg, customer_city
        )

        if city == "N":
            await handle_error_response(message, wait_message, "moderation_failed")
            return

        log.info("request was successfully done")
    except Exception as e:
        await handle_error_response(message, wait_message, "general")
        log.error(f"Error: {e}")
        return

    prepare_dict = await formatter._prepare_data(
        moscow_time,
        city,
        customer_name,
        customer_phone,
        addresses,
        delivery_object,
        description,
    )

    order_info = await formatter.format_order_form(prepare_dict)
    reply_kb = await kb.get_customer_kb("voice_order_accept")

    await state.set_state(current_state)
    await state.update_data(current_order_info=(prepare_dict, order_info))
    await rediska.set_state(customer_bot_id, tg_id, current_state)
    await rediska.save_fsm_state(state, customer_bot_id, tg_id)

    new_message = await message.answer(
        order_info, reply_markup=reply_kb, disable_notification=True, parse_mode="HTML"
    )

    await wait_message.delete()

    await handler.catch(
        bot=message.bot,
        chat_id=message.chat.id,
        user_id=message.from_user.id,
        new_message=new_message,
        current_message=message,
        delete_previous=True,
    )


async def handle_error_response(
    message: Message, wait_message: Message, error_key: str
):
    """Функция для обработки и отправки сообщения об ошибке."""
    error_messages = {
        "general": "⚠ Ошибка при обработке заказа.\nПопробуйте снова",
        "unrecognized": "Мы не смогли определить ваш заказ.\nПопробуйте переформулировать заказ более четко и повторить попытку.",
        "timeout": "⚠ Время обработки заказа превышено. Попробуйте снова.",
        "moderation_failed": "⚠ Оформление заказа не удалось! Модерация не прошла.",
    }

    new_message = await message.answer(
        error_messages[error_key],
        reply_markup=await kb.get_customer_kb("rerecord"),
        disable_notification=True,
    )
    await wait_message.delete()

    await handler.catch(
        bot=message.bot,
        chat_id=message.chat.id,
        user_id=message.from_user.id,
        new_message=new_message,
        current_message=message,
        delete_previous=True,
    )
    log.warning(f"Error response sent: {error_key}")


# ---


@customer_r.callback_query(F.data == "order_sent")
async def set_order_to_db(callback_query: CallbackQuery, state: FSMContext):

    tg_id = callback_query.from_user.id

    state_data = await state.get_data()
    current_order_info = state_data.get("current_order_info")

    current_state = CustomerState.default.state

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)

    if current_order_info:
        data, order_forma = [*current_order_info]
        order_forma = zlib.compress(order_forma.encode("utf-8"))
    else:
        log.error("Ключ 'current_order_info' отсутствует в состоянии FSM")
        await callback_query.answer(
            "Ошибка: данные заказа не найдены.",
            disable_notification=True,
            show_alert=True,
        )
        return

    try:
        order_number = await order_data.create_order(tg_id, data, order_forma)
        text = (
            f"Заказ <b>№{order_number}</b> успешно создан! 🎉\n"
            f"Мы ищем курьера для вашего заказа 🔎\n\n"
            f"<i>*Информацию о заказах можно посмотреть в разделе</i> <b>Мои заказы</b>.\n\n"
            f"▼ <b>Выберите действие ...</b>"
        )
    except Exception as e:
        log.error(f"Ошибка при создании заказа: {str(e)}")
        text = "Ошибка при создании заказа.\n" "Попробуйте повторить заказ."

    new_message = await callback_query.message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )

    await handler.catch(
        bot=callback_query.bot,
        chat_id=callback_query.message.chat.id,
        user_id=tg_id,
        new_message=new_message,
        current_message=callback_query.message,
        delete_previous=False,
    )


# ---


@customer_r.callback_query(F.data == "cancel_order")
async def cancel_order(callback_query: CallbackQuery, state: FSMContext):

    current_state = CustomerState.default.state
    tg_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)

    text = "▼ <b>Выберите действие ...</b>"
    new_message = await callback_query.message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )
    await handler.catch(
        bot=callback_query.bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=callback_query.message,
        delete_previous=False,
    )


# ---


@customer_fallback.message()
async def handle_unrecognized_message(message: Message):
    await message.delete()
