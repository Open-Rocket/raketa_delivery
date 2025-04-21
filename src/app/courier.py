from ._deps import (
    CommandStart,
    TelegramBadRequest,
    FSMContext,
    ContentType,
    ReplyKeyboardRemove,
    filters,
    Message,
    CallbackQuery,
    OrderStatus,
    CourierState,
    PreCheckoutQuery,
    LabeledPrice,
    zlib,
    Time,
    json,
    courier_bot,
    courier_bot_id,
    handler,
    courier_r,
    courier_fallback,
    courier_data,
    customer_data,
    payment_r,
    kb,
    title,
    courier_bot_id,
    order_data,
    partner_data,
    partner_bot,
    admin_data,
    rediska,
    cities,
    payment_provider,
    customer_bot,
    log,
    F,
    find_closest_city,
    send_notification_to_couriers,
    ceil,
)


# ---
# ---


@courier_r.message(
    CommandStart(),
)
async def cmd_start_courier(
    message: Message,
    state: FSMContext,
):
    """Обрабатывает команду /start для курьера."""

    tg_id = message.from_user.id
    is_reg = await rediska.is_reg(courier_bot_id, tg_id)
    new_message = None

    if is_reg:
        current_state = CourierState.default.state
        await message.answer(
            text=f"▼ <b>Выберите действие в • ≡ Меню •</b>",
            disable_notification=True,
            parse_mode="HTML",
        )

    else:
        subscription_price = await admin_data.get_subscription_price()
        current_state = CourierState.reg_state.state
        photo_title = await title.get_title_courier("/start")
        text = (
            "Добро пожаловать в сервис доставки <b>Raketa!</b>\n\n"
            "◉ <b>Наши условия:</b>\n"
            "<b>Ты оплачиваешь только подписку и получаешь 100% прибыли с каждого выполненного заказа.</b>\n\n"
            f"<b>Подписка {subscription_price // 100}₽ в месяц!</b>\n\n"
            "Присоединяйся и начинай зарабатывать больше уже сегодня!"
        )
        reply_kb = await kb.get_courier_kb("/start")
        new_message = await message.answer_photo(
            photo=photo_title,
            caption=text,
            reply_markup=reply_kb,
            disable_notification=True,
            parse_mode="HTML",
        )

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)

    if new_message:
        await handler.catch(
            bot=courier_bot,
            chat_id=message.chat.id,
            user_id=tg_id,
            new_message=new_message,
            current_message=message,
            delete_previous=True,
        )


@courier_r.callback_query(
    F.data == "reg",
)
async def data_reg_courier(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обрабатывает запрос на регистрацию курьера."""

    await callback_query.answer("✍️ Регистрация", show_alert=False)

    current_state = CourierState.reg_Name.state
    tg_id = callback_query.from_user.id
    text = (
        f"Пройдите небольшую регистрацию.\n"
        f"Это не займет много времени.\n\n"
        f"<b>Как вас зовут?</b>\n\n"
    )

    new_message = await callback_query.message.answer(
        text=text,
        disable_notification=True,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)

    await handler.catch(
        bot=courier_bot,
        chat_id=callback_query.message.chat.id,
        user_id=tg_id,
        new_message=new_message,
        current_message=None,
        delete_previous=True,
    )


@courier_r.message(
    filters.StateFilter(CourierState.reg_Name),
)
async def data_name_courier(
    message: Message,
    state: FSMContext,
):
    """Обрабатывает имя курьера. CourierState.reg_Name"""

    current_state = CourierState.reg_Phone.state
    tg_id = message.from_user.id
    courier_name = message.text

    reply_kb = await kb.get_courier_kb("phone_number")
    text = (
        f"Привет, {courier_name}!👋\n\nЧтобы начать работу, пожалуйста, укажите ваш номер телефона для связи.\n\n"
        f"<i>*При регистрации с компьютера нажмите на значок команд рядом с полем ввода.</i>\n\n"
        f"<i>*Отправка номера возможно только по клику на кнопку 'Поделится номером'!</i>\n\n"
        f"<b>Ваш номер:</b>"
    )

    new_message = await message.answer(
        text=text,
        reply_markup=reply_kb,
        disable_notification=True,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)
    await rediska.set_name(courier_bot_id, tg_id, courier_name)

    await handler.catch(
        bot=courier_bot,
        chat_id=message.chat.id,
        user_id=tg_id,
        new_message=new_message,
        current_message=message,
        delete_previous=True,
    )


@courier_r.message(
    filters.StateFilter(CourierState.reg_Phone),
)
async def data_phone_courier(
    message: Message,
    state: FSMContext,
):
    """Обрабатывает номер телефона курьера. CourierState.reg_Phone"""

    current_state = CourierState.reg_City.state
    tg_id = message.from_user.id
    courier_phone = message.contact.phone_number

    text = (
        f"Последний шаг!\n\n"
        f"Чтобы сделать заказы максимально удобными, пожалуйста, введите город, где вы будете работать.\n\n"
        f"<i>Доступны только города РФ.</i>\n\n"
        f"<b>Ваш город:</b>"
    )

    new_message = await message.answer(
        text=text,
        disable_notification=True,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)
    await rediska.set_phone(courier_bot_id, tg_id, courier_phone)

    await handler.catch(
        bot=courier_bot,
        chat_id=message.chat.id,
        user_id=tg_id,
        new_message=new_message,
        current_message=message,
        delete_previous=True,
    )


@courier_r.message(
    filters.StateFilter(CourierState.reg_City),
)
async def data_city_courier(
    message: Message,
    state: FSMContext,
):
    """Обрабатывает город курьера. CourierState.reg_City"""

    tg_id = message.from_user.id
    russian_cities = await cities.get_cities()
    city, _ = await find_closest_city(message.text, russian_cities)

    if not city:
        await message.answer(
            text=f"Введите корректное название города!\n\n<b>Ваш город:</b>",
            disable_notification=True,
            parse_mode="HTML",
        )

    else:
        current_state = CourierState.reg_tou.state
        reply_kb = await kb.get_courier_kb("accept_tou")
        text = (
            f"Начиная использование сервиса, вы соглашаетесь с "
            f"<a href='https://drive.google.com/file/d/16NYgi7_7GL830A4xwaeHBYsYKyduOiSS/view?usp=drive_link'>"
            f"Пользовательским соглашением и правилами использования</a>, а также "
            f"<a href='https://telegram.org/privacy'>Политикой конфиденциальности</a>.\n\n"
            f"<i>*Обращаем внимание, что любые действия, связанные с заказами, "
            f"отправкой или получением посылок, должны соответствовать законодательству "
            f"вашего государства и общепринятым этическим нормам.</i>\n\n"
        )

        new_message = await message.answer(
            text,
            reply_markup=reply_kb,
            disable_notification=True,
            disable_web_page_preview=True,
            parse_mode="HTML",
        )

        await state.set_state(current_state)
        await rediska.set_state(courier_bot_id, tg_id, current_state)
        await rediska.set_city(courier_bot_id, tg_id, city)

    await handler.catch(
        bot=courier_bot,
        chat_id=message.chat.id,
        user_id=tg_id,
        new_message=new_message,
        current_message=message,
        delete_previous=True,
    )


@courier_r.callback_query(
    F.data == "accept_tou",
)
async def courier_accept_tou(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обрабатывает принятие пользовательского соглашения. CourierState.reg_tou"""

    tg_id = callback_query.from_user.id
    accept_tou = (
        "Пользовательское соглашение и правила использования сервиса - Принимаю"
    )

    courier_name, courier_phone, courier_city = await rediska.get_user_info(
        courier_bot_id, tg_id
    )
    is_set_reg = await rediska.set_reg(
        courier_bot_id,
        tg_id,
        True,
    )
    is_set_courier_to_db = await courier_data.set_courier(
        tg_id,
        courier_name,
        courier_phone,
        courier_city,
        accept_tou,
    )

    if is_set_reg and is_set_courier_to_db:

        await callback_query.answer("✅ Принято", show_alert=False)

        current_state = CourierState.default.state

        moscow_time = await Time.get_moscow_time()
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
            subscription_status = (
                f"<b>Подписка:</b> Не активна\n\n"
                f"<i>Введите PROMOKOD для активации бесплатного периода</i> /promo\n\n"
            )

        text = (
            f"Вы успешно зарегистрировались! 🎉\n\n"
            f"Имя: {courier_name}\n"
            f"Номер: {courier_phone}\n"
            f"Город: {courier_city}\n"
            f"{subscription_status}"
            f"▼ <b>Выберите действие в • ≡ Меню •</b>"
        )

        new_message = await callback_query.message.answer(
            text=text,
            disable_notification=False,
            parse_mode="HTML",
        )

    else:

        current_state = CourierState.reg_tou.state
        reply_kb = await kb.get_courier_kb("accept_tou")
        tou_text = (
            f"Начиная использование сервиса, вы соглашаетесь с "
            f"<a href='https://disk.yandex.ru/i/d2S9C4zW4hmL0w'>"
            f"Пользовательским соглашением и правилами использования</a>, а также "
            f"<a href='https://telegram.org/privacy'>Политикой конфиденциальности</a>.\n\n"
            f"<i>*Обращаем внимание, что любые действия, связанные с заказами, "
            f"отправкой или получением посылок, должны соответствовать законодательству "
            f"вашего государства и общепринятым этическим нормам.</i>\n\n"
        )

        new_message = await callback_query.message.answer(
            text=(
                f"<b>‼️ Произошла ошибка при сохранении данных, попробуйте позже еще раз!</b>\n\n"
                f"{tou_text}"
            ),
            reply_markup=reply_kb,
            disable_notification=True,
            disable_web_page_preview=True,
            parse_mode="HTML",
        )

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)

    await handler.catch(
        bot=courier_bot,
        chat_id=callback_query.message.chat.id,
        user_id=tg_id,
        new_message=new_message,
        current_message=None,
        delete_previous=True,
    )


