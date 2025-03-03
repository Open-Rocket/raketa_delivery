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
    CustomerState,
    CustomerOuterMiddleware,
    time,
    zlib,
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
    log.info(f"cmd_start_customer was called!")

    bot_id = message.bot.id
    tg_id = message.from_user.id
    current_state = CustomerState.reg_state.state

    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)

    is_reg = await rediska.is_reg(bot_id, tg_id)

    if is_reg:
        default_state = CustomerState.default.state
        await state.set_state(default_state)
        await rediska.set_state(bot_id, tg_id, default_state)
        text = "▼ <b>Выберите действие ...</b>"

        await message.answer(text, parse_mode="HTML", disable_notification=True)

        return

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

    await message.answer_photo(
        photo=photo_title,
        caption=text,
        reply_markup=reply_kb,
        parse_mode="HTML",
        disable_notification=True,
    )

    log.info(
        f"\n"
        f"- Customer 🧍\n"
        f"- Handler /start\n"
        f"- Customer telegram ID: {tg_id}\n"
        f"- Customer message: {message.text}\n"
        f"- Customer state now: {current_state}"
    )

    log.info(f"cmd_start_customer was successfully done!")


@customer_r.callback_query(F.data == "reg")
async def data_reg_customer(callback_query: CallbackQuery, state: FSMContext):
    log.info(f"data_reg_customer was called!")

    bot_id = callback_query.bot.id
    tg_id = callback_query.from_user.id
    current_state = CustomerState.reg_Name.state

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
        f"- Customer 🧍\n"
        f"- Handler F.data: {F.data}\n"
        f"- Customer telegram ID: {tg_id}\n"
        f"- Customer message: {callback_query.message.text}\n"
        f"- Customer state now: {current_state}"
    )

    log.info(f"data_reg_customer was successfully done!")


@customer_r.message(filters.StateFilter(CustomerState.reg_Name))
async def data_name_customer(message: Message, state: FSMContext):
    log.info(f"data_name_customer was called!")

    handler = MessageHandler(state, message.bot)
    handle_state = await state.get_state()
    bot_id = message.bot.id
    tg_id = message.from_user.id
    customer_name = message.text
    current_state = CustomerState.reg_Phone.state

    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)
    is_name_set = await rediska.set_user_name(bot_id, tg_id, customer_name)

    reply_kb = await kb.get_customer_kb("phone_number")
    text = (
        f"Привет, {customer_name}!👋\n\nЧтобы мы могли быстро оформить заказ и курьер смог связаться с вами "
        f"в случае необходимости, пожалуйста, нажмите на кнопку 'Поделиться номером'!\n\n"
        f"<i>*При регистрации с компьютера нажмите на значок команд рядом с полем ввода.</i>\n\n"
        f"<i>*Отправка номера возможно только по клику на кнопку!</i>\n\n"
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
        f"- Customer 🧍\n"
        f"- Handler StateFilter: {handle_state}\n"
        f"- Customer telegram ID: {tg_id}\n"
        f"- Customer message: {customer_name}\n"
        f"- Customer state now: {current_state}\n"
        f"- Is name set: {is_name_set}"
    )

    log.info(f"data_name_customer was successfully done!")


@customer_r.message(filters.StateFilter(CustomerState.reg_Phone))
async def data_phone_customer(message: Message, state: FSMContext):
    log.info(f"data_phone_customer was called!")

    handler = MessageHandler(state, message.bot)
    handle_state = await state.get_state()
    bot_id = message.bot.id
    tg_id = message.from_user.id
    customer_phone = message.contact.phone_number
    current_state = CustomerState.reg_City.state

    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)
    is_phone_set = await rediska.set_user_phone(bot_id, tg_id, customer_phone)

    text = (
        f"Последний шаг!\n\n"
        f"Для того чтобы каждый раз не указывать город доставки, "
        f"скажите в каком городе вы будете в основном делать заказы "
        f"и он автоматически будет подставляться.\n\n"
        f"<b>Ваш город:</b>"
    )

    await handler.delete_previous_message(message.chat.id)
    new_message = await message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )
    await handler.handle_new_message(new_message, message)

    log.info(
        f"\n"
        f"- Customer 🧍\n"
        f"- Handler StateFilter: {handle_state}\n"
        f"- Customer telegram ID: {tg_id}\n"
        f"- Customer message: {customer_phone}\n"
        f"- Customer state now: {current_state}\n"
        f"- Is phone set: {is_phone_set}"
    )

    log.info(f"data_phone_customer was successfully done!")


