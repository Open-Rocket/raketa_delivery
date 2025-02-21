# ------------------------------------------------------- ✺ Start ✺ ------------------------------------------------ #
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
    Router,
    datetime,
    time,
    moscow_time,
    customer_r,
    customer_fallback,
    kb,
    title,
    customer_data,
    order_data,
    route,
    recognizer,
    rediska,
    assistant,
    log,
    F,
)


# ------------------------------------------------------------------------------------------------------------------- #
#                                                     ⇣ MDW ⇣
# ------------------------------------------------------------------------------------------------------------------- #


# middlewares_Outer
customer_r.message.outer_middleware(CustomerOuterMiddleware(rediska))
customer_r.callback_query.outer_middleware(CustomerOuterMiddleware(rediska))


# ------------------------------------------------------------------------------------------------------------------- #
#                                              ⇣ Registration steps ⇣
# ------------------------------------------------------------------------------------------------------------------- #


# /start
@customer_r.message(CommandStart())
async def cmd_start_customer(message: Message, state: FSMContext) -> None:
    log.info(f"cmd_start_customer was called!")

    bot_id = message.bot.id
    tg_id = message.from_user.id
    current_state = CustomerState.reg_state.state

    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)

    handler = MessageHandler(state, message.bot)
    is_reg = await rediska.is_reg(bot_id, tg_id)

    if is_reg:
        default_state = CustomerState.default.state
        await state.set_state(default_state)
        await rediska.set_state(bot_id, tg_id, default_state)
        text = "▼ <b>Выберите действие ...</b>"
        await handler.delete_previous_message(message.chat.id)
        new_message = await message.answer(
            text, parse_mode="HTML", disable_notification=True
        )
        await handler.handle_new_message(new_message, message)
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
        f"- Customer 🧍\n"
        f"- Handler /start\n"
        f"- Customer telegram ID: {tg_id}\n"
        f"- Customer message: {message.text}\n"
        f"- Customer state now: {current_state}"
    )

    log.info(f"cmd_start_customer was successfully done!")


# registration_Name
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


# registration_Phone
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


# registration_City
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


# terms of use
@customer_r.message(filters.StateFilter(CustomerState.reg_City))
async def data_city_customer(message: Message, state: FSMContext):
    log.info(f"data_city_customer was called!")

    handler = MessageHandler(state, message.bot)
    handle_state = await state.get_state()
    bot_id = message.bot.id
    tg_id = message.from_user.id
    customer_city = message.text
    current_state = CustomerState.reg_tou.state

    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)
    is_city_set = await rediska.set_user_city(bot_id, tg_id, customer_city)

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
        f"- Customer message: {customer_city}\n"
        f"- Customer state now: {current_state}\n"
        f"- Is city set: {is_city_set}"
    )

    log.info(f"data_city_customer was successfully done!")


# tou Accept registration was done
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


# ------------------------------------------------------------------------------------------------------------------- #
#                                                    ⇣ Bot functions ⇣
# ------------------------------------------------------------------------------------------------------------------- #


# order
@customer_r.message(F.text == "/order")
async def cmd_order(message: Message, state: FSMContext):
    log.info(f"cmd_order was called!")

    handler = MessageHandler(state, message.bot)
    bot_id = message.bot.id
    tg_id = message.from_user.id
    current_state = None

    is_read_info = await rediska.is_read_info(bot_id, tg_id)

    await handler.delete_previous_message(message.chat.id)

    if not is_read_info:
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

        new_message = await message.answer_photo(
            photo=photo_title,
            caption=text,
            reply_markup=reply_kb,
            disable_notification=True,
            parse_mode="HTML",
        )

    else:
        current_state = CustomerState.ai_voice_order.state
        await state.set_state(current_state)
        await rediska.set_state(bot_id, tg_id, current_state)

        text = (
            "<i>*Вы можете отправить как голосовое сообщение так и текстовое, "
            "заказ будет оформлен в считанные секунды.</i>"
        )

        new_message = await message.answer(
            text=f"{text}\n\nゞ <b>Опишите ваш заказ ...</b>",
            disable_notification=True,
            parse_mode="HTML",
        )

    await handler.handle_new_message(new_message, message)

    log.info(
        f"\n"
        f"- Customer 🧍\n"
        f"- Handler F.text: {F.text}\n"
        f"- Customer telegram ID: {tg_id}\n"
        f"- Customer state now: {current_state}\n"
        f"- Is read info order: {is_read_info}"
    )

    log.info(f"cmd_order was successfully done!")


# commands_Profile
@customer_r.message(F.text == "/profile")
async def cmd_profile(message: Message, state: FSMContext):
    log.info(f"cmd_profile was called!")

    handler = MessageHandler(state, message.bot)
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

    await handler.delete_previous_message(message.chat.id)

    new_message = await message.answer(
        text, reply_markup=reply_kb, disable_notification=True, parse_mode="HTML"
    )
    await handler.handle_new_message(new_message, message)

    log.info(
        f"\n"
        f"- Customer 🧍\n"
        f"- Handler F.text: {F.text}\n"
        f"- Customer telegram ID: {tg_id}\n"
        f"- Customer state now: {current_state}\n"
    )

    log.info(f"cmd_profile was successfully done!")


# faq
@customer_r.message(F.text == "/faq")
async def cmd_faq(message: Message, state: FSMContext):
    log.info(f"cmd_faq was called!")

    handler = MessageHandler(state, message.bot)
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

    await handler.delete_previous_message(message.chat.id)

    new_message = await message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )
    await handler.handle_new_message(new_message, message)

    log.info(
        f"\n"
        f"- Customer 🧍\n"
        f"- Handler F.text: {F.text}\n"
        f"- Customer telegram ID: {tg_id}\n"
        f"- Customer state now: {current_state}\n"
    )

    log.info(f"cmd_faq was successfully done!")