# ---
# ---


@courier_r.message(
    F.text == "/notify",
)
async def cmd_notify(
    message: Message,
    state: FSMContext,
):
    """Обработчик команды /notify"""

    current_state = CourierState.default.state
    tg_id = message.from_user.id

    notify_status = await courier_data.get_courier_notify_status(tg_id=tg_id)

    log.info(f"notify status: {notify_status}")

    text = (
        f"Уведомления: {'<b>ON🔔</b>' if notify_status else '<b>OFF🔕</b>'}\n\n"
        f"{'<i>*Вы будете получать уведомления о новых заказах и акциях.</i>' if notify_status else '<i>*Включите уведомления, чтобы получать информацию о новых заказах и акциях.</i>'}\n\n"
    )

    reply_kb = await kb.get_turn_status_kb(
        "notify",
        status_notify=not notify_status,
    )

    await message.answer(
        text=text,
        reply_markup=reply_kb,
        disable_notification=True,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)


@courier_r.callback_query(
    F.data == "turn_on_notify",
)
@courier_r.callback_query(
    F.data == "turn_off_notify",
)
async def data_turn_on_notify(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик 'turn_on_notify' и 'turn_off_notify' для курьера."""

    tg_id = callback_query.from_user.id
    notify_status = await courier_data.get_courier_notify_status(tg_id=tg_id)

    log.info(f"notify status: {notify_status}")

    notify_status = not notify_status
    await courier_data.set_courier_notify_status(
        tg_id=tg_id,
        status=notify_status,
    )

    text = (
        f"Уведомления: {'<b>ON🔔</b>' if notify_status else '<b>OFF🔕</b>'}\n\n"
        f"{'<i>*Вы будете получать уведомления о новых заказах и акциях.</i>' if notify_status else '<i>*Включите уведомления, чтобы получать информацию о новых заказах и акциях.</i>'}\n\n"
    )

    await callback_query.answer(
        "✅ Уведомления обновлены",
        show_alert=False,
    )
    await callback_query.message.answer(
        text=text,
        disable_notification=True,
        parse_mode="HTML",
    )

    await callback_query.message.delete()

    await state.set_state(CourierState.default.state)
    await rediska.set_state(courier_bot_id, tg_id, CourierState.default.state)


# ---


@courier_r.message(
    F.text == "/promo",
)
async def cmd_promo(
    message: Message,
    state: FSMContext,
):
    """Обработчик команды /promo для курьера."""

    current_state = CourierState.default.state
    tg_id = message.from_user.id

    courier_seed_key = await courier_data.get_courier_seed_key(tg_id)

    if courier_seed_key:
        text = (
            f"🎉 <b>PROMO</b>\n\n"
            f"Вы являетесь участником PROMO акций!\n\n"
            f"Ваш PROMOKOD: <code>{courier_seed_key}</code>"
        )

        await message.answer(
            text=text,
            disable_notification=True,
            parse_mode="HTML",
        )

    else:

        text = (
            f"🎉 <b>PROMOKOD</b>\n\n"
            f"Здесь вы можете ввести свой промокод, участвовать в акциях и получать скидки.\n\n"
        )

        reply_kb = await kb.get_courier_kb("promo")

        await message.answer(
            text=text,
            reply_markup=reply_kb,
            disable_notification=True,
            parse_mode="HTML",
        )

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)


@courier_r.callback_query(
    F.data == "PROMOKOD",
)
async def data_set_PROMO(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик коллбэка 'PROMOKOD' для курьера."""

    tg_id = callback_query.from_user.id
    await callback_query.answer("🎉 PROMOKOD", show_alert=False)

    is_set_key = await courier_data.is_set_key(tg_id)

    if is_set_key:
        current_state = CourierState.default.state
        text = f"Вы уже применили свой PROMOKOD!\n\n"
    else:
        current_state = CourierState.set_seed_key.state
        text = f"Ваш PROMOKOD:"

    await callback_query.message.answer(
        text=text,
        disable_notification=True,
        parse_mode="HTML",
    )

    await callback_query.message.delete()

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)


@courier_r.message(
    filters.StateFilter(CourierState.set_seed_key),
)
async def data_PROMO(
    message: Message,
    state: FSMContext,
):
    """Обработчик состояния 'CourierState.set_seed_key'."""

    current_state = CourierState.default.state
    tg_id = message.from_user.id
    seed_key = message.text.upper()

    is_set_key = await courier_data.set_courier_seed_key(tg_id, seed_key)

    log.info(f"is_set_key: {is_set_key}")

    free_period = await courier_data.get_free_period()

    if is_set_key:
        moscow_time = await Time.get_moscow_time()
        free_period = await courier_data.get_free_period()

        _ = await courier_data.update_courier_subscription(tg_id, days=free_period)

        _, _, _, end_date = await courier_data.get_courier_full_info(tg_id)

        (
            partner_tg_id,
            balance,
            is_blocked,
        ) = await admin_data.get_partner_full_info_by_SEED(seed=seed_key)

        if not is_blocked:
            await partner_bot.send_message(
                chat_id=partner_tg_id,
                text=f"Ваши ключем <b>{seed_key}</b> только что воспользовались!👍\nПродолжайте в том же духе!",
                disable_notification=True,
                parse_mode="HTML",
            )

        if end_date and end_date >= moscow_time:
            remaining_days = (end_date - moscow_time).days
            subscription_status = (
                f"<b>Подписка:</b> Активна 🚀\n"
                f"📅 Действует до: {end_date.strftime('%d.%m.%Y')}\n"
                f"🕒 Осталось дней: {remaining_days - 1}\n\n"
            )

        text = (
            f"✅ PROMOKOD успешно установлен!\n\n"
            f"Вам начислено <b>+{free_period}</b> бесплатных дней.\n\n"
            f"{subscription_status}"
        )
    else:
        text = "‼️ Ошибка при установке PROMOKOD-а\n\nВозможно такого промокода не существует!"

    await message.answer(
        text=text,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)