@customer_r.message(filters.StateFilter(CustomerState.reg_City))
async def data_city_customer(message: Message, state: FSMContext):
    log.info(f"data_city_customer was called!")

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

    current_state = CustomerState.reg_tou.state

    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)
    is_city_set = await rediska.set_user_city(bot_id, tg_id, city)

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
    await handler.delete_previous_message(message.chat.id)
    new_message = await message.answer(
        text, reply_markup=reply_kb, disable_notification=True, parse_mode="HTML"
    )
    await handler.handle_new_message(new_message, message)

    log.info(
        f"\n"
        f"- Customer 🧍\n"
        f"- Handler StateFilter: {handle_state}\n"
        f"- Customer telegram ID: {tg_id}\n"
        f"- Customer city: {city}, score: {score}\n"
        f"- Customer state now: {current_state}\n"
        f"- Is city set: {is_city_set}"
    )

    log.info(f"data_city_customer was successfully done!")


@customer_r.callback_query(F.data == "accept_tou")
async def customer_accept_tou(callback_query: CallbackQuery, state: FSMContext):
    log.info(f"customer_accept_tou was called!")

    handler = MessageHandler(state, callback_query.bot)
    bot_id = callback_query.bot.id
    tg_id = callback_query.from_user.id
    current_state = CustomerState.default.state

    accept_tou = (
        "Пользовательское соглашение и правила использования сервиса - Принимаю"
    )

    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)
    await rediska.set_user_tou(bot_id, tg_id, accept_tou)
    await rediska.set_reg(bot_id, tg_id, True)

    customer_name, customer_phone, customer_city, tou = await rediska.get_user_info(
        bot_id, tg_id
    )

    is_new_customer_add = await customer_data.set_customer(
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
    await handler.handle_new_message(new_message, callback_query.message)

    log.info(
        f"\n"
        f"- Customer 🧍\n"
        f"- Handler F.data: {F.data}\n"
        f"- Customer telegram ID: {tg_id}\n"
        f"- Customer click: {accept_tou}\n"
        f"- Customer state now: {current_state}\n"
        f"- Is new customer add: {is_new_customer_add}"
    )

    log.info(f"customer_accept_tou was successfully done!")


# ---


@customer_r.message(F.text == "/order")
async def cmd_order(message: Message, state: FSMContext):
    log.info(f"cmd_order was called!")

    bot_id = message.bot.id
    tg_id = message.from_user.id
    current_state = None

    is_read_info = await rediska.is_read_info(bot_id, tg_id)

    log.info(f"is_read: {is_read_info}")

    if is_read_info:

        current_state = CustomerState.ai_voice_order.state
        await state.set_state(current_state)
        await rediska.set_state(bot_id, tg_id, current_state)

        text = (
            "<i>*Вы можете отправить как голосовое сообщение так и текстовое, "
            "заказ будет оформлен в считанные секунды.</i>"
        )

        await message.answer(
            text=f"{text}\n\nゞ <b>Опишите ваш заказ ...</b>",
            disable_notification=True,
            parse_mode="HTML",
        )

    else:

        current_state = CustomerState.default.state
        await state.set_state(current_state)
        await rediska.set_state(bot_id, tg_id, current_state)

        photo_title = await title.get_title_customer(message.text)
        reply_kb = await kb.get_customer_kb(message.text)
        text = (
            "◉ Вы можете сделать заказ с помощью текста или голоса, "
            "и наш ИИ ассистент быстро его обработает и передаст курьеру.\n\n"
            "<i>*При записи голосового сообщения или набора текста описывайте заказ так, как вам удобно, "
            "ассистент создаст заявку для вашего заказа.</i>"
        )

        await message.answer_photo(
            photo=photo_title,
            caption=text,
            reply_markup=reply_kb,
            disable_notification=True,
            parse_mode="HTML",
        )

    log.info(
        f"\n"
        f"- Customer 🧍\n"
        f"- Handler F.text: {F.text}\n"
        f"- Customer telegram ID: {tg_id}\n"
        f"- Customer state now: {current_state}\n"
        f"- Is read info order: {is_read_info}"
    )

    log.info(f"cmd_order was successfully done!")


@customer_r.message(F.text == "/profile")
async def cmd_profile(message: Message, state: FSMContext):
    log.info(f"cmd_profile was called!")

    bot_id = message.bot.id
    tg_id = message.from_user.id
    current_state = CustomerState.default.state

    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)

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

    await message.answer(
        text, reply_markup=reply_kb, disable_notification=True, parse_mode="HTML"
    )

    log.info(
        f"\n"
        f"- Customer 🧍\n"
        f"- Handler F.text: {F.text}\n"
        f"- Customer telegram ID: {tg_id}\n"
        f"- Customer state now: {current_state}\n"
    )

    log.info(f"cmd_profile was successfully done!")