# rules
@customer_r.message(F.text == "/rules")
async def cmd_rules(message: Message, state: FSMContext):
    log.info(f"cmd_rules was called!")

    handler = MessageHandler(state, message.bot)
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

    await handler.delete_previous_message(message.chat.id)

    new_message = await message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )
    await handler.handle_new_message(new_message, message)

    log.info(
        f"\n"
        f"- Customer 🧍\n"
        f"- Handler F.text: {F.text}\n"
        f"- Customer telegram ID: {tg_id}\n"
        f"- Customer state now: {current_state}\n"
    )

    log.info(f"cmd_rules was successfully done!")


# commands_BecomeCourier
@customer_r.message(F.text == "/become_courier")
async def cmd_become_courier(message: Message, state: FSMContext):
    log.info(f"cmd_become_courier was called!")

    handler = MessageHandler(state, message.bot)
    bot_id = message.bot.id
    tg_id = message.from_user.id
    current_state = CustomerState.default.state

    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)

    photo_title = await title.get_title_customer(message.text)
    text = (
        "⦿ Стать курьером у нас — это отличный способ заработать без комиссии!\n\n"
        "⦿ Работайте в удобное время, выбирайте заказы рядом и получайте бонусы за быструю доставку.\n\n"
        "⦿ Зарабатывайте до 7000₽ в день уже сегодня!"
    )
    reply_kb = await kb.get_customer_kb(message)

    await handler.delete_previous_message(message.chat.id)

    new_message = await message.answer_photo(
        photo=photo_title,
        caption=text,
        reply_markup=reply_kb,
        disable_notification=True,
    )

    await handler.handle_new_message(new_message, message)

    log.info(
        f"\n"
        f"- Customer 🧍\n"
        f"- Handler F.text: {F.text}\n"
        f"- Customer telegram ID: {tg_id}\n"
        f"- Customer state now: {current_state}\n"
    )

    log.info(f"cmd_become_courier was successfully done!")


# read_Info
@customer_r.callback_query(F.data == "ai_order")
async def data_ai(callback_query: CallbackQuery, state: FSMContext):
    log.info(f"data_ai was called!")

    handler = MessageHandler(state, callback_query.bot)
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

    new_message = await callback_query.message.answer(
        text=f"{text}\n\nゞ <b>Опишите ваш заказ ...</b>",
        disable_notification=True,
        parse_mode="HTML",
    )
    await handler.handle_new_message(new_message, callback_query.message)

    log.info(
        f"\n"
        f"- Customer 🧍\n"
        f"- Handler F.data: {F.data}\n"
        f"- Customer telegram ID: {tg_id}\n"
        f"- Customer state now: {current_state}\n"
        f"- Is set read info order: {is_set}"
    )

    log.info(f"data_ai was successfully done!")


# cancel_Order
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


# set_my_name
@customer_r.callback_query(F.data == "set_my_name")
async def set_name(callback_query: CallbackQuery, state: FSMContext):
    log.info(f"set_name was called!")

    handler = MessageHandler(state, callback_query.bot)
    bot_id = callback_query.bot.id
    tg_id = callback_query.from_user.id
    current_state = CustomerState.change_Name.state

    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)

    text = f"Изменить данные профиля.\n\n" f"<b>Ваше имя:</b>"
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

    log.info(f"set_name was successfully done!")


# set_my_phone
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


# set_my_city
@customer_r.callback_query(F.data == "set_my_city")
async def set_city(callback_query: CallbackQuery, state: FSMContext):
    log.info(f"set_city was called!")

    handler = MessageHandler(state, callback_query.bot)
    bot_id = callback_query.bot.id
    tg_id = callback_query.from_user.id
    current_state = CustomerState.change_City.state

    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)

    text = f"Изменить данные профиля.\n\n" f"<b>Ваш город:</b>"
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

    log.info(f"set_city was successfully done!")


# change name state
@customer_r.message(filters.StateFilter(CustomerState.change_Name))
async def change_name(message: Message, state: FSMContext):
    log.info(f"change_name was called!")

    handler = MessageHandler(state, message.bot)
    bot_id = message.bot.id
    tg_id = message.from_user.id
    name = message.text
    current_state = CustomerState.default.state

    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)
    new_name_was_set = await customer_data.set_customer_name(tg_id, name)

    text = f"Имя было изменено на {name} 🎉\n\n" f"▼ <b>Выберите действие ...</b>"

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
        f"- new_name_was_set: {new_name_was_set}\n"
    )

    log.info(f"change_name was successfully done!")


# change phone state
@customer_r.message(filters.StateFilter(CustomerState.change_Phone))
async def change_phone(message: Message, state: FSMContext):
    log.info(f"change_phone was called!")

    handler = MessageHandler(state, message.bot)
    bot_id = message.bot.id
    tg_id = message.from_user.id
    phone = message.contact.phone_number
    current_state = CustomerState.default.state

    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)
    new_phone_was_set = await customer_data.set_customer_phone(tg_id, phone)

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


# change city state
@customer_r.message(filters.StateFilter(CustomerState.change_City))
async def change_city(message: Message, state: FSMContext):
    log.info(f"change_city was called!")

    handler = MessageHandler(state, message.bot)
    bot_id = message.bot.id
    tg_id = message.from_user.id
    city = message.text
    current_state = CustomerState.default.state

    await state.set_state(current_state)
    await rediska.set_state(bot_id, tg_id, current_state)
    new_city_was_set = await customer_data.set_customer_city(tg_id, city)

    text = f"Город был изменен на {city} 🎉\n\n" f"▼ <b>Выберите действие ...</b>"

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
        f"- new_city_was_set: {new_city_was_set}\n"
    )

    log.info(f"change_city was successfully done!")