# ---
# ---


@courier_r.message(
    F.text == "/run",
)
@courier_r.callback_query(
    F.data == "lets_go",
)
async def cmd_run(
    event: Message | CallbackQuery,
    state: FSMContext,
):
    """Обрабатывает запрос на начало работы курьера. /run, lets_go"""

    if isinstance(event, CallbackQuery):

        await event.message.delete()
        await event.answer("🚀 Начать работу", show_alert=False)

    current_state = CourierState.default.state
    tg_id = event.from_user.id
    moscow_time = await Time.get_moscow_time()
    chat_id = event.chat.id if isinstance(event, Message) else event.message.chat.id
    is_read_info = await rediska.is_read_info(courier_bot_id, tg_id)
    _, _, _, end_date = await courier_data.get_courier_full_info(tg_id)

    log.info(f"end_date: {end_date}")

    is_block = await admin_data.get_courier_block_status(tg_id=tg_id)

    if is_block:
        await event.answer(
            text="🚫 <b>Вы были заблокированы и не можете больше принимать новые заказы!</b>",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="HTML",
        )
        return

    if end_date and end_date >= moscow_time:
        if is_read_info:
            if isinstance(event, CallbackQuery):
                await event.answer("🚀 Начать работу", show_alert=False)

            current_state = CourierState.location.state
            current_active_orders_count = (
                await courier_data.get_courier_active_orders_count(tg_id)
            )
            max_orders_count = await admin_data.get_courier_max_active_orders_count()

            reply_kb = await kb.get_courier_kb("/run")

            if current_active_orders_count < max_orders_count:
                text = (
                    f"Пожалуйста, отправьте вашу текущую локацию, чтобы мы могли назначить вам ближайшие заказы.\n\n"
                    f"<i>*Доступно только с мобильных устройств</i>\n\n"
                )

                await event.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    reply_markup=reply_kb,
                    disable_notification=True,
                    parse_mode="HTML",
                )
            else:
                current_state = CourierState.default.state
                text = (
                    "Вы уже выполняете максимальное количество заказов.\n\n"
                    "Пожалуйста, завершите текущие заказы, чтобы начать новые."
                )

                await event.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    disable_notification=True,
                    parse_mode="HTML",
                )
        else:
            current_state = CourierState.default.state

            ttl = await title.get_title_courier("first_run")

            text = (
                f"⚠️ Важно:\n\n"
                f"- Частые нарушения правил могут привести к бану аккаунта.\n\n"
                f"- За кражу заказа или мошенничество блокировка и уголовное наказание.\n\n"
                f"🍀 Удачной работы!\n"
                f"💰 Все заработанные деньги ваши!\n\n"
            )

            reply_kb = await kb.get_courier_kb("run_first")

            new_message = await event.bot.send_photo(
                chat_id=chat_id,
                photo=ttl,
                caption=text,
                reply_markup=reply_kb,
                disable_notification=True,
                parse_mode="HTML",
            )

            await handler.catch(
                bot=courier_bot,
                chat_id=chat_id,
                user_id=tg_id,
                new_message=new_message,
                current_message=None,
                delete_previous=True,
            )
    else:
        reply_kb = await kb.get_courier_kb("pay_sub")
        text = (
            "‼️ Ваша подписка не активна, пожалуйста, оплатите подписку.\n\n"
            "<i>*Введите PROMOKOD если еще не использовали пробный период</i> /promo"
        )
        if isinstance(event, CallbackQuery):
            await event.message.answer(
                text=text,
                reply_markup=reply_kb,
                show_alert=True,
                parse_mode="HTML",
            )
        else:
            await event.answer(
                text=text,
                reply_markup=reply_kb,
                disable_notification=True,
                parse_mode="HTML",
            )

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)