@customer_r.message(F.text == "/faq")
async def cmd_faq(message: Message, state: FSMContext):
    log.info(f"cmd_faq was called!")

    bot_id = message.bot.id
    tg_id = message.from_user.id
    current_state = CustomerState.default.state

    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)

    text = (
        f"🤔 <b>Вопросы и ответы</b>\n\n"
        f"Частые вопросы и ответы на них "
        f"<a href='https://drive.google.com/file/d/1cXYK_FqU7kRpTU9p04dVjcE4vRbmNvMw/view?usp=sharing'>FAQ</a>"
    )

    await message.answer(text, disable_notification=True, parse_mode="HTML")

    log.info(
        f"\n"
        f"- Customer 🧍\n"
        f"- Handler F.text: {F.text}\n"
        f"- Customer telegram ID: {tg_id}\n"
        f"- Customer state now: {current_state}\n"
    )

    log.info(f"cmd_faq was successfully done!")


@customer_r.message(F.text == "/rules")
async def cmd_rules(message: Message, state: FSMContext):
    log.info(f"cmd_rules was called!")

    bot_id = message.bot.id
    tg_id = message.from_user.id
    current_state = CustomerState.default.state

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

    await message.answer(text, disable_notification=True, parse_mode="HTML")

    log.info(
        f"\n"
        f"- Customer 🧍\n"
        f"- Handler F.text: {F.text}\n"
        f"- Customer telegram ID: {tg_id}\n"
        f"- Customer state now: {current_state}\n"
    )

    log.info(f"cmd_rules was successfully done!")


@customer_r.message(F.text == "/become_courier")
async def cmd_become_courier(message: Message, state: FSMContext):
    log.info(f"cmd_become_courier was called!")

    bot_id = message.bot.id
    tg_id = message.from_user.id
    current_state = CustomerState.default.state

    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)

    photo_title = await title.get_title_customer("/become_courier")
    text = (
        "⦿ Стать курьером у нас — это отличный способ заработать без комиссии!\n\n"
        "⦿ Работайте в удобное время, выбирайте заказы рядом и получайте бонусы за быструю доставку.\n\n"
        "⦿ Зарабатывайте до 7000₽ в день уже сегодня!"
    )
    reply_kb = await kb.get_customer_kb("/become_courier")

    await message.answer_photo(
        photo=photo_title,
        caption=text,
        reply_markup=reply_kb,
        disable_notification=True,
    )

    log.info(
        f"\n"
        f"- Customer 🧍\n"
        f"- Handler F.text: {F.text}\n"
        f"- Customer telegram ID: {tg_id}\n"
        f"- Customer state now: {current_state}\n"
    )

    log.info(f"cmd_become_courier was successfully done!")