# ------------------------------------------------------------------------------------------------------------------- #
#                                                   ⇣ User orders ⇣
# ------------------------------------------------------------------------------------------------------------------- #


# handler for /my_orders and back_myOrders
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
    canceled_count = len(await order_data.get_canceled_orders(tg_id))
    completed_count = len(await order_data.get_completed_orders(tg_id))

    reply_kb = await kb.get_customer_orders_kb(
        pending_count, active_count, canceled_count, completed_count
    )
    text = (
        f"✎ <b>Мои заказы</b>\n\n"
        f"Здесь вы можете посмотреть статус ваших заказов, "
        f"а также статистику за все время использования нашего сервиса.\n\n"
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
        f"- Customer 🧍\n"
        f"- Customer telegram ID: {tg_id}\n"
        f"- Customer event info: {event.data if is_callback else event.text}\n"
        f"- Customer state now: {current_state}\n"
    )

    log.info(f"handle_my_orders was successfully done!")


# customer orders
@customer_r.callback_query(
    F.data.in_(
        {
            "pending_orders",
            "active_orders",
            "canceled_orders",
            "completed_orders",
            "next_order",
            "prev_order",
        }
    )
)
async def get_orders(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    # Переключение между заказами (если нажали "следующий" или "предыдущий")
    if callback_query.data in {"next_order", "prev_order"}:
        counter = data.get("counter", 0)
        orders_text = data.get("orders_text", [])

        if not orders_text:
            await callback_query.answer("Нет доступных заказов.", show_alert=True)
            return

        total_orders = len(orders_text)
        counter = (
            (counter + 1) % total_orders
            if callback_query.data == "next_order"
            else (counter - 1) % total_orders
        )
        await state.update_data(counter=counter)

        await callback_query.message.edit_text(
            orders_text[counter],
            reply_markup=await kb.get_customer_kb("one_my_order"),
            disable_notification=True,
            parse_mode="HTML",
        )
        return

    # Определение типа заказа
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
        "canceled_orders": (
            order_data.get_canceled_orders,
            CustomerState.myOrders_canceled,
            "отменённых",
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
        await callback_query.answer("Ошибка запроса заказов.", show_alert=True)
        return

    # Получение заказов пользователя
    tg_id = callback_query.from_user.id
    bot_id = callback_query.bot.id
    current_status = state_status if state_status else CustomerState.default.state
    customer_orders = await get_orders_func(tg_id)

    await state.set_state(state_status)
    await rediska.set_state(bot_id, tg_id, current_status)
    await state.update_data(orders={order.order_id: order for order in customer_orders})
    await rediska.save_fsm_state(state, bot_id, tg_id)

    # --- continue from this point

    def format_address(number, address, url):
        return f"⦿ <b>Адрес {number}:</b> <a href='{url}'>{address}</a>\n"

    # Формирование текста для каждого заказа
    orders_text = []
    for index, order in enumerate(customer_orders, start=1):
        base_info = (
            f"<b>{index}/{len(customer_orders)}</b>\n"
            f"<b>Заказ: №{order.order_id}</b>\n"
            f"---------------------------------------------\n\n"
            f"<b>Город:</b> {order.order_city}\n\n"
            f"<b>Заказ №{order.order_id}</b>\n"
            f"<b>Дата оформления:</b> {order.created_at_moscow_time}\n"
            f"<b>Статус заказа:</b> {order.order_status.value}\n\n"
            f"<b>Заказчик:</b> {order.customer_name if order.customer_name else '-'}\n"
            f"<b>Телефон:</b> {order.customer_phone if order.customer_phone else '-'}\n\n"
        )

        base_info += format_address(1, order.starting_point_a, order.a_url)

        delivery_points = [
            (order.destination_point_b, order.b_url),
            (order.destination_point_c, order.c_url),
            (order.destination_point_d, order.d_url),
            (order.destination_point_e, order.e_url),
        ]

        for i, (point, url) in enumerate(delivery_points, start=2):
            if point:
                base_info += format_address(i, point, url)

        courier_name, courier_phone = await order_data.get_order_courier_info(
            order.order_id
        )

        base_info += (
            f"\n<b>Доставляем:</b> {order.delivery_object if order.delivery_object else '-'}\n"
            f"<b>Расстояние:</b> {order.distance_km} км\n"
            f"<b>Стоимость доставки:</b> {order.price_rub}₽\n\n"
            f"<b>Курьер:</b> {courier_name if courier_name else '-'}\n"
            f"<b>Телефон курьера:</b> {courier_phone if courier_phone else '-'}\n\n"
            f"<b>Описание:</b> <i>{order.description if order.description else '...'}</i>\n\n"
            f"---------------------------------------------\n"
            f"• Проверьте ваш заказ и если всё верно, то разместите.\n"
            f"• Курьер может связаться с вами для уточнения деталей!\n"
            f"• Оплачивайте курьеру наличными или переводом.\n\n"
            f"⦿⌁⦿ <a href='{order.full_rout}'>Маршрут доставки</a>\n\n"
        )

        orders_text.append(base_info)

    # Если заказов нет
    if not orders_text:
        await callback_query.message.edit_text(
            f"У вас нет {status_text} заказов.",
            reply_markup=await kb.get_customer_kb(text="one_my_order"),
            disable_notification=True,
        )
        return

    # Сохранение данных и отправка первого заказа
    await state.update_data(orders_text=orders_text, counter=0)
    reply_kb = await kb.get_customer_kb(
        text="one_my_order" if len(orders_text) == 1 else callback_query.data
    )

    await callback_query.message.edit_text(
        orders_text[0],
        reply_markup=reply_kb,
        disable_notification=True,
        parse_mode="HTML",
    )


# customer statistic
@customer_r.callback_query(F.data == "my_statistic")
async def get_my_statistic(callback_query: CallbackQuery, state: FSMContext):
    user_tg_id = callback_query.from_user.id

    # Получение статистики пользователя
    total_orders = await order_data.get_total_orders(user_tg_id) or 0
    completed_orders = await order_data.get_completed_orders_count(user_tg_id) or 0
    canceled_orders = await order_data.get_canceled_orders_count(user_tg_id) or 0
    avg_speed = await order_data.get_avg_order_speed(user_tg_id) or 0
    avg_distance = await order_data.get_avg_order_distance(user_tg_id) or 0
    fastest_order_speed = await order_data.get_fastest_order_speed(user_tg_id) or 0
    slowest_order_speed = await order_data.get_slowest_order_speed(user_tg_id) or 0
    avg_time = await order_data.get_avg_order_time(user_tg_id) or 0
    fastest_order_time = await order_data.get_fastest_order_time(user_tg_id) or 0
    longest_order_time = await order_data.get_longest_order_time(user_tg_id) or 0
    shortest_order_distance = (
        await order_data.get_shortest_order_distance(user_tg_id) or 0
    )
    longest_order_distance = (
        await order_data.get_longest_order_distance(user_tg_id) or 0
    )

    # Если заказов нет, то процент успешных заказов будет 0
    success_rate = (completed_orders / total_orders) * 100 if total_orders > 0 else 0

    avg_price = await order_data.get_avg_order_price(user_tg_id) or 0
    max_price = await order_data.get_max_order_price(user_tg_id) or 0
    min_price = await order_data.get_min_order_price(user_tg_id) or 0

    # Формирование текста для сообщения
    text = (
        f"☈ <b>Статистика заказов</b>\n\n"
        f"Всего заказов: {total_orders}\n"
        f"Выполненные: {completed_orders}\n"
        f"Отмененные: {canceled_orders}\n\n"
        f"Самый медленный (по скорости): {slowest_order_speed:.2f} км/ч\n"
        f"Самый быстрый (по скорости): {fastest_order_speed:.2f} км/ч\n"
        f"Средняя скорость выполнения: {avg_speed:.2f} км/ч\n\n"
        f"Самый долгий: {longest_order_time:.2f} мин\n"
        f"Самый быстрый (по времени): {fastest_order_time:.2f} мин\n"
        f"Среднее время выполнения: {avg_time:.2f} мин\n\n"
        f"Самое короткое расстояние: {shortest_order_distance:.2f} км\n"
        f"Самое большое расстояние: {longest_order_distance:.2f} км\n"
        f"Среднее расстояние: {avg_distance:.2f} км\n\n"
        f"Наименьшая стоимость: {min_price:.2f} руб.\n"
        f"Наибольшая стоимость: {max_price:.2f} руб.\n"
        f"Средняя стоимость: {avg_price:.2f} руб.\n\n"
        f"Процент успешных: {success_rate:.2f}%\n"
    )

    reply_kb = await kb.get_customer_kb(text="one_my_order")

    # Отправка сообщения пользователю
    await callback_query.message.edit_text(
        text, reply_markup=reply_kb, parse_mode="HTML"
    )


# handler for right button "⇥" to move forward
@customer_r.callback_query(F.data == "next_right_mo")
async def on_button_next_my_orders(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    orders_text = data.get("orders_text")
    orders = data.get("orders")
    counter = data.get("counter", 0)

    # Увеличиваем счетчик и зацикливаем его
    counter = (counter + 1) % len(orders_text)

    # Обновляем состояние с новым значением счетчика и ID текущего заказа
    current_order_id = list(orders.keys())[
        counter
    ]  # Получаем ID нового активного заказа
    await state.update_data(counter=counter, current_order_id=current_order_id)

    # Обновляем сообщение с новым заказом
    new_order_info = orders_text[counter]
    await callback_query.message.edit_text(
        new_order_info,
        reply_markup=callback_query.message.reply_markup,
        parse_mode="HTML",
    )


# handler for left button "⇤" to move back
@customer_r.callback_query(F.data == "back_left_mo")
async def on_button_back_my_orders(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    orders_text = data.get("orders_text")
    orders = data.get("orders")
    counter = data.get("counter", 0)

    # Уменьшаем счетчик и зацикливаем его
    counter = (counter - 1) % len(orders_text)

    # Обновляем состояние с новым значением счетчика
    current_order_id = list(orders.keys())[counter]
    await state.update_data(counter=counter, current_order_id=current_order_id)

    # Обновляем сообщение с новым заказом
    new_order_info = orders_text[counter]
    await callback_query.message.edit_text(
        new_order_info,
        reply_markup=callback_query.message.reply_markup,
        parse_mode="HTML",
    )


# ------------------------------------------------------------------------------------------------------------------- #
#                                                   ⇣ Cancel order ⇣
# ------------------------------------------------------------------------------------------------------------------- #


# cancel order from orders
@customer_r.callback_query(F.data == "cancel_my_order")
async def cancel_order(callback_query: CallbackQuery, state: FSMContext):
    handler = MessageHandler(state, callback_query.message.bot)
    data = await state.get_data()
    current_order_id = data.get("current_order_id")  # Получаем ID текущего заказа

    if not current_order_id:
        await callback_query.message.answer("Не удалось найти заказ для отмены.")
        return

    order = await order_data.get_order_by_id(current_order_id)

    if order.order_status != OrderStatus.PENDING:
        new_message = await callback_query.message.answer(
            f"Заказ №{current_order_id} нельзя отменить, так как он не в статусе ожидания."
        )
        return

    await order_data.update_order_status(current_order_id, OrderStatus.CANCELLED)
    text = (
        f"<b>Заказ №{current_order_id} успешно отменен.</b>\n\n"
        # f"<i>*Вы можете отменить заказ до того как курьер его принял и начал выполнять!</i>\n"
        f"<i>*Посмотреть информацию вы можете в своих заказах в пункте</i> <b>Отмененные.</b>\n\n"
        f"▼ <b>Выберите действие ...</b>"
    )
    new_message = await callback_query.message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )

    await handler.handle_new_message(new_message, callback_query.message)


# ------------------------------------------------------------------------------------------------------------------- #
#                                               ⇣ Formation of an order ⇣
# ------------------------------------------------------------------------------------------------------------------- #


# order process
@customer_r.message(
    filters.StateFilter(CustomerState.ai_voice_order),
    F.content_type.in_([ContentType.VOICE, ContentType.TEXT]),
)
async def process_message(message: Message, state: FSMContext):
    handler = MessageHandler(state, message.bot)
    wait_message = await message.answer(
        f"Заказ обрабатывается, подождите ...", disable_notification=True
    )

    try:
        await asyncio.wait_for(
            process_order_logic(message, state, handler, wait_message), timeout=120
        )
    except asyncio.TimeoutError:
        await wait_message.delete()
        new_message = await message.answer(
            "⚠ Время обработки заказа превышено. Попробуйте снова.",
            reply_markup=await kb.get_customer_kb(text="rerecord"),
            disable_notification=True,
        )
        await handler.handle_new_message(new_message, message)
    except Exception as e:
        await wait_message.delete()
        new_message = await message.answer(
            f"⚠ Ошибка при обработке заказа: {str(e)}",
            reply_markup=await kb.get_customer_kb(text="rerecord"),
            disable_notification=True,
        )
        await handler.handle_new_message(new_message, message)


# form_Order
async def process_order_logic(
    message: Message, state: FSMContext, handler, wait_message
):
    await state.set_state(CustomerState.waiting_Courier)
    await handler.delete_previous_message(message.chat.id)

    # Инициализация переменных
    reply_kb = await kb.get_customer_kb(text="voice_order_accept")
    rerecord_kb = await kb.get_customer_kb(text="rerecord")
    tg_id = message.from_user.id
    user_city = await customer_data.get_user_city(tg_id)
    customer_name, customer_phone = await customer_data.get_username_userphone(tg_id)
    new_message = "Ошибка распознавания. Попробуйте снова."

    recognized_text = await recognizer.get_recognition_text(message)

    # Если распознавание не удалось
    if not recognized_text:
        recognized_text = new_message
        new_message = await message.answer(
            text="Мы не смогли определить ваш заказ.\n Попробуйте переформулировать заказ более четко и повторить попытку.",
            reply_markup=rerecord_kb,
            disable_notification=True,
        )
        await wait_message.delete()
        await handler.handle_new_message(new_message, message)
        return

    # Обработка для разрешенных заказов (обычные товары)
    addresses = await get_parsed_addresses(recognized_text, user_city)

    if len(addresses) == 2:
        pickup_address, delivery_address = addresses
        pickup_coords = await route.get_coordinates(pickup_address)
        delivery_coords = await route.get_coordinates(delivery_address)
        all_coordinates = [pickup_coords, delivery_coords]

        if all(pickup_coords) and all(delivery_coords):

            # Формирование координат
            yandex_maps_url, pickup_point, delivery_point = await route.get_rout(
                pickup_coords, [delivery_coords]
            )

            distance, duration = await route.calculate_total_distance(all_coordinates)
            distance = round(distance, 2)
            price = await route.get_price(distance, moscow_time)

            # Структурирование данных заказа
            structured_data = await process_order_text(recognized_text)
            city = structured_data.get("City")

            if not city:
                city = user_city

            starting_point_a = structured_data.get("Starting point A")
            destination_point_b = structured_data.get("Destination point B")
            delivery_object = structured_data.get("Delivery object")
            description = structured_data.get("Description", None)

            # Сохранение данных в состоянии
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
                customer_name=customer_name,
                customer_phone=customer_phone,
                description=description,
                distance_km=distance,
                duration_min=duration,
                price_rub=price,
                order_text=recognized_text,
                order_time=moscow_time,
                yandex_maps_url=yandex_maps_url,
                pickup_point=pickup_point,
                delivery_point=delivery_point,
            )

            # Отправка ответа пользователю
            order_forma = (
                f"<b>Ваш заказ</b> ✍︎\n"
                f"---------------------------------------------\n\n"
                f"<b>Город:</b> {city}\n\n"
                f"<b>Заказчик:</b> {customer_name}\n"
                f"<b>Телефон:</b> {customer_phone}\n\n"
                f"⦿ <b>Адрес 1:</b> <a href='{pickup_point}'>{starting_point_a}</a>\n"
                f"⦿ <b>Адрес 2:</b> <a href='{delivery_point}'>{destination_point_b}</a>\n\n"
                f"<b>Доставляем:</b> {delivery_object if delivery_object else '...'}\n"
                f"<b>Расстояние:</b> {distance} км\n"
                f"<b>Стоимость доставки:</b> {price}₽\n\n"
                f"<b>Описание:</b> {description if description else '...'}\n\n"
                f"---------------------------------------------\n"
                f"• Проверьте ваш заказ и если все верно, то разместите.\n"
                f"• Курьер может связаться с вами для уточнения деталей!\n"
                f"• Оплачивайте курьеру наличными или переводом.\n\n"
                f"⦿⌁⦿ <a href='{yandex_maps_url}'>Маршрут доставки</a>\n\n"
            )
            new_message = await message.answer(
                text=order_forma,
                reply_markup=reply_kb,
                disable_notification=True,
                parse_mode="HTML",
            )

        else:
            new_message = await message.answer(
                text=f"Не удалось получить координаты для заказа. Проверьте заказ и попробуйте снова.",
                reply_markup=reply_kb,
                disable_notification=True,
            )
    elif len(addresses) == 3:
        pickup_address, delivery_address_1, delivery_address_2 = addresses
        pickup_coords = await route.get_coordinates(pickup_address)
        delivery_coords_1 = await route.get_coordinates(delivery_address_1)
        delivery_coords_2 = await route.get_coordinates(delivery_address_2)
        all_coordinates = [pickup_coords, delivery_coords_1, delivery_coords_2]

        if all(pickup_coords) and all(delivery_coords_1) and (delivery_coords_2):

            # Формирование координат
            yandex_maps_url, pickup_point, delivery_point_1, delivery_point_2 = (
                await route.get_rout(
                    pickup_coords, [delivery_coords_1, delivery_coords_2]
                )
            )

            distance, duration = await route.calculate_total_distance(all_coordinates)
            distance = round(distance, 2)
            price = await route.get_price(distance, moscow_time, over_price=70)

            # Структурирование данных заказа
            structured_data = await process_order_text(recognized_text)
            city = structured_data.get("City")

            if not city:
                city = user_city

            starting_point_a = structured_data.get("Starting point A")
            destination_point_b = structured_data.get("Destination point B")
            destination_point_c = structured_data.get("Destination point C")
            delivery_object = structured_data.get("Delivery object")
            description = structured_data.get("Description", None)

            # Сохранение данных в состоянии
            await state.update_data(
                city=city,
                starting_point_a=starting_point_a,
                a_latitude=float(pickup_coords[0]),
                a_longitude=float(pickup_coords[1]),
                a_coordinates=pickup_coords,
                a_url=pickup_point,
                destination_point_b=destination_point_b,
                b_latitude=float(delivery_coords_1[0]),
                b_longitude=float(delivery_coords_1[1]),
                b_coordinates=delivery_coords_1,
                b_url=delivery_point_1,
                destination_point_c=destination_point_c,
                c_latitude=float(delivery_coords_2[0]),
                c_longitude=float(delivery_coords_2[1]),
                c_coordinates=delivery_coords_2,
                c_url=delivery_point_2,
                delivery_object=delivery_object,
                customer_name=customer_name,
                customer_phone=customer_phone,
                distance_km=distance,
                duration_min=duration,
                price_rub=price,
                order_text=recognized_text,
                order_time=moscow_time,
                yandex_maps_url=yandex_maps_url,
                pickup_point=pickup_point,
                delivery_point=delivery_point_1,
            )

            # Отправка ответа пользователю
            order_forma = (
                f"<b>Ваш заказ</b> ✍︎\n"
                f"---------------------------------------------\n\n"
                f"<b>Город:</b> {city}\n\n"
                f"<b>Заказчик:</b> {customer_name}\n"
                f"<b>Телефон:</b> {customer_phone}\n\n"
                f"⦿ <b>Адрес 1:</b> <a href='{pickup_point}'>{starting_point_a}</a>\n"
                f"⦿ <b>Адрес 2:</b> <a href='{delivery_point_1}'>{destination_point_b}</a>\n"
                f"⦿ <b>Адрес 3:</b> <a href='{delivery_point_2}'>{destination_point_c}</a>\n\n"
                f"<b>Доставляем:</b> {delivery_object if delivery_object else '...'}\n"
                f"<b>Расстояние:</b> {distance} км\n"
                f"<b>Стоимость доставки:</b> {price}₽\n\n"
                f"<b>Описание:</b> {description if description else '...'}\n\n"
                f"---------------------------------------------\n"
                f"• Проверьте ваш заказ и если все верно, то разместите.\n"
                f"• Курьер может связаться с вами для уточнения деталей!\n"
                f"• Оплачивайте курьеру наличными или переводом.\n\n"
                f"⦿⌁⦿ <a href='{yandex_maps_url}'>Маршрут доставки</a>\n\n"
            )
            new_message = await message.answer(
                text=order_forma,
                reply_markup=reply_kb,
                disable_notification=True,
                parse_mode="HTML",
            )
    elif len(addresses) == 4:
        pickup_address, delivery_address_1, delivery_address_2, delivery_address_3 = (
            addresses
        )
        pickup_coords = await route.get_coordinates(pickup_address)
        delivery_coords_1 = await route.get_coordinates(delivery_address_1)
        delivery_coords_2 = await route.get_coordinates(delivery_address_2)
        delivery_coords_3 = await route.get_coordinates(delivery_address_3)
        all_coordinates = [
            pickup_coords,
            delivery_coords_1,
            delivery_coords_2,
            delivery_coords_3,
        ]

        if (
            all(pickup_coords)
            and all(delivery_coords_1)
            and all(delivery_coords_2)
            and all(delivery_coords_3)
        ):

            # Формирование координат
            (
                yandex_maps_url,
                pickup_point,
                delivery_point_1,
                delivery_point_2,
                delivery_point_3,
            ) = await route.get_rout(
                pickup_coords, [delivery_coords_1, delivery_coords_2, delivery_coords_3]
            )

            # Рассчет дистанции и продолжительности
            distance, duration = await route.calculate_total_distance(all_coordinates)
            distance = round(distance, 2)
            price = await route.get_price(distance, moscow_time, over_price=90)

            # Структурирование данных заказа
            structured_data = await process_order_text(recognized_text)
            city = structured_data.get("City")

            if not city:
                city = user_city

            starting_point_a = structured_data.get("Starting point A")
            destination_point_b = structured_data.get("Destination point B")
            destination_point_c = structured_data.get("Destination point C")
            destination_point_d = structured_data.get("Destination point D")
            delivery_object = structured_data.get("Delivery object")
            description = structured_data.get("Description", None)

            # Сохранение данных в состоянии
            await state.update_data(
                city=city,
                starting_point_a=starting_point_a,
                a_latitude=float(pickup_coords[0]),
                a_longitude=float(pickup_coords[1]),
                a_coordinates=pickup_coords,
                a_url=pickup_point,
                destination_point_b=destination_point_b,
                b_latitude=float(delivery_coords_1[0]),
                b_longitude=float(delivery_coords_1[1]),
                b_coordinates=delivery_coords_1,
                b_url=delivery_point_1,
                destination_point_c=destination_point_c,
                c_latitude=float(delivery_coords_2[0]),
                c_longitude=float(delivery_coords_2[1]),
                c_coordinates=delivery_coords_2,
                c_url=delivery_point_2,
                destination_point_d=destination_point_d,
                d_latitude=float(delivery_coords_3[0]),
                d_longitude=float(delivery_coords_3[1]),
                d_coordinates=delivery_coords_3,
                d_url=delivery_point_3,
                delivery_object=delivery_object,
                customer_name=customer_name,
                customer_phone=customer_phone,
                distance_km=distance,
                duration_min=duration,
                price_rub=price,
                order_text=recognized_text,
                order_time=moscow_time,
                yandex_maps_url=yandex_maps_url,
                pickup_point=pickup_point,
                delivery_point=delivery_point_1,
            )

            # Формирование ответа пользователю
            order_forma = (
                f"<b>Ваш заказ</b> ✍︎\n"
                f"---------------------------------------------\n\n"
                f"<b>Город:</b> {city}\n\n"
                f"<b>Заказчик:</b> {customer_name}\n"
                f"<b>Телефон:</b> {customer_phone}\n\n"
                f"⦿ <b>Адрес 1:</b> <a href='{pickup_point}'>{starting_point_a}</a>\n"
                f"⦿ <b>Адрес 2:</b> <a href='{delivery_point_1}'>{destination_point_b}</a>\n"
                f"⦿ <b>Адрес 3:</b> <a href='{delivery_point_2}'>{destination_point_c}</a>\n"
                f"⦿ <b>Адрес 4:</b> <a href='{delivery_point_3}'>{destination_point_d}</a>\n\n"
                f"<b>Доставляем:</b> {delivery_object if delivery_object else '...'}\n"
                f"<b>Расстояние:</b> {distance} км\n"
                f"<b>Стоимость доставки:</b> {price}₽\n\n"
                f"<b>Описание:</b> {description if description else '...'}\n\n"
                f"---------------------------------------------\n"
                f"• Проверьте ваш заказ и если все верно, то разместите.\n"
                f"• Курьер может связаться с вами для уточнения деталей!\n"
                f"• Оплачивайте курьеру наличными или переводом.\n\n"
                f"⦿⌁⦿ <a href='{yandex_maps_url}'>Маршрут доставки</a>\n\n"
            )
            new_message = await message.answer(
                text=order_forma,
                reply_markup=reply_kb,
                disable_notification=True,
                parse_mode="HTML",
            )
    elif len(addresses) == 5:
        (
            pickup_address,
            delivery_address_1,
            delivery_address_2,
            delivery_address_3,
            delivery_address_4,
        ) = addresses

        pickup_coords = await route.get_coordinates(pickup_address)
        delivery_coords_1 = await route.get_coordinates(delivery_address_1)
        delivery_coords_2 = await route.get_coordinates(delivery_address_2)
        delivery_coords_3 = await route.get_coordinates(delivery_address_3)
        delivery_coords_4 = await route.get_coordinates(delivery_address_4)

        all_coordinates = [
            pickup_coords,
            delivery_coords_1,
            delivery_coords_2,
            delivery_coords_3,
            delivery_coords_4,
        ]

        if (
            all(pickup_coords)
            and all(delivery_coords_1)
            and all(delivery_coords_2)
            and all(delivery_coords_3)
            and all(delivery_coords_4)
        ):
            # Формирование координат
            (
                yandex_maps_url,
                pickup_point,
                delivery_point_1,
                delivery_point_2,
                delivery_point_3,
                delivery_point_4,
            ) = await route.get_rout(
                pickup_coords,
                [
                    delivery_coords_1,
                    delivery_coords_2,
                    delivery_coords_3,
                    delivery_coords_4,
                ],
            )
            # Рассчет дистанции и продолжительности
            distance, duration = await route.calculate_total_distance(all_coordinates)
            distance = round(distance, 2)
            price = await route.get_price(distance, moscow_time, over_price=120)

            # Структурирование данных заказа
            structured_data = await process_order_text(recognized_text)
            city = structured_data.get("City")

            if not city:
                city = user_city

            starting_point_a = structured_data.get("Starting point A")
            destination_point_b = structured_data.get("Destination point B")
            destination_point_c = structured_data.get("Destination point C")
            destination_point_d = structured_data.get("Destination point D")
            destination_point_e = structured_data.get("Destination point E")
            delivery_object = structured_data.get("Delivery object")
            description = structured_data.get("Description", None)

            # Сохранение данных в состоянии
            await state.update_data(
                city=city,
                starting_point_a=starting_point_a,
                a_latitude=float(pickup_coords[0]),
                a_longitude=float(pickup_coords[1]),
                a_coordinates=pickup_coords,
                a_url=pickup_point,
                destination_point_b=destination_point_b,
                b_latitude=float(delivery_coords_1[0]),
                b_longitude=float(delivery_coords_1[1]),
                b_coordinates=delivery_coords_1,
                b_url=delivery_point_1,
                destination_point_c=destination_point_c,
                c_latitude=float(delivery_coords_2[0]),
                c_longitude=float(delivery_coords_2[1]),
                c_coordinates=delivery_coords_2,
                c_url=delivery_point_2,
                destination_point_d=destination_point_d,
                d_latitude=float(delivery_coords_3[0]),
                d_longitude=float(delivery_coords_3[1]),
                d_coordinates=delivery_coords_3,
                d_url=delivery_point_3,
                destination_point_e=destination_point_e,
                e_latitude=float(delivery_coords_4[0]),
                e_longitude=float(delivery_coords_4[1]),
                e_coordinates=delivery_coords_4,
                e_url=delivery_point_4,
                delivery_object=delivery_object,
                customer_name=customer_name,
                customer_phone=customer_phone,
                distance_km=distance,
                duration_min=duration,
                price_rub=price,
                order_text=recognized_text,
                order_time=moscow_time,
                yandex_maps_url=yandex_maps_url,
                pickup_point=pickup_point,
                delivery_point=delivery_point_1,
            )

            # Формирование ответа пользователю
            order_forma = (
                f"<b>Ваш заказ</b> ✍︎\n"
                f"---------------------------------------------\n\n"
                f"<b>Город:</b> {city}\n\n"
                f"<b>Заказчик:</b> {customer_name}\n"
                f"<b>Телефон:</b> {customer_phone}\n\n"
                f"⦿ <b>Адрес 1:</b> <a href='{pickup_point}'>{starting_point_a}</a>\n"
                f"⦿ <b>Адрес 2:</b> <a href='{delivery_point_1}'>{destination_point_b}</a>\n"
                f"⦿ <b>Адрес 3:</b> <a href='{delivery_point_2}'>{destination_point_c}</a>\n"
                f"⦿ <b>Адрес 4:</b> <a href='{delivery_point_3}'>{destination_point_d}</a>\n"
                f"⦿ <b>Адрес 5:</b> <a href='{delivery_point_4}'>{destination_point_e}</a>\n\n"
                f"<b>Доставляем:</b> {delivery_object if delivery_object else '...'}\n"
                f"<b>Расстояние:</b> {distance} км\n"
                f"<b>Стоимость доставки:</b> {price}₽\n\n"
                f"<b>Описание:</b> {description if description else '...'}\n\n"
                f"---------------------------------------------\n"
                f"• Проверьте ваш заказ и если все верно, то разместите.\n"
                f"• Курьер может связаться с вами для уточнения деталей!\n"
                f"• Оплачивайте курьеру наличными или переводом.\n\n"
                f"⦿⌁⦿ <a href='{yandex_maps_url}'>Маршрут доставки</a>\n\n"
            )

            new_message = await message.answer(
                text=order_forma,
                reply_markup=reply_kb,
                disable_notification=True,
                parse_mode="HTML",
            )
    elif len(addresses) > 5:
        new_message = await message.answer(
            text=f"<b>Слишком много пунктов</b> 𐒀 \n\nМы не оформляем доставки с более чем 5 адресами, "
            "так как курьер может запутаться и не выполнить ваш заказ!",
            reply_markup=rerecord_kb,
            disable_notification=True,
            parse_mode="HTML",
        )
    else:
        new_message = await message.answer(
            text="Мы не смогли определить ваш заказ.\n Попробуйте переформулировать заказ более четко и повторить попытку.",
            reply_markup=rerecord_kb,
            disable_notification=True,
        )

    # Завершение обработки
    await wait_message.delete()
    await handler.handle_new_message(new_message, message)


# send_Order
@customer_r.callback_query(F.data == "order_sent")
async def set_order_to_db(callback_query: CallbackQuery, state: FSMContext):
    # Устанавливаем состояние
    # await state.set_state(CustomerState.default)

    # Создаем обработчик сообщений
    handler = MessageHandler(state, callback_query.bot)

    # Получаем ID пользователя
    tg_id = callback_query.from_user.id
    data = await state.get_data()
    await state.set_state(CustomerState.default)

    try:
        # Асинхронно создаем заказ
        order_number = await order_data.create_order(tg_id, data)
        text = (
            f"Заказ <b>№{order_number}</b> успешно создан! 🎉\n"
            f"Мы ищем курьера для вашего заказа 🔎\n\n"
            f"<i>*Информацию о заказах можно посмотреть в разделе</i> <b>Мои заказы</b>.\n\n"
            f"▼ <b>Выберите действие ...</b>"
        )
    except Exception as e:
        # Обработка возможных ошибок
        print(f"Ошибка при создании заказа: {str(e)}")

        text = "Ошибка при создании заказа.\n" "Попробуйте повторить заказ."

    new_message = await callback_query.message.answer(
        text, disable_notification=True, parse_mode="HTML"
    )

    # Обрабатываем новое сообщение
    await handler.handle_new_message(new_message, callback_query.message)


# ---------------------------------------------✺ The end (u_rout) ✺ ------------------------------------------------- #


# fallback
@customer_fallback.message()
async def handle_unrecognized_message(message: Message):
    log.info(message.text)
    await message.delete()