@courier_r.callback_query(
    F.data == "lets_go_first",
)
async def data_lets_go_first(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик коллбэка 'lets_go_first' для курьера."""

    await callback_query.answer("🚀 Начать работу", show_alert=False)

    current_state = CourierState.location.state
    tg_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    current_active_orders_count = await courier_data.get_courier_active_orders_count(
        tg_id
    )
    max_orders_count = await admin_data.get_courier_max_active_orders_count()

    reply_kb = await kb.get_courier_kb("/run")

    if current_active_orders_count < max_orders_count:

        text = (
            "Пожалуйста, отправьте вашу текущую локацию, чтобы мы могли назначить вам ближайшие заказы.\n\n"
            "<i>*Доступно только с мобильных устройств</i>"
        )

        await callback_query.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_kb,
            disable_notification=True,
            parse_mode="HTML",
        )
    else:

        current_state = CourierState.default.state

        text = (
            "Вы уже выполняете максимальное количество заказов.\n\n"
            "Пожалуйста, завершите текущие заказы, чтобы начать новые."
        )

        await callback_query.message.answer(
            text=text,
            disable_notification=True,
            parse_mode="HTML",
        )

    await callback_query.message.delete()

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)
    await rediska.set_read_info(courier_bot_id, tg_id, True)


@courier_r.message(
    F.content_type == ContentType.LOCATION,
    filters.StateFilter(CourierState.location),
)
@courier_r.callback_query(
    F.data == "back_location",
)
@courier_r.callback_query(
    F.data == "refresh_orders",
)
async def get_location(
    event: Message | CallbackQuery,
    state: FSMContext,
):
    """Обрабатывает получение локации курьера. CourierState.location"""

    current_state = CourierState.default.state

    tg_id = event.from_user.id
    courier_tg_id = event.from_user.id
    courier_city = await courier_data.get_courier_city(courier_tg_id)
    radius_km = await admin_data.get_distance_radius()

    if isinstance(event, CallbackQuery):

        if event.data == "refresh_orders" or event.data == "back_location":
            my_lat, my_lon = await courier_data.get_courier_last_location(courier_tg_id)

    else:
        my_lat = event.location.latitude
        my_lon = event.location.longitude

        _ = await courier_data.update_courier_location(
            tg_id,
            my_lat,
            my_lon,
        )

    nearby_orders = await order_data.get_nearby_orders(my_lat, my_lon, radius_km)
    city_orders = await order_data.get_pending_orders_in_city(courier_city)

    total_sum_nearby = sum(order["price_rub"] for order in nearby_orders.values())
    total_sum_city = sum(order["price_rub"] for order in city_orders.values())

    text = (
        f"<b>📋 Заказы</b>\n\n"
        f"Заказов в городе <b>{courier_city}</b>: <b>{len(city_orders)}</b>\n"
        f"Заказов рядом с вами: <b>{len(nearby_orders)}</b>\n\n"
        f"{courier_city}: <b>{total_sum_city}₽</b>\n"
        f"Рядом: <b>{total_sum_nearby}₽</b>\n\n"
        f"🔍 Хотите посмотреть заказы рядом?"
    )

    reply_kb = await kb.get_courier_orders_full_kb(
        city_orders_len=len(city_orders),
        available_orders_len=len(nearby_orders),
    )

    # Сохраняем данные состояния для сравнения
    state_data = await state.get_data()
    saved_text = state_data.get("message_text_orders")
    saved_kb = state_data.get("message_kb_orders")

    new_kb_json = json.dumps(reply_kb.model_dump())

    if isinstance(event, CallbackQuery):
        if event.data == "back_location":
            await event.answer(
                text="↩️ Назад",
                show_alert=False,
            )

            # Обновляем сообщение с заказами
            await event.message.edit_text(
                text=text,
                reply_markup=reply_kb,
                disable_notification=True,
                parse_mode="HTML",
            )

        if (
            event.data == "refresh_orders"
            or saved_text != text
            or saved_kb != new_kb_json
        ):
            await event.answer(
                text="🔄 Обновление данных...",
                show_alert=False,
            )

            # Проверяем, что контент действительно изменился, прежде чем обновлять сообщение
            if saved_text != text or saved_kb != new_kb_json:
                await event.message.edit_text(
                    text=text,
                    reply_markup=reply_kb,
                    disable_notification=True,
                    parse_mode="HTML",
                )

    else:
        if event.location.live_period:
            await event.answer(
                text=(
                    "Локация не принята!\n"
                    "Пожалуйста, отправьте статичную локацию!\n\n"
                    "<i>*Доступно только с мобильных устройств</i>"
                ),
                reply_markup=ReplyKeyboardRemove(),
                disable_notification=True,
            )
            await event.delete()
            return

        await event.answer(
            text="Локация принята!",
            reply_markup=ReplyKeyboardRemove(),
            disable_notification=True,
        )

        await event.answer(
            text=text,
            reply_markup=reply_kb,
            disable_notification=True,
            parse_mode="HTML",
        )

    await state.set_state(current_state)
    await state.update_data(
        message_text_orders=text,
        message_kb_orders=new_kb_json,
        order_data={
            "nearby_orders": nearby_orders,
            "city_orders": city_orders,
        },
    )
    await rediska.set_state(courier_bot_id, tg_id, current_state)
    await rediska.save_fsm_state(state, courier_bot_id, courier_tg_id)


# ---


@courier_r.callback_query(
    F.data == "show_nearby_orders",
)
async def show_nearby_orders(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обрабатывает запрос на просмотр заказов в радиусе курьера. show_nearby_orders"""

    current_state = CourierState.nearby_Orders.state

    data = await state.get_data()
    order_data: dict = data.get("order_data", {})
    nearby_orders = order_data.get("nearby_orders", {})

    tg_id = callback_query.from_user.id
    bot_id = callback_query.bot.id

    if not nearby_orders or not isinstance(nearby_orders, dict):

        await callback_query.answer(
            "Нет доступных заказов в вашем радиусе.",
            show_alert=True,
        )

    else:
        len_nearby_orders = len(nearby_orders)
        nearby_orders_data = {}
        order_ids = list(nearby_orders.keys())
        for index, order_id in enumerate(order_ids, start=1):
            order_forma = nearby_orders[order_id]["text"]
            order_text = (
                f"<b>{index}/{len_nearby_orders}</b>\n"
                f"<b>Заказ: №{order_id}</b>\n"
                f"---------------------------------------------\n\n"
                f"{order_forma}"
            )
            nearby_orders_data[order_id] = {"text": order_text, "index": index}

        first_order_id = order_ids[0]
        reply_markup = await kb.get_courier_kb(
            "one_order" if len(order_ids) == 1 else "available_orders"
        )

        await callback_query.answer(
            f"📍 Заказы рядом {len_nearby_orders}", show_alert=False
        )

        await callback_query.message.edit_text(
            nearby_orders_data[first_order_id]["text"],
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            parse_mode="HTML",
        )

        await state.set_state(current_state)
        await state.update_data(
            nearby_orders_data=nearby_orders_data,
            order_ids=order_ids,
            current_index=0,
            current_order_id=order_ids[0],
        )
        await rediska.save_fsm_state(state, bot_id, tg_id)


@courier_r.callback_query(
    F.data == "show_city_orders",
)
async def show_city_orders(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обрабатывает запрос на просмотр всех заказов в городе. show_city_orders"""

    current_state = CourierState.city_Orders.state

    data = await state.get_data()
    order_data: dict = data.get("order_data", {})
    city_orders = order_data.get("city_orders", {})

    tg_id = callback_query.from_user.id
    bot_id = callback_query.bot.id

    if not city_orders or not isinstance(city_orders, dict):
        await callback_query.answer(
            "Нет доступных заказов в вашем городе.",
            show_alert=True,
        )
        return

    len_city_orders = len(city_orders)
    orders_data = {}
    order_ids = list(city_orders.keys())

    for index, order_id in enumerate(order_ids, start=1):
        order_forma = city_orders[order_id]["text"]
        order_text = (
            f"<b>{index}/{len_city_orders}</b>\n"
            f"<b>Заказ: №{order_id}</b>\n"
            f"---------------------------------------------\n\n"
            f"{order_forma}"
        )
        orders_data[order_id] = {"text": order_text, "index": index}

    first_order_id = order_ids[0]
    reply_markup = await kb.get_courier_kb(
        "one_order" if len(order_ids) == 1 else "available_orders"
    )

    await callback_query.answer(
        f"🏙️ Заказы в городе: {len_city_orders}", show_alert=False
    )

    await callback_query.message.edit_text(
        orders_data[first_order_id]["text"],
        reply_markup=reply_markup,
        disable_web_page_preview=True,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await state.update_data(
        orders_data=orders_data,
        order_ids=order_ids,
        current_index=0,
        current_order_id=order_ids[0],
    )
    await rediska.save_fsm_state(state, bot_id, tg_id)


# ---


@courier_r.callback_query(
    filters.StateFilter(
        CourierState.city_Orders,
    ),
    F.data.in_({"next_right", "back_left"}),
)
async def handle_order_navigation_city(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обрабатывает навигацию по заказам курьера. next_right, back_left"""

    current_state = CourierState.city_Orders.state
    tg_id = callback_query.from_user.id

    data = await state.get_data()
    order_data: dict = data.get("order_data", {})
    city_orders_data: dict = order_data.get("city_orders", {})

    city_order_ids = list(city_orders_data.keys())
    current_index = data.get("current_index", 0)

    if not city_orders_data or not city_order_ids:
        log.warning(f"❌ Нет доступных заказов.")
        await callback_query.answer("Нет доступных заказов.", show_alert=True)
        return

    total_orders_city = len(city_order_ids)

    if callback_query.data == "next_right":
        new_index = (current_index + 1) % total_orders_city
        await callback_query.answer(
            f"{new_index+1}/{total_orders_city} ⏩", show_alert=False
        )

    else:
        new_index = (current_index - 1) % total_orders_city
        await callback_query.answer(
            f"⏪ {new_index+1}/{total_orders_city}", show_alert=False
        )

    new_order_id = city_order_ids[new_index]

    reply_markup = await kb.get_courier_kb(
        "available_orders" if total_orders_city > 1 else "one_order"
    )

    await callback_query.message.edit_text(
        city_orders_data[new_order_id]["text"],
        reply_markup=reply_markup,
        disable_web_page_preview=True,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await state.update_data(current_index=new_index, current_order_id=new_order_id)
    await rediska.set_state(courier_bot_id, tg_id, current_state)
    await rediska.save_fsm_state(state, courier_bot_id, tg_id)


# ---


@courier_r.callback_query(
    filters.StateFilter(
        CourierState.nearby_Orders,
    ),
    F.data.in_({"next_right", "back_left"}),
)
async def handle_order_navigation_nearby(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обрабатывает навигацию по заказам курьера. next_right, back_left"""

    current_state = CourierState.nearby_Orders.state
    tg_id = callback_query.from_user.id

    data = await state.get_data()
    order_data: dict = data.get("order_data", {})
    nearby_orders_data: dict = order_data.get("nearby_orders", {})

    nearby_order_ids = list(nearby_orders_data.keys())
    current_index = data.get("current_index", 0)

    if not nearby_orders_data or not nearby_order_ids:
        log.warning(f"❌ Нет доступных заказов.")
        await callback_query.answer("Нет доступных заказов.", show_alert=True)
        return

    total_orders_nearby = len(nearby_order_ids)

    if callback_query.data == "next_right":
        new_index = (current_index + 1) % total_orders_nearby
        await callback_query.answer(
            f"{new_index+1}/{total_orders_nearby} ⏩", show_alert=False
        )

    else:
        new_index = (current_index - 1) % total_orders_nearby
        await callback_query.answer(
            f"⏪ {new_index+1}/{total_orders_nearby}", show_alert=False
        )

    new_order_id = nearby_order_ids[new_index]

    reply_markup = await kb.get_courier_kb(
        "available_orders" if total_orders_nearby > 1 else "one_order"
    )

    await callback_query.message.edit_text(
        nearby_orders_data[new_order_id]["text"],
        reply_markup=reply_markup,
        disable_web_page_preview=True,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await state.update_data(current_index=new_index, current_order_id=new_order_id)
    await rediska.set_state(courier_bot_id, tg_id, current_state)
    await rediska.save_fsm_state(state, courier_bot_id, tg_id)


# ---
# ---


@courier_r.callback_query(
    F.data == "accept_order",
)
async def accept_order(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обрабатывает запрос на принятие заказа курьером. accept_order"""

    current_state = CourierState.default.state

    tg_id = callback_query.from_user.id
    data = await state.get_data()
    order_ids: list = data.get("order_ids", [])
    current_order_id = int(data.get("current_order_id"))
    courier_name, courier_phone, _ = await courier_data.get_courier_info(tg_id)

    customer_name, customer_phone, customer_tg_id = (
        await order_data.get_customer_info_by_order_id(current_order_id)
    )

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
                f"К сожалению, заказ №{current_order_id} уже был принят другим курьером.",
                parse_mode="HTML",
            )
            return

        await order_data.update_order_status_and_started_time(
            order_id=current_order_id,
            new_status=OrderStatus.IN_PROGRESS,
        )

        await customer_bot.send_message(
            chat_id=customer_tg_id,
            text=(
                f"<b>✅ Заказ №{current_order_id} принят!</b>\n\n"
                f"Курьер: {courier_name}\n"
                f"Телефон: {courier_phone}\n\n"
                f"<i>*Подробности в меню</i> <b>Мои заказы</b>\n\n"
                f"<i>*Запросите у курьера его транслируемую геопозицию для отслеживания местоположения вашего заказа!\n</i>"
            ),
            parse_mode="HTML",
        )

        order_ids.remove(current_order_id)

        text = (
            f"<b>✅ Заказ №{current_order_id} принят!</b>\n\n"
            f"Заказчик: {customer_name}\n"
            f"Телефон: {customer_phone}\n\n"
            f"<i>*Принимайте оплату наличными или переводом!</i>\n\n"
            f"<i>*Поделитесь пожалуйста с заказчиком транслируемой геопозицией на время выполнения заказа чтобы он мог видеть его текущее местоположение!</i>\n\n"
            f"<i>*Нажмите на знак 📎 -> Геопозиция -> Транслировать геопозицию.</i>\n\n"
            f"<i>*После завершения заказ перейдите в Меню -> Мои заказы -> Активные и нажмите на кнопку '✅ Доставил'</i>\n\n"
        )

        await callback_query.answer("✅ Заказ принят!", show_alert=False)

        await callback_query.message.answer(
            text=text,
            disable_web_page_preview=True,
            parse_mode="HTML",
        )

        await callback_query.message.delete()

        await state.set_state(current_state)
        await state.update_data(
            order_ids=order_ids,
            current_order_id=None if not order_ids else order_ids[0],
        )
        await rediska.set_state(courier_bot_id, tg_id, current_state)
        await rediska.save_fsm_state(state, courier_bot_id, tg_id)

        await courier_data.change_order_active_count(tg_id, count=1)

    except Exception as e:
        log.error(f"Ошибка при принятии заказа {current_order_id}: {e}")
        await callback_query.answer(
            "Ошибка при принятии заказа.",
            show_alert=True,
        )


# ---


@courier_r.callback_query(
    F.data == "order_delivered",
)
async def complete_order(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обрабатывает запрос на завершение заказа курьером. order_delivered"""

    data = await state.get_data()
    current_order_id = data.get("current_order_id")
    tg_id = callback_query.from_user.id

    current_state = CourierState.default.state

    if not current_order_id:
        await callback_query.message.answer(
            "Не удалось найти активный заказ для завершения."
        )
        return

    try:

        order = await order_data.get_order_by_id(current_order_id)

        current_time = await Time.get_moscow_time()

        execution_time_seconds = (
            current_time - order.started_at_moscow_time
        ).total_seconds()

        execution_time_hours_for_speed = execution_time_seconds / 3600
        execution_time_hours = int(execution_time_seconds // 3600)
        execution_time_minutes = int(execution_time_seconds % 3600 // 60)

        speed = order.distance_km / execution_time_hours_for_speed
        distance = order.distance_km
        earned = order.price_rub

        AVERAGE_SPEED_KMH = 8
        SPEED_MULTIPLIER = 10

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

            text = f"Заказ №{current_order_id} уже завершён или находится в другом статусе.\n\nСтатус: {'Завершен' if order.order_status == OrderStatus.COMPLETED else  'Отменен' if OrderStatus.CANCELLED else 'Не определен'}."

            await callback_query.message.answer(
                text=text,
                parse_mode="HTML",
            )
            return

        base_order_XP = await admin_data.get_base_order_XP()
        distance_XP = await admin_data.get_distance_XP()
        speed_XP = await admin_data.get_speed_XP()

        calculate_distance_XP = round((distance * distance_XP), 2)
        calculate_speed_XP = round((speed * speed_XP), 2)

        new_XP = round((base_order_XP + calculate_distance_XP + calculate_speed_XP), 2)

        await order_data.update_order_status_and_completed_time(
            order_id=current_order_id,
            courier_username=callback_query.from_user.username,
            new_status=OrderStatus.COMPLETED,
            speed_kmh=round(speed, 2),
            execution_time_seconds=execution_time_seconds,
        )
        customer_tg_id = await order_data.get_customer_tg_id(order.order_id)

        _ = await courier_data.update_courier_XP(
            tg_id=tg_id,
            new_XP=new_XP,
        )

        _ = await courier_data.update_courier_records(
            tg_id=tg_id,
            count=1,
            distance=distance,
            earned=earned,
        )

        await courier_data.change_order_active_count(
            tg_id,
            count=-1,
        )

        notification_text = (
            f"Ваш заказ <b>№{current_order_id}</b> был доставлен курьером!\n"
            f"Заказ был выполнен за <b>{execution_time_hours} ч {execution_time_minutes} мин</b>\n"
            f"Спасибо что выбрали наш сервис! 🚀"
        )
        await customer_bot.send_message(
            chat_id=customer_tg_id,
            text=notification_text,
            parse_mode="HTML",
        )

        text_1 = (
            f"<b>✅ Заказ №{current_order_id} доставлен</b>!\n\n"
            f"Вы заработали <b>{order.price_rub} руб</b>\n"
            f"Время доставки: <b>{execution_time_hours} ч {execution_time_minutes} мин</b>\n"
            f"Скорость доставки: <b>{speed:.2f} км/ч</b>\n\n"
            f"<b>Спасибо за вашу работу! 🚀</b>\n"
        )

        text_2 = (
            f"+ {base_order_XP} очков опыта за заказ\n"
            f"+ {calculate_distance_XP} очков опыта за расстояние\n"
            f"+ {calculate_speed_XP} очков опыта за скорость\n"
            f"Итого заработано: <b>{new_XP} очков опыта</b>\n\n"
            f"<i>Сейчас вы можете использовать очки опыта для покупки подписки!</i>\n\n"
            # f"<i>В ближайшее время появятся новые возможности:</i>\n"
            # f"🔹 Приоритет к лучшим заказам\n"
            # f"🔹 Открытие лутбоксов с наградами\n"
            # f"🔹 Прокачка рейтинга и уровней\n"
            # f"🔹 Обмен очков на криптовалюту\n"
            # f"🔹 Доступ к уникальным заданиям\n"
            # f"🔹 Покупка реальных предметов во внутреннем магазине\n\n"
        )

        await callback_query.message.answer(
            text=text_1,
            disable_notification=False,
            parse_mode="HTML",
        )

        await callback_query.message.answer(
            text=text_2,
            disable_notification=False,
            parse_mode="HTML",
        )

        await state.set_state(current_state)
        await rediska.set_state(courier_bot_id, tg_id, current_state)

        await callback_query.answer("👍 Заказ завершен", show_alert=False)

        await callback_query.message.delete()

    except Exception as e:
        await callback_query.answer("Ошибка при завершении заказа.", show_alert=True)
        log.error(f"Ошибка при завершении заказа: {e}")


# ---
# ---


@courier_r.message(
    F.text == "/my_orders",
)
@courier_r.callback_query(
    F.data == "back_myOrders",
)
async def cmd_my_orders(
    event: Message | CallbackQuery,
    state: FSMContext,
):
    """Обрабатывает запрос на просмотр заказов курьера. /my_orders, back_myOrders"""

    current_state = CourierState.myOrders.state
    is_callback = isinstance(event, CallbackQuery)
    tg_id = event.from_user.id

    if is_callback:
        await event.answer(
            "↩️ Назад",
            show_alert=False,
        )

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

        await event.message.edit_text(
            text,
            reply_markup=reply_kb,
            disable_notification=True,
            parse_mode="HTML",
        )
    else:

        await event.answer(
            text=text,
            reply_markup=reply_kb,
            disable_notification=True,
            parse_mode="HTML",
        )

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)


@courier_r.callback_query(
    F.data.in_(
        {
            "active_orders",
            "completed_orders",
        },
    ),
)
async def get_my_orders(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обрабатывает запрос на просмотр заказов курьера. active_orders, completed_orders"""

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
        callback_query.data,
        (None, None, ""),
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
            "one_my_order" if len(orders_data) == 1 else "complete_orders"
        )

    await callback_query.message.edit_text(
        orders_data[first_order_id]["text"],
        reply_markup=reply_markup,
        disable_notification=True,
        disable_web_page_preview=True,
        parse_mode="HTML",
    )


@courier_r.callback_query(
    F.data.in_(
        {
            "next_right_mo",
            "back_left_mo",
        },
    ),
)
async def handle_order_navigation(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обрабатывает навигацию по заказам курьера. next_right_mo, back_left_mo"""

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
        disable_web_page_preview=True,
        parse_mode="HTML",
    )


# ---
# ---


@courier_r.message(
    F.text == "/profile",
)
async def cmd_profile(
    message: Message,
    state: FSMContext,
):
    """Обрабатывает запрос на просмотр профиля курьера. /profile"""

    current_state = CourierState.default.state
    tg_id = message.from_user.id
    moscow_time = await Time.get_moscow_time()

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)

    courier_name, courier_phone, courier_city, end_date = (
        await courier_data.get_courier_full_info(tg_id)
    )

    if end_date and end_date >= moscow_time:
        remaining_days = (end_date - moscow_time).days
        subscription_status = (
            f"<b>Подписка:</b> Активна 🚀\n"
            f"📅 Действует до: {end_date.strftime('%d.%m.%Y')}\n"
            f"🕒 Осталось дней: {remaining_days}\n\n"
        )
    else:
        subscription_status = "<b>Подписка:</b> Не активна\n\n"

    courier_XP = await courier_data.get_courier_XP(tg_id)

    text = (
        f"👤 <b>Профиль курьера</b>\n\n"
        f"Посмотрите или измените данные о себе.\n\n"
        f"• Номер нужен для связи с заказчиком.\n\n"
        f"<b>Имя:</b> {courier_name}\n"
        f"<b>Номер:</b> {courier_phone}\n"
        f"<b>Город:</b> {courier_city}\n\n"
        f"{subscription_status}"
        f"Ваши очки опыта: <b>{courier_XP}</b>\n\n"
    )

    reply_kb = await kb.get_courier_kb("/profile")

    await message.answer(
        text,
        reply_markup=reply_kb,
        disable_notification=True,
        parse_mode="HTML",
    )


@courier_r.callback_query(
    F.data == "set_my_name",
)
async def set_name(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обрабатывает запрос на изменение имени курьера. set_my_name"""

    await callback_query.answer("Изменить имя:", show_alert=False)

    current_state = CourierState.change_Name.state
    tg_id = callback_query.from_user.id

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)

    text = f"Изменить данные профиля.\n\n" f"<b>Ваше имя:</b>"
    await callback_query.message.answer(
        text,
        reply_markup=ReplyKeyboardRemove(),
        disable_notification=True,
        parse_mode="HTML",
    )

    await callback_query.message.delete()


@courier_r.callback_query(
    F.data == "set_my_phone",
)
async def set_phone(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обрабатывает запрос на изменение телефона курьера. set_my_phone"""

    await callback_query.answer("Изменить телефон:", show_alert=False)

    current_state = CourierState.change_Phone.state
    tg_id = callback_query.from_user.id

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)

    reply_kb = await kb.get_courier_kb("phone_number")
    text = f"Изменить данные профиля.\n\n" f"<b>Ваш Телефон:</b>"
    await callback_query.message.answer(
        text=text,
        disable_notification=True,
        reply_markup=reply_kb,
        parse_mode="HTML",
    )

    await callback_query.message.delete()


@courier_r.callback_query(
    F.data == "set_my_city",
)
async def set_city(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обрабатывает запрос на изменение города курьера. set_my_city"""

    await callback_query.answer("Изменить город:", show_alert=False)

    current_state = CourierState.change_City.state
    tg_id = callback_query.from_user.id

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)

    text = f"Изменить данные профиля.\n\n" f"<b>Ваш город:</b>"
    await callback_query.message.answer(
        text=text,
        reply_markup=ReplyKeyboardRemove(),
        disable_notification=True,
        parse_mode="HTML",
    )

    await callback_query.message.delete()


# ---
# ---


@courier_r.message(
    filters.StateFilter(
        CourierState.change_Name,
    ),
)
async def change_name(
    message: Message,
    state: FSMContext,
):
    """Обрабатывает изменение имени курьера. CourierState.change_Name"""

    current_state = CourierState.default.state
    tg_id = message.from_user.id
    new_name = message.text

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)

    _ = await courier_data.update_courier_name(tg_id, new_name)
    _ = await rediska.set_name(courier_bot_id, tg_id, new_name)

    text = (
        f"Имя было изменено на {new_name} 🎉\n\n"
        f"▼ <b>Выберите действие в • ≡ Меню •</b>"
    )

    await message.answer(
        text,
        disable_notification=True,
        parse_mode="HTML",
    )


@courier_r.message(
    filters.StateFilter(
        CourierState.change_Phone,
    ),
)
async def change_phone(
    message: Message,
    state: FSMContext,
):
    """Обрабатывает изменение телефона курьера. CourierState.change_Phone"""

    current_state = CourierState.default.state
    tg_id = message.from_user.id
    phone = message.contact.phone_number

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)

    _ = await courier_data.update_courier_phone(tg_id, phone)
    _ = await rediska.set_phone(courier_bot_id, tg_id, phone)

    text = (
        f"Номер был изменен на {phone} 🎉\n\n"
        f"▼ <b>Выберите действие в • ≡ Меню •</b>"
    )

    await message.answer(
        text,
        reply_markup=ReplyKeyboardRemove(),
        disable_notification=True,
        parse_mode="HTML",
    )


@courier_r.message(
    filters.StateFilter(
        CourierState.change_City,
    ),
)
async def change_city(
    message: Message,
    state: FSMContext,
):
    """Обрабатывает изменение города курьера. CourierState.change_City"""

    tg_id = message.from_user.id

    russian_cities = await cities.get_cities()
    city, _ = await find_closest_city(message.text, russian_cities)

    if not city:

        current_state = CourierState.change_City.state
        text = f"Введите корректное название города!\n<b>Ваш город:</b>"
        await message.answer(
            text,
            disable_notification=True,
            parse_mode="HTML",
        )

    else:

        current_state = CourierState.default.state
        text = (
            f"Город был изменен на {city} 🎉\n\n"
            f"▼ <b>Выберите действие в • ≡ Меню •</b>"
        )

        _ = await courier_data.update_courier_city(tg_id, city)
        _ = await rediska.set_city(courier_bot_id, tg_id, city)

        await message.answer(
            text,
            disable_notification=True,
            parse_mode="HTML",
        )

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)