# ---


@customer_r.callback_query(F.data == "ai_order")
async def data_ai(callback_query: CallbackQuery, state: FSMContext):
    log.info(f"data_ai was called!")

    bot_id = callback_query.bot.id
    tg_id = callback_query.from_user.id
    current_state = CustomerState.ai_voice_order.state

    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)
    is_set = await rediska.set_read_info(bot_id, tg_id, True)

    log.info(f"\n" f"- Customer 🧍\n" f"- Is read info set: {is_set}")

    text = (
        "<i>*Вы можете отправить как голосовое сообщение так и текстовое, "
        "заказ будет оформлен в считанные секунды.</i>"
    )

    await callback_query.message.answer(
        text=f"{text}\n\nゞ <b>Опишите ваш заказ ...</b>",
        disable_notification=True,
        parse_mode="HTML",
    )

    log.info(
        f"\n"
        f"- Customer 🧍\n"
        f"- Handler F.data: {F.data}\n"
        f"- Customer telegram ID: {tg_id}\n"
        f"- Customer state now: {current_state}\n"
        f"- Is set read info order: {is_set}"
    )

    log.info(f"data_ai was successfully done!")


# ---


@customer_r.callback_query(F.data == "set_my_name")
async def set_name(callback_query: CallbackQuery, state: FSMContext):
    log.info(f"set_name was called!")

    bot_id = callback_query.bot.id
    tg_id = callback_query.from_user.id
    current_state = CustomerState.change_Name.state

    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)

    text = f"Изменить данные профиля.\n\n" f"<b>Ваше имя:</b>"
    await callback_query.message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )

    log.info(
        f"\n"
        f"- Customer 🧍\n"
        f"- Handler F.data: {F.data}\n"
        f"- Customer telegram ID: {tg_id}\n"
        f"- Customer state now: {current_state}\n"
    )

    log.info(f"set_name was successfully done!")


@customer_r.callback_query(F.data == "set_my_phone")
async def set_phone(callback_query: CallbackQuery, state: FSMContext):
    log.info(f"set_phone was called!")

    handler = MessageHandler(state, callback_query.bot)
    bot_id = callback_query.bot.id
    tg_id = callback_query.from_user.id
    current_state = CustomerState.change_Phone.state

    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)

    reply_kb = await kb.get_customer_kb("phone_number")
    text = f"Изменить данные профиля.\n\n" f"<b>Ваш Телефон:</b>"
    new_message = await callback_query.message.answer(
        text, disable_notification=True, reply_markup=reply_kb, parse_mode="HTML"
    )
    await handler.handle_new_message(new_message, callback_query.message)

    log.info(
        f"\n"
        f"- Customer 🧍\n"
        f"- Handler F.data: {F.data}\n"
        f"- Customer telegram ID: {tg_id}\n"
        f"- Customer state now: {current_state}\n"
    )

    log.info(f"set_phone was successfully done!")


@customer_r.callback_query(F.data == "set_my_city")
async def set_city(callback_query: CallbackQuery, state: FSMContext):
    log.info(f"set_city was called!")

    bot_id = callback_query.bot.id
    tg_id = callback_query.from_user.id
    current_state = CustomerState.change_City.state

    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)

    text = f"Изменить данные профиля.\n\n" f"<b>Ваш город:</b>"
    await callback_query.message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )

    log.info(
        f"\n"
        f"- Customer 🧍\n"
        f"- Handler F.data: {F.data}\n"
        f"- Customer telegram ID: {tg_id}\n"
        f"- Customer state now: {current_state}\n"
    )

    log.info(f"set_city was successfully done!")


