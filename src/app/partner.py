from ._deps import (
    CommandStart,
    FSMContext,
    PartnerState,
    BufferedInputFile,
    InputMediaDocument,
    CallbackQuery,
    Message,
    filters,
    ContentType,
    ReplyKeyboardRemove,
    LabeledPrice,
    zlib,
    Time,
    json,
    F,
    find_closest_city,
    seed_maker,
    partner_bot,
    partner_bot_id,
    partner_r,
    partner_fallback,
    partner_data,
    handler,
    kb,
    title,
    rediska,
    cities,
    log,
)


# ---
# ---


@partner_r.message(
    CommandStart(),
)
async def cmd_start(
    message: Message,
    state: FSMContext,
):
    """Обрабатывает команду /start для партнера."""

    tg_id = message.from_user.id
    is_reg = await rediska.is_reg(partner_bot_id, tg_id)
    new_message = None

    if is_reg:
        current_state = PartnerState.default.state
        await message.answer(
            text="▼ <b>Выберите действие в Меню ...</b>",
            disable_notification=True,
            parse_mode="HTML",
        )

    else:
        current_state = PartnerState.reg_state.state
        photo_title = await title.get_title_partner("/start")
        text = (
            "🚀 <b>Добро пожаловать в Raketa Delivery | Партнеры</b>\n\n"
            "🔹 <b>Наши условия:</b>\n"
            "Вы привлекаете как клиентов, так и курьеров, и получаете <b>30% с подписки каждого курьера</b>, которого привлекли.\n\n"
            "🔸 Привлекая клиентов, вы помогаете увеличивать сеть сервиса, что делает его более востребованным и выгодным.\n\n"
            "🔸 Работайте в удобное время, привлекай новых пользователей и получайте пассивный доход!\n\n"
            "💰 <b>Присоединяйтесь и начинайте зарабатывать уже сейчас!</b>"
        )
        reply_kb = await kb.get_partner_kb("/start")
        new_message = await message.answer_photo(
            photo=photo_title,
            caption=text,
            reply_markup=reply_kb,
            disable_notification=True,
            parse_mode="HTML",
        )

    await state.set_state(current_state)
    await rediska.set_state(partner_bot_id, tg_id, current_state)

    if new_message:
        await handler.catch(
            bot=partner_bot,
            chat_id=message.chat.id,
            user_id=tg_id,
            new_message=new_message,
            current_message=message,
            delete_previous=True,
        )