# ---
# ---


@courier_r.message(
    F.text == "/info",
)
async def cmd_info(
    message: Message,
    state: FSMContext,
):
    """Обработчик команды /info."""

    current_state = CourierState.default.state
    tg_id = message.from_user.id

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)

    text = (
        f"ℹ️ <b>Информация</b>\n\n"
        f"Здесь вы можете ознакомиться с основной информацией о сервисе, задать вопрос или предложить свою идею!\n\n"
        f"<a href='https://disk.yandex.ru/i/PGll6-rJV7QhNA'>О Нас 'Raketa'</a>\n"
        f"<a href='https://disk.yandex.ru/i/NiwitOTuU0YPXQ'>Частые вопросы и ответы на них</a>\n"
        f" •\n"
        f"<a href='https://t.me/raketadeliverychannel/14'>Вопросы - Обсуждения - Предложения</a>"
    )

    await message.answer(
        text,
        disable_notification=True,
        disable_web_page_preview=True,
        parse_mode="HTML",
    )


@courier_r.message(
    F.text == "/rules",
)
async def cmd_rules(
    message: Message,
    state: FSMContext,
):
    """Обрабатывает запрос на просмотр правил сервиса. /rules"""

    current_state = CourierState.default.state
    tg_id = message.from_user.id

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)

    text = (
        f"⚖️ <b>Правила сервиса</b>\n\n"
        f"Начиная использование сервиса, вы соглашаетесь с "
        f"<a href='https://disk.yandex.ru/i/d2S9C4zW4hmL0w'>"
        f"Пользовательским соглашением и правилами использования</a>, а также "
        f"<a href='https://telegram.org/privacy'>Политикой конфиденциальности</a>.\n\n"
        f"<i>*Обращаем внимание, что любые действия, связанные с заказами, "
        f"отправкой или получением посылок, должны соответствовать законодательству "
        f"вашего государства и общепринятым этическим нормам.</i>\n\n"
    )

    await message.answer(
        text,
        disable_notification=True,
        disable_web_page_preview=True,
        parse_mode="HTML",
    )