# ---


@customer_r.message(filters.StateFilter(CustomerState.change_Name))
async def change_name(message: Message, state: FSMContext):
    log.info(f"change_name was called!")

    bot_id = message.bot.id
    tg_id = message.from_user.id
    name = message.text
    current_state = CustomerState.default.state

    new_name_was_set = await customer_data.update_customer_name(tg_id, name)
    new_name_was_set_redis = await rediska.set_user_name(bot_id, tg_id, name)
    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)

    log.info(f"new_name_was_set_redis: {new_name_was_set_redis}")
    text = f"Имя было изменено на {name} 🎉\n\n" f"▼ <b>Выберите действие ...</b>"

    await message.answer(text, disable_notification=True, parse_mode="HTML")

    log.info(
        f"\n"
        f"- Customer 🧍\n"
        f"- Customer telegram ID: {tg_id}\n"
        f"- Customer message: {message.text}\n"
        f"- Customer state now: {current_state}\n"
        f"- new_name_was_set: {new_name_was_set}\n"
    )

    log.info(f"change_name was successfully done!")


@customer_r.message(filters.StateFilter(CustomerState.change_Phone))
async def change_phone(message: Message, state: FSMContext):
    log.info(f"change_phone was called!")

    handler = MessageHandler(state, message.bot)
    bot_id = message.bot.id
    tg_id = message.from_user.id
    phone = message.contact.phone_number
    current_state = CustomerState.default.state

    new_phone_was_set = await customer_data.update_customer_phone(tg_id, phone)
    new_phone_was_set_redis = await rediska.set_user_phone(bot_id, tg_id, phone)
    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)

    log.info(f"new_phone_was_set_redis: {new_phone_was_set_redis}")

    text = f"Номер был изменено на {phone} 🎉\n\n" f"▼ <b>Выберите действие ...</b>"

    await handler.delete_previous_message(message.chat.id)

    new_message = await message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )

    await handler.handle_new_message(new_message, message)

    log.info(
        f"\n"
        f"- Customer 🧍\n"
        f"- Customer telegram ID: {tg_id}\n"
        f"- Customer message: {message.text}\n"
        f"- Customer state now: {current_state}\n"
        f"- new_phone_was_set: {new_phone_was_set}\n"
    )

    log.info(f"change_phone was successfully done!")


@customer_r.message(filters.StateFilter(CustomerState.change_City))
async def change_city(message: Message, state: FSMContext):
    log.info(f"change_city was called!")

    bot_id = message.bot.id
    tg_id = message.from_user.id

    russian_cities = await cities.get_cities()
    city, score = await find_closest_city(message.text, russian_cities)

    current_state = CustomerState.default.state

    if not city:
        text = f"Введите корректное название города!\n<b>Ваш город:</b>"

        new_message = await message.answer(
            text, disable_notification=True, parse_mode="HTML"
        )

        log.info(f"city name was uncorrectable: {city}\n" f"text message: {text}\n")

        await handler.delete_previous_message(message.chat.id)
        await handler.handle_new_message(new_message, message)

        return

    new_city_was_set = await customer_data.update_customer_city(tg_id, city)
    new_city_was_set_redis = await rediska.set_user_city(bot_id, tg_id, city)
    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)

    log.info(f"new_phone_was_set_redis: {new_city_was_set_redis}")

    text = f"Город был изменен на {city} 🎉\n\n" f"▼ <b>Выберите действие ...</b>"

    await message.answer(text, disable_notification=True, parse_mode="HTML")

    log.info(
        f"\n"
        f"- Customer 🧍\n"
        f"- Customer telegram ID: {tg_id}\n"
        f"- Customer message: {message.text}\n"
        f"- Customer state now: {current_state}\n"
        f"- new_city_was_set: {new_city_was_set}, score: {score}\n"
    )

    log.info(f"change_city was successfully done!")