@partner_r.callback_query(
    F.data == "reg_partner",
)
async def data_reg(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обрабатывает запрос на регистрацию курьера."""

    await callback_query.answer("✍️ Регистрация", show_alert=False)

    current_state = PartnerState.reg_Name.state
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
    await rediska.set_state(partner_bot_id, tg_id, current_state)

    await handler.catch(
        bot=partner_bot,
        chat_id=callback_query.message.chat.id,
        user_id=tg_id,
        new_message=new_message,
        current_message=None,
        delete_previous=True,
    )


@partner_r.message(
    filters.StateFilter(PartnerState.reg_Name),
)
async def data_name(
    message: Message,
    state: FSMContext,
):
    """Обрабатывает имя партнера. PartnerState.reg_Name"""

    current_state = PartnerState.reg_Phone.state
    tg_id = message.from_user.id
    courier_name = message.text

    reply_kb = await kb.get_partner_kb("phone_number")
    text = (
        f"Привет, {courier_name}!👋\n\nПожалуйста, укажите ваш номер телефона.\n\n"
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
    await rediska.set_state(partner_bot_id, tg_id, current_state)
    await rediska.set_name(partner_bot_id, tg_id, courier_name)

    await handler.catch(
        bot=partner_bot,
        chat_id=message.chat.id,
        user_id=tg_id,
        new_message=new_message,
        current_message=message,
        delete_previous=True,
    )


@partner_r.message(
    filters.StateFilter(PartnerState.reg_Phone),
)
async def data_phone(
    message: Message,
    state: FSMContext,
):
    """Обрабатывает номер телефона партнера. PartnerState.reg_Phone"""

    current_state = PartnerState.reg_City.state
    tg_id = message.from_user.id
    courier_phone = message.contact.phone_number

    text = f"<b>Ваш город:</b>"

    new_message = await message.answer(
        text=text,
        disable_notification=True,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(partner_bot_id, tg_id, current_state)
    await rediska.set_phone(partner_bot_id, tg_id, courier_phone)

    await handler.catch(
        bot=partner_bot,
        chat_id=message.chat.id,
        user_id=tg_id,
        new_message=new_message,
        current_message=message,
        delete_previous=True,
    )


@partner_r.message(
    filters.StateFilter(PartnerState.reg_City),
)
async def data_city(
    message: Message,
    state: FSMContext,
):
    """Обрабатывает город партнера. PartnerState.reg_City"""

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
        current_state = PartnerState.generate_seed_key.state
        reply_kb = await kb.get_partner_kb("generate_seed")
        text = (
            f"🔑 <b>Генерация ключа партнёра</b>\n\n"
            f"Для того чтобы вы могли привлекать новых пользователей, необходимо сгенерировать уникальный ключ. "
            f"Этот ключ закрепляет клиентов и курьеров за вами, позволяя системе учитывать вашу активность "
            f"и начислять вам вознаграждение.\n\n"
            f"Как это работает?\n"
            f"1️⃣ После генерации ключа вы сможете передавать его курьерам и клиентам.\n"
            f"2️⃣ Курьеры, регистрируясь в системе с вашим ключом, становятся вашими рефералами.\n"
            f"3️⃣ С каждого оплаченного месяца подписки курьера вы будете получать 30% от её стоимости.\n"
            f"4️⃣ Чем больше активных курьеров и клиентов привязано к вашему ключу, тем выше ваш доход.\n\n"
        )

        new_message = await message.answer(
            text,
            reply_markup=reply_kb,
            disable_notification=True,
            parse_mode="HTML",
        )

        await state.set_state(current_state)
        await rediska.set_state(partner_bot_id, tg_id, current_state)
        await rediska.set_city(partner_bot_id, tg_id, city)

    await handler.catch(
        bot=partner_bot,
        chat_id=message.chat.id,
        user_id=tg_id,
        new_message=new_message,
        current_message=message,
        delete_previous=True,
    )


@partner_r.callback_query(
    F.data == "generate_seed_key",
)
@partner_r.callback_query(
    F.data == "try_save_again",
)
async def partner_generate_seed(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обрабатывает генерацию seed для партнера с возможностью повторной попытки."""

    current_state = PartnerState.default.state
    tg_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id

    seed_key_from_redis = await rediska.get_seed_key(partner_bot_id, tg_id)
    all_seed_keys = await partner_data.get_all_seed_keys()

    log.info(f"Seed key from redis: {seed_key_from_redis}")
    log.info(f"All seed keys: {all_seed_keys}")

    if not seed_key_from_redis:

        await callback_query.answer("🔑 Генерация ключа...", show_alert=False)

        partner_name, partner_phone, partner_city = await rediska.get_user_info(
            partner_bot_id, tg_id
        )

        try:

            is_set_reg = await rediska.set_reg(partner_bot_id, tg_id, True)
            is_set_partner_to_db = await partner_data.set_new_partner(
                tg_id, partner_name, partner_phone, partner_city
            )

            if is_set_reg and is_set_partner_to_db:
                partner_id, partner_name, partner_phone, partner_city = (
                    await partner_data.get_partner_info(tg_id)
                )

                while True:
                    seed_key = await seed_maker.generate_seed()
                    if seed_key not in all_seed_keys:
                        break

                log.info(f"Generated unique seed key: {seed_key}")

                is_create = await partner_data.create_new_seed_key(partner_id, seed_key)
                await rediska.set_seed_key(partner_bot_id, tg_id, seed_key)

                if is_create:
                    text = (
                        f"🔑 <b>Ваш ключ:</b> <b><code>{seed_key}</code></b>\n\n"
                        f"- Этот ключ служит промокодом для ваших клиентов. Используя его при первом заказе, они получат скидку на доставку.\n\n"
                        f"- Для курьеров это также промокод, который дает скидку на подписку. Таким образом, курьеры могут снизить свои затраты на участие в сервисе.\n\n"
                        f"- Для вас, как партнера, этот ключ важен тем, что мы отслеживаем, сколько людей зарегистрировались с вашим ключом. "
                        f"Чем больше клиентов и курьеров, использующих ваш ключ, тем выше ваш доход, поскольку вы получаете 30% с подписки курьеров каждый месяц.\n\n"
                        f"▼ <b>Выберите действие в Меню ...</b>"
                    )

                    new_message = await callback_query.message.answer(
                        text=text,
                        disable_notification=True,
                        parse_mode="HTML",
                    )

                    await state.set_state(current_state)
                    await rediska.set_state(partner_bot_id, tg_id, current_state)

                else:
                    new_message = await callback_query.message.answer(
                        text="<b>‼️ Произошла ошибка при создании ключа, попробуйте позже еще раз!</b>\n\n",
                        disable_notification=True,
                        parse_mode="HTML",
                    )

            else:
                new_message = await callback_query.message.answer(
                    text="<b>‼️ Произошла ошибка при сохранении данных, попробуйте позже еще раз!</b>\n\n",
                    disable_notification=True,
                    parse_mode="HTML",
                )

        except Exception as e:
            new_message = await callback_query.message.answer(
                text="<b>‼️ Произошла ошибка, попробуйте позже.</b>\n\n",
                disable_notification=True,
                parse_mode="HTML",
            )

    else:

        text = (
            f"🔑 <b>Ваш ключ:</b> <b><code>{seed_key}</code></b>\n\n"
            f"- Этот ключ служит промокодом для ваших клиентов. Используя его при первом заказе, они получат скидку на доставку.\n\n"
            f"- Для курьеров это также промокод, который дает скидку на подписку. Таким образом, курьеры могут снизить свои затраты на участие в сервисе.\n\n"
            f"- Для вас, как партнера, этот ключ важен тем, что мы отслеживаем, сколько людей зарегистрировались с вашим ключом. "
            f"Чем больше клиентов и курьеров, использующих ваш ключ, тем выше ваш доход, поскольку вы получаете 30% с подписки курьеров каждый месяц.\n\n"
            f"▼ <b>Выберите действие ...</b>"
        )

        new_message = await callback_query.message.answer(
            text=text,
            disable_notification=True,
            parse_mode="HTML",
        )

    await handler.catch(
        bot=partner_bot,
        chat_id=chat_id,
        user_id=tg_id,
        new_message=new_message,
        current_message=None,
        delete_previous=True,
    )


# ---
# ---


@partner_r.message(F.text == "/refs")
@partner_r.callback_query(F.data == "refresh_refs")
async def cmd_refs(event: Message | CallbackQuery, state: FSMContext):
    """Обрабатывает команду /refs"""

    tg_id = event.from_user.id
    current_state = PartnerState.default.state

    customers, couriers = await partner_data.get_all_my_seed_key_referrals(tg_id=tg_id)
    paid_subscriptions = await partner_data.get_paid_subscriptions_count(tg_id=tg_id)
    total_earnings = await partner_data.get_my_all_time_earn(tg_id=tg_id)
    total_refs = len(customers) + len(couriers)

    text = (
        f"<b>👥 Рефералы</b>\n\n"
        f"Здесь вы можете посмотреть основную статистику о рефералах, которых вы привлекли в сервис.\n\n"
        f" - Вы привлекли пользователей: <b>{total_refs}</b>\n"
        f" - Клиентов: <b>{len(customers)}</b>\n"
        f" - Курьеров: <b>{len(couriers)}</b>\n"
        f" - Оплачено подписок: <b>{paid_subscriptions}</b>\n"
        f" - Общий заработок: <b>{total_earnings}₽</b>\n\n"
    )

    reply_kb = await kb.get_partner_kb("refresh_refs")

    state_data = await state.get_data()
    saved_text = state_data.get("message_text_refs")
    saved_kb = state_data.get("message_kb_refs")

    new_kb_json = json.dumps(reply_kb.model_dump())

    if isinstance(event, Message):
        await event.answer(
            text=text,
            reply_markup=reply_kb,
            disable_notification=True,
            parse_mode="HTML",
        )

    elif isinstance(event, CallbackQuery):

        await event.answer(
            text="🔄 Обновление данных...",
            show_alert=False,
        )

        if saved_text != text or saved_kb != new_kb_json:
            await event.message.edit_text(
                text=text,
                reply_markup=reply_kb,
                parse_mode="HTML",
            )

    await state.set_state(current_state)
    await state.update_data(message_text_refs=text, message_kb_refs=new_kb_json)
    await rediska.set_state(partner_bot_id, tg_id, current_state)
    await rediska.save_fsm_state(state, partner_bot_id, tg_id)


@partner_r.message(
    F.text == "/key",
)
async def cmd_key(
    message: Message,
    state: FSMContext,
):
    """Обрабатывает команду /key"""

    current_state = PartnerState.default.state
    tg_id = message.from_user.id

    seed_key = await rediska.get_seed_key(partner_bot_id, tg_id)

    text = (
        f"Приглашайте курьеров и клиентов, используя этот ключ. "
        f"За каждого привлеченного курьера вы будете получать 30% от его подписки каждый месяц.\n\n"
        f"<b>🔑 Ваш ключ:</b>"
    )

    await message.answer(
        text=text,
        disable_notification=True,
        parse_mode="HTML",
    )

    await message.answer(
        text=f"<b><code>{seed_key}</code></b>\n\n",
        disable_notification=True,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(partner_bot_id, tg_id, current_state)


@partner_r.message(
    F.text == "/info",
)
async def cmd_info(
    message: Message,
    state: FSMContext,
):
    """Обработчик команды /info"""

    current_state = PartnerState.default.state
    tg_id = message.from_user.id

    text = (
        f"ℹ️ <b>Информация</b>\n\n"
        f"Здесь вы можете ознакомиться с основной информацией о сервисе.\n\n"
        f"<a href='https://disk.yandex.ru/i/PGll6-rJV7QhNA'>О Нас 'Raketa'</a>\n"
        f"<a href='https://disk.yandex.ru/i/NiwitOTuU0YPXQ'>Частые вопросы и ответы на них</a>"
    )

    await message.answer(
        text=text,
        disable_notification=True,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )

    await state.set_state(current_state)
    await rediska.set_state(partner_bot_id, tg_id, current_state)


@partner_r.message(F.text == "/balance")
@partner_r.callback_query(F.data == "refresh_balance")
async def cmd_balance(event: Message | CallbackQuery, state: FSMContext):
    """Обрабатывает команду /balance"""

    tg_id = event.from_user.id
    current_state = PartnerState.default.state

    balance = await partner_data.get_partner_balance(tg_id)

    text = (
        f"📊 <b>Текущий баланс</b>\n\n"
        f"Здесь вы можете посмотреть ваш текущий баланс с момента последней выплаты.\n\n"
        f"🔸 <b>Баланс:</b> <b>{balance}₽</b>\n"
    )

    reply_kb = await kb.get_partner_kb("earn_request")

    state_data = await state.get_data()
    saved_text = state_data.get("message_text_balance")
    saved_kb = state_data.get("message_kb_balance")

    new_kb_json = json.dumps(reply_kb.model_dump())

    if isinstance(event, Message):
        await event.answer(
            text=text,
            reply_markup=reply_kb,
            disable_notification=True,
            parse_mode="HTML",
        )

    elif isinstance(event, CallbackQuery):

        await event.answer(
            text="🔄 Обновление баланса...",
            show_alert=False,
        )

        if saved_text != text or saved_kb != new_kb_json:
            await event.message.edit_text(
                text=text,
                reply_markup=reply_kb,
                parse_mode="HTML",
            )

    await state.set_state(current_state)
    await state.update_data(message_text_balance=text, message_kb_balance=new_kb_json)
    await rediska.set_state(partner_bot_id, tg_id, current_state)
    await rediska.save_fsm_state(state, partner_bot_id, tg_id)


# ---
# ---


@partner_r.message(
    F.text == "/adv",
)
async def cmd_adv(
    message: Message,
    state: FSMContext,
):
    """Обрабатывает команду /adv"""

    tg_id = message.from_user.id
    current_state = PartnerState.default.state

    text = (
        f"📈 <b>Рекламные материалы</b>\n\n"
        f"Здесь вы можете скачать рекламные материалы для привлечения новых пользователей в сервис.\n\n"
        f"🔸 <b>Визитка и буклет для курьера</b>\n"
        f"🔸 <b>Визитка и буклет для клиента</b>\n"
        f"🔸 <b>QR коды отдельно</b>\n"
        f"🔸 <b>Ваш персональный ключ отдельно</b>\n\n"
        f"<i>*Мы подготовили для вас уже готовый материал, но при желании вы можете сделать свой!</i>\n"
    )

    reply_kb = await kb.get_partner_kb("adv_request")

    await message.answer(
        text=text,
        reply_markup=reply_kb,
        disable_notification=True,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(partner_bot_id, tg_id, current_state)


@partner_r.callback_query(F.data == "business_card_courier")
@partner_r.callback_query(F.data == "business_card_customer")
async def data_business_card(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Возвращает визитку"""

    current_state = PartnerState.default.state
    tg_id = callback_query.from_user.id
    seed_key = await partner_data.get_my_seed_key(tg_id)
    callback_data = callback_query.data

    log.info(f"callback_message: {callback_data}")

    try:
        pdf_data = await seed_maker.get_business_card(
            seed_key=seed_key,
            type_template=f"{callback_data}",
        )
        business_card = BufferedInputFile(pdf_data, filename=f"{callback_data}.pdf")

        type_of_users = (
            "курьеров" if callback_data == "business_card_courier" else "клиентов"
        )

        text = (
            f"🔥 <b>Ваша визитка для {type_of_users}</b>\n\n"
            f"Рекомендации по использованию визитки:\n"
            f"1️⃣ Распечатайте визитку и раздавайте ее.\n"
            f"2️⃣ Отправьте визитку в электронном виде в чаты и группы.\n\n"
            f"Отслеживайте количество привлеченных пользователей и ваш доход в разделе <b>Пользователи 👥</b> и <b>Баланс 💰</b>.\n\n"
        )

        await callback_query.message.answer_document(
            document=business_card,
            caption=f"Размеры визитки: 90x50 мм.",
            parse_mode="HTML",
        )

        await callback_query.message.answer(
            text=text,
            parse_mode="HTML",
        )

        await state.set_state(current_state)
        await rediska.set_state(partner_bot_id, tg_id, current_state)

    except Exception as e:
        await callback_query.message.answer(f"Ошибка при генерации визитки: {str(e)}")


@partner_r.callback_query(F.data == "buklet_courier")
@partner_r.callback_query(F.data == "buklet_customer")
async def data_buklet(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Возвращает буклет"""

    current_state = PartnerState.default.state
    tg_id = callback_query.from_user.id
    seed_key = await partner_data.get_my_seed_key(tg_id)
    callback_data = callback_query.data

    log.info(f"callback_message: {callback_data}")

    try:
        pdf_data = await seed_maker.get_business_card(
            seed_key=seed_key,
            type_template=f"{callback_data}",
        )
        buklet = BufferedInputFile(pdf_data, filename=f"{callback_data}.pdf")

        type_of_users = "курьеров" if callback_data == "buklet_courier" else "клиентов"

        text = (
            f"🔥 <b>Ваш буклет для {type_of_users}</b>\n\n"
            f"Рекомендации по использованию буклета:\n"
            f"1️⃣ Распечатайте буклет и раздавайте его.\n"
            f"2️⃣ Отправьте буклет в электронном виде в чаты и группы.\n\n"
            f"Отслеживайте количество привлеченных пользователей и ваш доход в разделе <b>Пользователи 👥</b> и <b>Баланс 💰</b>.\n\n"
        )

        await callback_query.message.answer_document(
            document=buklet,
            caption=f"Размеры буклета: А4 - A5.",
            parse_mode="HTML",
        )

        await callback_query.message.answer(
            text=text,
            parse_mode="HTML",
        )

        await state.set_state(current_state)
        await rediska.set_state(partner_bot_id, tg_id, current_state)

    except Exception as e:
        await callback_query.message.answer(f"Ошибка при генерации буклета: {str(e)}")


@partner_r.callback_query(F.data == "QR_courier")
@partner_r.callback_query(F.data == "QR_customer")
async def data_qr_courier(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Возвращает QR-коды"""

    current_state = PartnerState.default.state
    tg_id = callback_query.from_user.id
    callback_data = callback_query.data

    log.info(f"callback_message: {callback_data}")

    try:
        png_data: tuple = await seed_maker.get_qr_codes(type_of_user=callback_data)
        qr_white = BufferedInputFile(png_data[0], filename=f"{callback_data}_white.png")
        qr_black = BufferedInputFile(png_data[1], filename=f"{callback_data}_black.png")

        type_of_users = "курьеров" if callback_data == "QR_courier" else "клиентов"
        type_of_bot = (
            "@raketadeliverywork_bot"
            if callback_data == "QR_courier"
            else "@raketadelivery_bot"
        )
        link = (
            "https://t.me/raketadeliverywork_bot"
            if callback_data == "QR_courier"
            else "https://t.me/raketadelivery_bot"
        )

        text = (
            f"🔥 <b>QR-коды для {type_of_users}</b>\n\n"
            f"Белый и чёрный в формате .png\n"
            f"Бот: {type_of_bot}\n"
            f"Ссылка: {link}\n\n"
            f"Рекомендации по использованию QR-кода:\n"
            f"1️⃣ Разместите его на своем сайте или в социальных сетях.\n\n"
            f"Отслеживайте количество привлечённых пользователей и ваш доход в разделе <b>Пользователи 👥</b> и <b>Баланс 💰</b>.\n\n"
        )

        await callback_query.message.answer_media_group(
            media=[
                InputMediaDocument(
                    media=qr_white,
                    caption=f"QR-код {type_of_users} (белый)",
                ),
                InputMediaDocument(
                    media=qr_black,
                    caption=f"QR-код {type_of_users} (чёрный)",
                ),
            ]
        )
        await callback_query.message.answer(
            text,
            parse_mode="HTML",
        )

        await state.set_state(current_state)
        await rediska.set_state(partner_bot_id, tg_id, current_state)

    except Exception as e:
        await log.info(f"Ошибка при генерации QR-кода: {str(e)}")
        await callback_query.message.answer(f"Ошибка при генерации QR-кода")


@partner_r.callback_query(F.data == "logo")
async def data_logo(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Возвращает логотипы"""

    current_state = PartnerState.default.state
    tg_id = callback_query.from_user.id

    try:
        png_data: tuple = await seed_maker.get_logo()
        font_logo_white = BufferedInputFile(
            png_data[0],
            filename=f"font_logo_white.png",
        )
        font_logo_black = BufferedInputFile(
            png_data[1],
            filename=f"font_logo_black.png",
        )
        logo_white = BufferedInputFile(
            png_data[2],
            filename=f"logo_white.png",
        )
        logo_black = BufferedInputFile(
            png_data[3],
            filename=f"logo_black.png",
        )

        text = (
            f"🔥 <b>Логотипы сервиса Raketa</b>\n\n"
            f"C надписью и без в формате .png\n\n"
            f"Отслеживайте количество привлечённых пользователей и ваш доход в разделе <b>Пользователи 👥</b> и <b>Баланс 💰</b>.\n\n"
        )

        await callback_query.message.answer_media_group(
            media=[
                InputMediaDocument(
                    media=font_logo_white,
                    caption=f"Логотип с надписью (белый)",
                ),
                InputMediaDocument(
                    media=font_logo_black,
                    caption=f"Логотип с надписью (черный)",
                ),
                InputMediaDocument(
                    media=logo_white,
                    caption=f"Логотип (белый)",
                ),
                InputMediaDocument(
                    media=logo_black,
                    caption=f"Логотип (черный)",
                ),
            ]
        )

        await callback_query.message.answer(
            text=text,
            parse_mode="HTML",
        )

        await state.set_state(current_state)
        await rediska.set_state(partner_bot_id, tg_id, current_state)

    except Exception as e:
        await log.info(f"Ошибка при генерации логотипа: {str(e)}")
        await callback_query.message.answer(f"Ошибка при генерации логотипа")


@partner_r.callback_query(F.data == "seed_key")
async def data_seed_key_svg(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Возвращает SVG SEED ключа"""

    current_state = PartnerState.default.state
    tg_id = callback_query.from_user.id
    seed_key = await partner_data.get_my_seed_key(tg_id)

    try:
        svg_white, svg_black = await seed_maker.get_seed_key_svg(seed_key=seed_key)

        # Преобразуем SVG-код в байты
        svg_white_bytes = svg_white.encode("utf-8")
        svg_black_bytes = svg_black.encode("utf-8")

        seed_file_white = BufferedInputFile(
            svg_white_bytes, filename="seed_key_white.svg"
        )
        seed_file_black = BufferedInputFile(
            svg_black_bytes, filename="seed_key_black.svg"
        )

        text = (
            "🔥 <b>Ваш SEED ключ</b>\n\n"
            "В формате .svg\n\n"
            "Отслеживайте количество привлечённых пользователей и ваш доход в разделе "
            "<b>Пользователи 👥</b> и <b>Баланс 💰</b>.\n\n"
        )

        await callback_query.message.answer_media_group(
            media=[
                InputMediaDocument(
                    media=seed_file_white, caption="SEED ключ (белый текст)"
                ),
                InputMediaDocument(
                    media=seed_file_black, caption="SEED ключ (чёрный текст)"
                ),
            ]
        )

        await callback_query.message.answer(
            text=text,
            parse_mode="HTML",
        )

        await state.set_state(current_state)
        await rediska.set_state(partner_bot_id, tg_id, current_state)

    except Exception as e:
        log.info(f"Ошибка при генерации SVG SEED ключа: {str(e)}")
        await callback_query.message.answer("Ошибка при генерации SVG SEED ключа")


# ---
# ---


@partner_r.callback_query(
    F.data == "get_partner_earn",
)
async def data_earn(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обрабатывает запрос на вывод заработанных денег."""

    await callback_query.answer("💰 Запрос на вывод", show_alert=False)

    current_state = PartnerState.default.state
    tg_id = callback_query.from_user.id

    balance = await partner_data.get_partner_balance(tg_id)

    if balance < 1000:
        text = (
            f"🚫 <b>Минимальная сумма вывода:</b> 1000₽\n\n"
            f"Ваш текущий баланс: <b>{balance}₽</b>\n\n"
            f"Приглашайте больше клиентов и курьеров, чтобы увеличить свой доход!\n\n"
        )
    else:
        text = (
            f"✅ Ваш запрос принят!\n\n"
            f"С вами свяжется наш менеджер для уточнения деталей.\n\n"
        )

    await callback_query.message.answer(
        text=text,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(partner_bot_id, tg_id, current_state)