@courier_r.message(
    F.text == "/make_order",
)
async def cmd_make_order(
    message: Message,
    state: FSMContext,
):
    """Обрабатывает запрос на переход в бота для клиентов. /make_order"""

    current_state = CourierState.default.state
    tg_id = message.from_user.id

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)

    text = (
        f"📦 <b>Оформить заказ</b>\n\n"
        f"⦿ Сделать заказ у нас — это просто и удобно!\n"
        f"⦿ Наслаждайтесь удобством и скоростью нашего сервиса!"
    )
    reply_kb = await kb.get_courier_kb("/make_order")

    await message.answer(
        text=text,
        reply_markup=reply_kb,
        disable_notification=True,
        parse_mode="HTML",
    )


@courier_r.message(
    F.text == "/become_partner",
)
async def cmd_become_partner(
    message: Message,
    state: FSMContext,
):
    """Обрабатывает запрос на переход в бот для партнеров. /become_partner"""

    current_state = CourierState.default.state
    tg_id = message.from_user.id

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)

    refund_percent = await admin_data.get_refund_percent()

    text = (
        f"💼 <b>Станьте партнёром Raketa!</b>\n\n"
        f"🚀 <b>Зарабатывайте на привлечении курьеров и клиентов!</b>\n\n"
        f"🔹 Приглашайте курьеров и получайте <b>{refund_percent}% с их подписки</b>\n"
        f"🔹 Продвигайте сервис среди клиентов и увеличивайте свои доходы\n"
        f"🔹 Работайте когда хотите — без вложений и рисков!\n\n"
        f"💰 Чем больше курьеров — тем больше доход! Присоединяйтесь!"
    )
    ttl = await title.get_title_courier("/become_partner")
    reply_kb = await kb.get_courier_kb("/become_partner")

    await message.answer_photo(
        photo=ttl,
        caption=text,
        reply_markup=reply_kb,
        disable_notification=True,
        parse_mode="HTML",
    )