# ---


@customer_r.message(F.text == "/my_orders")
@customer_r.callback_query(F.data == "back_myOrders")
async def handle_my_orders(event, state: FSMContext):
    log.info(f"handle_my_orders was called!")

    is_callback = isinstance(event, CallbackQuery)
    tg_id = event.from_user.id
    chat_id = event.message.chat.id if is_callback else event.chat.id
    bot = event.bot
    bot_id = event.bot.id
    current_state = CustomerState.myOrders.state

    if not is_callback:
        handler = MessageHandler(state, bot)
        await handler.delete_previous_message(chat_id)

    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)

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

    if is_callback:
        await event.message.edit_text(
            text, reply_markup=reply_kb, disable_notification=True, parse_mode="HTML"
        )
    else:
        await event.answer(
            text, reply_markup=reply_kb, disable_notification=True, parse_mode="HTML"
        )

    log.info(
        f"\n"
        f"- Customer 🧍\n"
        f"- Customer telegram ID: {tg_id}\n"
        f"- Customer event info: {event.data if is_callback else event.text}\n"
        f"- Customer state now: {current_state}\n"
    )

    log.info(f"handle_my_orders was successfully done!")


@customer_r.callback_query(
    F.data.in_(
        {
            "pending_orders",
            "active_orders",
            "completed_orders",
        }
    )
)
async def get_orders(callback_query: CallbackQuery, state: FSMContext):

    log.info(f"handle_my_orders was called!")

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
            reply_markup=await kb.get_customer_kb("one_my_order"),
            disable_notification=True,
            parse_mode="HTML",
        )
        log.info(
            f"Конец выполнения get_orders: успешно переключен заказ #{counter + 1}"
        )
        return

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

    tg_id = callback_query.from_user.id
    bot_id = callback_query.bot.id
    current_status = state_status if state_status else CustomerState.default.state
    customer_orders = await get_orders_func(tg_id)

    await state.set_state(state_status)
    await rediska.set_state(bot_id, tg_id, current_status)
    await rediska.save_fsm_state(state, bot_id, tg_id)

    orders_data = []
    for index, order in enumerate(customer_orders, start=1):
        order_forma = (
            zlib.decompress(order.order_forma).decode("utf-8")
            if order.order_forma
            else "-"
        )

        log.info(f"Формирование заказа #{order.order_id}: order_forma={order_forma}")

        base_info = (
            f"<b>{index}/{len(customer_orders)}</b>\n"
            f"<b>Заказ: №{order.order_id}</b>\n"
            f"---------------------------------------------\n"
            f"{order_forma}"
        )
        orders_data.append((base_info, order.order_id))

    if not orders_data:
        log.info(f"Нет {status_text} заказов для пользователя tg_id={tg_id}")
        await callback_query.message.edit_text(
            f"У вас нет {status_text} заказов.",
            reply_markup=await kb.get_customer_kb("one_my_order"),
            disable_notification=True,
        )
        log.info(f"Конец выполнения get_orders: заказов не найдено")
        return

    await state.update_data(orders_data=orders_data, counter=0)
    reply_kb = await kb.get_customer_kb(
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


@customer_r.callback_query(F.data.in_({"next_right_mo", "back_left_mo"}))
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


@customer_r.callback_query(F.data == "cancel_my_order")
async def cancel_my_order(callback_query: CallbackQuery, state: FSMContext):

    log.info(f"cancel_my_order was called!")

    data = await state.get_data()
    current_order_id = data.get("current_order_id")

    if not current_order_id:
        await callback_query.message.answer("Не удалось найти заказ для отмены.")
        return

    order = await order_data.get_order_by_id(current_order_id)

    if order.order_status != OrderStatus.PENDING:
        await callback_query.message.answer(
            f"Заказ №{current_order_id} нельзя отменить, так как он не в статусе ожидания."
        )
        return

    is_canceled = await order_data.update_order_status(
        current_order_id, OrderStatus.CANCELLED
    )
    text = (
        f"<b>Заказ №{current_order_id} успешно отменен.</b>\n\n"
        f"<i>*Посмотреть информацию вы можете в своих заказах в пункте</i> <b>Отмененные.</b>\n\n"
        f"▼ <b>Выберите действие ...</b>"
    )
    await callback_query.message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )

    log.info(f"order {current_order_id} is_canceled: {is_canceled}")
    log.info(f"cancel_my_order was successfully done!")