@courier_r.message(
    F.text == "/orders_bot",
)
async def cmd_orders_bot(
    message: Message,
    state: FSMContext,
):
    """Обрабатывает запрос на переход в бот заказов. /orders_bot"""

    current_state = CourierState.default.state
    tg_id = message.from_user.id

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)

    text = (
        f"📋 <b>Бот заказов Raketa Delivery</b>\n\n"
        f"🔹 <b>Получайте заказы</b> в удобном формате и выбирайте подходящие\n"
        f"🔹 <b>Оперативные уведомления</b> о новых заказах в вашем городе\n"
        f"🔹 <b>Гибкий график</b> — работайте когда удобно\n\n"
        f"🚀 <b>Подключайтесь и начните зарабатывать с Raketa прямо сейчас!</b>"
    )

    reply_kb = await kb.get_courier_kb("/orders_bot")

    await message.answer(
        text=text,
        reply_markup=reply_kb,
        disable_notification=True,
        parse_mode="HTML",
    )


@courier_r.message(
    F.text == "/channel",
)
async def cmd_channel(
    message: Message,
    state: FSMContext,
):
    """Обрабатывает запрос на переход в телеграмм канал. /channel"""

    current_state = CourierState.default.state
    tg_id = message.from_user.id

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)

    text = (
        f"📣 <b>Официальный канал Raketa Delivery</b>\n\n"
        f"🔹 <b>Актуальные новости</b> сервиса и важные объявления\n"
        f"🔹 <b>Полезные советы</b> для курьеров и партнеров\n"
        f"🔹 <b>Информация</b> о новых функциях и возможностях\n\n"
        f"🚀 <b>Подписывайтесь, чтобы быть в курсе всех обновлений!</b>\n\n"
    )

    reply_kb = await kb.get_courier_kb("/channel")

    await message.answer(
        text=text,
        reply_markup=reply_kb,
        disable_notification=True,
        parse_mode="HTML",
    )


# ---


@courier_r.message(
    F.text == "/support",
)
async def cmd_support(
    message: Message,
    state: FSMContext,
):
    """Обработчик команды /support."""

    current_state = CourierState.default.state
    tg_id = message.from_user.id

    text = (
        f"👨‍💼 <b>Поддержка</b>\n\n"
        f"Если у вас возникли вопросы или проблемы, "
        f"вы можете обратиться в нашу службу поддержки.\n\n"
        f"<i>*Мы всегда готовы помочь вам!</i>"
    )

    reply_kb = await kb.get_customer_kb("/support")

    await message.answer(
        text=text,
        reply_markup=reply_kb,
        disable_notification=True,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)


# ---
# ---