# ---


@customer_r.message(
    filters.StateFilter(CustomerState.ai_voice_order),
    F.content_type.in_([ContentType.VOICE, ContentType.TEXT]),
)
async def process_order(message: Message, state: FSMContext):
    log.info(f"process_message was called!")

    handler = MessageHandler(state, message.bot)
    wait_message = await message.answer(
        f"Заказ обрабатывается, подождите ...", disable_notification=True
    )

    error_messages = [
        "⚠ Ошибка при обработке заказа.\nПопробуйте снова",
        "Мы не смогли определить ваш заказ.\n Попробуйте переформулировать заказ более четко и повторить попытку.",
        "⚠ Время обработки заказа превышено. Попробуйте снова.",
    ]

    text_msg = None

    start_time = time.perf_counter()

    if message.content_type == ContentType.VOICE:
        log.info(f"content_type is Voice!\nProcess to recognition voice start.")

        recognized_text = await recognizer.get_recognition_text(message)

        if not recognized_text:
            rerecord_kb = await kb.get_customer_kb("rerecord")
            new_message = await message.answer(
                text=error_messages[1],
                reply_markup=rerecord_kb,
                disable_notification=True,
            )
            await wait_message.delete()
            await handler.handle_new_message(new_message, message)

            log.warning(f"Can't recognize voice!")

            return
        else:
            log.info(f"Voice was recognized")

            text_msg = recognized_text
    else:
        log.info(f"content_type is Text")

        text_msg = message.text

    try:
        log.info(f"Tying to process_order_logic.")
        await asyncio.wait_for(
            process_order_logic(
                text_msg,
                message,
                state,
                handler,
                wait_message,
                error_messages,
            ),
            timeout=120,
        )
    except asyncio.TimeoutError:
        new_message = await message.answer(
            error_messages[2],
            reply_markup=await kb.get_customer_kb("rerecord"),
            disable_notification=True,
        )
        await wait_message.delete()
        await handler.handle_new_message(new_message, message)

        log.info(f"Output error message: {new_message}")
        log.error(f"Error: asyncio.TimeoutError")

    except Exception as e:
        new_message = await message.answer(
            error_messages[0],
            reply_markup=await kb.get_customer_kb("rerecord"),
            disable_notification=True,
        )
        await wait_message.delete()
        await handler.handle_new_message(new_message, message)

        log.info(f"Output error message: {new_message}")
        log.error(f"Error: {e}")

    end_time = time.perf_counter()
    execution_time = end_time - start_time

    log.info(f"Execution time process_message: {execution_time:.4f} sec")