@courier_r.callback_query(
    F.data == "my_statistic",
)
async def get_courier_statistic(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обрабатывает запрос на просмотр статистики курьера. my_statistic"""

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
        total_distance,
        total_money_earned,
    ) = await courier_data.get_courier_statistic(tg_id)

    text = (
        f"📊 <b>Ваша статистика</b>\n\n"
        f"Всего заказов: <b>{total_orders}</b>\n"
        f"Завершенные заказы: <b>{completed_orders}</b>\n"
        f"Среднее время выполнения: <b>{average_execution_time / 60:.2f} мин</b>\n"
        f"Средняя скорость: <b>{average_speed:.2f} км/ч</b>\n"
        f"Пройденное расстояние: <b>{total_distance:.2f} км</b>\n"
        f"Сумма заработка: <b>{total_money_earned} ₽</b>\n"
    )

    reply_kb = await kb.get_courier_kb("go_back")

    await callback_query.message.edit_text(
        text,
        reply_markup=reply_kb,
        parse_mode="HTML",
    )


# ---
# ---


@payment_r.message(
    F.text == "/subs",
)
@payment_r.callback_query(
    F.data == "pay_sub",
)
async def payment_invoice(
    event: Message | CallbackQuery,
    state: FSMContext,
):
    """Обрабатывает запрос на оплату подписки. /subs, pay_sub"""

    tg_id = event.from_user.id
    moscow_time = await Time.get_moscow_time()

    current_state = CourierState.default.state
    await state.set_state(current_state)
    await rediska.set_state(courier_bot_id, tg_id, current_state)

    if isinstance(event, CallbackQuery):
        await event.answer("💵 Оформить подписку", show_alert=False)
        await event.message.delete()

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

        await event.answer(
            text=text,
            reply_markup=keyboard,
            disable_notification=True,
            parse_mode="HTML",
        )

    else:

        await _use_XP(event)


@payment_r.callback_query(
    F.data == "extend_sub",
)
async def extend_subscription(
    event: CallbackQuery,
):
    """Обрабатывает запрос на продление подписки. extend_sub"""

    await event.message.delete()

    await _use_XP(event)


async def _use_XP(
    event: Message | CallbackQuery,
):
    """Использует очки опыта для оплаты подписки."""

    text = (
        f"🚀 <b>Оплатить подписку</b>\n\n"
        f"Выберите способ оплаты:\n\n"
        f"💵 Оплатить подписку\n"
        f"✴️ Использовать очки опыта"
    )

    tg_id = event.from_user.id

    courier_XP = await courier_data.get_courier_XP(tg_id)

    if courier_XP is None:
        courier_XP = 0

    price_rub = await admin_data.get_subscription_price()
    price_rub = price_rub // 100
    new_price_rub = round((price_rub - courier_XP), 2)

    log.info(
        f"price_rub: {price_rub}, new_price_rub: {new_price_rub}, courier_XP: {courier_XP}"
    )

    if courier_XP >= price_rub:
        courier_XP = price_rub

    keyboard = await kb.courier_XP_kb(
        "use_XP",
        rub=round(price_rub, 2),
        current_xp=round(courier_XP, 2),
        new_price=round(new_price_rub, 2),
    )

    if isinstance(event, Message):
        await event.answer(
            text=text,
            reply_markup=keyboard,
            disable_notification=True,
            parse_mode="HTML",
        )

    elif isinstance(event, CallbackQuery):
        await event.message.answer(
            text=text,
            reply_markup=keyboard,
            disable_notification=True,
            parse_mode="HTML",
        )


@payment_r.callback_query(
    F.data == "use_rub",
)
@payment_r.callback_query(
    F.data == "use_XP",
)
async def send_payment_invoice(
    event: CallbackQuery,
    state: FSMContext,
):
    """Отправляет инвойс для оплаты подписки."""

    price_rub = await admin_data.get_subscription_price()

    tg_id = event.from_user.id
    chat_id = event.message.chat.id

    use_XP = False

    log.info(f"event.data: {event.data}")

    if event.data == "use_XP":

        use_XP = True

        courier_XP = await courier_data.get_courier_XP(tg_id)
        if courier_XP is None:
            courier_XP = 0
        price_rub = price_rub - (courier_XP * 100)
        new_XP = -courier_XP
        if price_rub < 0:
            price_rub = 0

        await state.update_data(
            use_XP=use_XP,
            new_XP=new_XP,
            new_price=price_rub,
        )
        await rediska.save_fsm_state(
            state,
            courier_bot_id,
            tg_id,
        )

    prices = [
        LabeledPrice(
            label="Месячная подписка",
            amount=price_rub,
        ),
    ]

    log.info(f"price_rub: {price_rub}")
    log.info(f"use_XP: {use_XP}")

    await state.update_data(
        use_XP=use_XP,
        new_price=price_rub,
    )
    await rediska.save_fsm_state(
        state,
        courier_bot_id,
        tg_id,
    )

    if not payment_provider:
        log.error("Ошибка: provider_token не найден. Проверьте переменные окружения.")
        return

    await event.bot.send_invoice(
        chat_id=chat_id,
        title="Подписка Raketa",
        description="Оформите подписку Raketa",
        payload="Payment through a bot",
        provider_token=payment_provider,
        currency="RUB",
        prices=prices,
        max_tip_amount=50000,
        start_parameter="",
        photo_url="https://i.ibb.co/NpQzZyY/subs.jpg",
        photo_width=1200,
        photo_height=720,
        need_name=False,
        need_phone_number=False,
        need_email=False,
        reply_markup=None,
    )

    # await event.message.delete()


@payment_r.pre_checkout_query()
async def pre_checkout_query(
    pre_checkout_query: PreCheckoutQuery,
    state: FSMContext,
):
    """Обрабатывает запрос на предварительную проверку оплаты."""

    price_rub = await admin_data.get_subscription_price()

    data = await state.get_data()
    use_XP = data.get("use_XP", False)

    if use_XP:
        new_price = data.get("new_price")
        price_rub = new_price

    log.info(f"price_rub: {price_rub}")
    log.info(f"use_XP: {use_XP}")

    try:
        if (
            pre_checkout_query.currency == "RUB"
            and pre_checkout_query.total_amount == price_rub
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
        log.error(f"Ошибка: {str(e)}")
        await pre_checkout_query.bot.answer_pre_checkout_query(
            pre_checkout_query.id,
            ok=False,
            error_message=f"Ошибка оплаты!",
        )


@payment_r.message(
    F.content_type == ContentType.SUCCESSFUL_PAYMENT,
)
async def successful_payment(
    message: Message,
    state: FSMContext,
):
    """Обрабатывает успешную оплату подписки."""

    tg_id = message.from_user.id

    data = await state.get_data()
    use_XP = data.get("use_XP", False)

    try:

        courier_id = await courier_data.get_courier_id(tg_id)

        sum = round((message.successful_payment.total_amount / 100), 2)

        log.info(f"sum: {sum}")

        _ = await courier_data.set_payment(
            courier_id,
            sum,
        )

        if use_XP:
            new_XP = data.get("new_XP")
            _ = await courier_data.update_courier_XP(tg_id, new_XP)

        is_updated = await courier_data.update_courier_subscription(
            tg_id=tg_id, days=30
        )

        if is_updated:
            ttl = await title.get_title_courier("success_payment")
            text = f"Спасибо за подписку!\nСумма: {sum} {message.successful_payment.currency}"
            reply_kb = await kb.get_courier_kb(
                "success_payment",
            )
            await message.answer_photo(
                photo=ttl,
                caption=text,
                reply_markup=reply_kb,
            )

            seed_key = await courier_data.get_courier_seed_key_by_tg_id(tg_id=tg_id)

            (
                partner_tg_id,
                balance,
                is_blocked,
            ) = await admin_data.get_partner_full_info_by_SEED(seed=seed_key)

            if not is_blocked:
                refund_percent = await admin_data.get_refund_percent()
                added_balance = int(sum * refund_percent / 100)
                await partner_bot.send_message(
                    chat_id=partner_tg_id,
                    text=f"Ваш реферал произвел оплату, <b>+{added_balance}₽</b> к вашему балансу!\nБаланс: <b>{balance}₽</b>",
                    disable_notification=True,
                )

            log.info(f"Subscription updated successfully for courier {tg_id}.")
        else:
            log.error(f"Failed to update subscription for courier {tg_id}.")
    except Exception as e:
        log.error(f"Error updating subscription for courier {tg_id}: {e}")


# ---
# ---


@courier_fallback.message()
async def handle_unrecognized_message(
    message: Message,
):
    """Обрабатывает нераспознанные сообщения."""

    await message.delete()