async def process_order_logic(
    text_msg: str,
    message: Message,
    state: FSMContext,
    handler: MessageHandler,
    wait_message: Message,
    error_messages: list,
):

    log.info(f"process_order_logic was called!")

    bot_id = message.bot.id
    tg_id = message.from_user.id
    chat_id = message.chat.id
    current_state = CustomerState.assistant_run.state
    customer_name = await rediska.get_user_name(bot_id, tg_id)
    customer_phone = await rediska.get_user_phone(bot_id, tg_id)
    customer_city = await rediska.get_user_city(bot_id, tg_id)

    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)

    await handler.delete_previous_message(chat_id)

    try:
        city, addresses, delivery_object, description = await assistant.process_order(
            text_msg, customer_city
        )

        if city == "N":
            new_message = await message.answer(
                error_messages[1],
                reply_markup=await kb.get_customer_kb("rerecord"),
                disable_notification=True,
            )
            await wait_message.delete()
            await handler.handle_new_message(new_message, message)

            log.warning(f" Оформление заказа не удалось! Модерация не прошла")

            return

        log.info("request was successfully done")
    except Exception as e:
        new_message = await message.answer(
            error_messages[0],
            reply_markup=await kb.get_customer_kb("rerecord"),
            disable_notification=True,
        )
        await wait_message.delete()
        await handler.handle_new_message(new_message, message)

        log.info(f"Output error message: {new_message}")
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

    full_rout = prepare_dict.get("yandex_maps_url")
    distance = prepare_dict.get("distance")
    price = prepare_dict.get("price")

    add_order_info = (
        f"<b>Ваш заказ</b> ✍︎\n---------------------------------------------\n\n"
    )
    order_info = await formatter.format_order_form(prepare_dict)

    moscow_time_str = moscow_time.isoformat()

    state_data = {
        "moscow_time_str": moscow_time_str,
        "city": city,
        "customer_name": customer_name,
        "customer_phone": customer_phone,
        "addresses": addresses,
        "delivery_object": delivery_object,
        "description": description,
        "order_info": order_info,
        "yandex_maps_url": full_rout,
        "distance": distance,
        "price": price,
    }

    await state.update_data(current_order_info=(state_data, order_info))
    await rediska.save_fsm_state(state, bot_id, tg_id)

    order_forma = add_order_info + order_info

    reply_kb = await kb.get_customer_kb("voice_order_accept")

    new_message = await message.answer(
        order_info, reply_markup=reply_kb, disable_notification=True, parse_mode="HTML"
    )

    log.info(f"Order form:\n\n{order_forma}\n")

    await wait_message.delete()
    await handler.handle_new_message(new_message, message)

    log.info(f"process_order_logic was successfully done!")


# ---


@customer_r.callback_query(F.data == "order_sent")
async def set_order_to_db(callback_query: CallbackQuery, state: FSMContext):

    log.info(f"set_order_to_db was called!")

    bot_id = callback_query.bot.id
    tg_id = callback_query.from_user.id
    handler = MessageHandler(state, callback_query.bot)

    state_data = await state.get_data()
    current_order_info = state_data.get("current_order_info")

    current_state = CustomerState.default.state

    if current_order_info:
        data, order_forma = [*current_order_info]
        order_forma = zlib.compress(order_forma.encode("utf-8"))
    else:
        log.error("Ключ 'current_order_info' отсутствует в состоянии FSM")
        await callback_query.message.answer(
            "Ошибка: данные заказа не найдены.", disable_notification=True
        )
        return

    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)

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

    await handler.handle_new_message(new_message, callback_query.message)

    log.info(f"set_order_to_db was successfully done!")


# ---


@customer_r.callback_query(F.data == "cancel_order")
async def cancel_order(callback_query: CallbackQuery, state: FSMContext):
    log.info(f"cancel_order was called!")

    handler = MessageHandler(state, callback_query.bot)
    bot_id = callback_query.bot.id
    tg_id = callback_query.from_user.id
    current_state = CustomerState.default.state

    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)

    text = "▼ <b>Выберите действие ...</b>"
    new_message = await callback_query.message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )
    await handler.handle_new_message(new_message, callback_query.message)

    log.info(
        f"\n"
        f"- Customer 🧍\n"
        f"- Handler F.data: {F.data}\n"
        f"- Customer telegram ID: {tg_id}\n"
        f"- Customer state now: {current_state}\n"
    )

    log.info(f"cancel_order was successfully done!")


# ---


@customer_fallback.message()
async def handle_unrecognized_message(message: Message):
    log.info(f"Data to delete: {message.text}")
    await message.delete()
