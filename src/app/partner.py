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
    admin_data,
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
    # is_reg = await rediska.is_reg(partner_bot_id, tg_id)
    seed_key = await partner_data.get_seed_key_by_partner_tg_id(tg_id=tg_id)
    new_message = None

    refund_percent = await admin_data.get_refund_percent()

    if seed_key:
        current_state = PartnerState.default.state
        await message.answer(
            text="▼ <b>Выберите действие в Меню ...</b>",
            disable_notification=True,
            parse_mode="HTML",
        )

    else:
        current_state = PartnerState.reg_state.state
        text = "Вам нужно сгенерировать ваш персональный SEED-ключ, чтобы начать работу с сервисом.\n\n"
        reply_kb = await kb.get_partner_kb("generate_seed")
        new_message = await message.answer_photo(
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
    F.data == "generate_seed_key",
)
async def partner_generate_seed(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обрабатывает генерацию seed ключа."""

    current_state = PartnerState.default.state
    tg_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id

    partner_id = await partner_data.get_partner_id_by_tg_id(tg_id)

    if partner_id:
        await callback_query.answer(
            text="Вы уже зарегистрированы в системе, вам не нужно повторно генерировать ключ.",
            show_alert=True,
        )
        return

    all_seed_keys = await partner_data.get_all_seed_keys()

    await callback_query.answer("🔑 Генерация ключа...", show_alert=False)

    try:

        user = callback_query.from_user

        username = user.username  # может быть None
        user_link = f"<a href='tg://user?id={tg_id}'>{username}</a>"

        partner_id = await partner_data.create_new_partner(tg_id)

        if partner_id:

            generate = True

            while generate:
                seed_key = await seed_maker.generate_seed()
                if seed_key not in all_seed_keys:
                    generate = False

            log.info(f"Generated unique seed key: {seed_key}")

            is_create = await partner_data.create_new_seed_key(partner_id, seed_key)
            refund_percent = await admin_data.get_refund_percent()

            seed_text = (
                f"🔑 <b>Ваш ключ:</b> <code>{seed_key}</code>  👈 <i>Нажмите</i>\n\n"
                f"- Этот ключ служит промокодом для пользователей. Используя его они получают скидки и могут участвовать в акциях сервиса.\n\n"
                f"- Для вас, как партнера, этот ключ важен тем, что мы отслеживаем, сколько людей зарегистрировались с вашим ключом. "
                f"Чем больше клиентов и курьеров, использующих ваш ключ, тем выше ваш доход, поскольку вы получаете <b>{refund_percent}%</b> с подписки курьеров каждый месяц.\n\n"
                f"▼ <b>Выберите действие в • ≡ Меню •</b>"
            )

            if is_create:

                new_message = await callback_query.message.answer(
                    text=seed_text,
                    disable_notification=True,
                    parse_mode="HTML",
                )

                await callback_query.message.delete()

                await state.set_state(current_state)
                await rediska.set_state(partner_bot_id, tg_id, current_state)

            else:
                new_message = await callback_query.answer(
                    text="<b>‼️ Произошла ошибка при создании ключа, попробуйте позже еще раз!</b>\n\n",
                    disable_notification=True,
                    show_alert=True,
                    parse_mode="HTML",
                )
                return

        else:
            new_message = await callback_query.message.answer(
                text="<b>‼️ Произошла ошибка при сохранении данных, попробуйте позже еще раз!</b>\n\n",
                disable_notification=True,
                parse_mode="HTML",
            )
            return

    except Exception as e:
        new_message = await callback_query.message.answer(
            text="<b>‼️ Произошла ошибка, попробуйте позже.</b>\n\n",
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


@partner_r.message(
    F.text == "/refs",
)
@partner_r.callback_query(
    F.data == "refresh_refs",
)
async def cmd_refs(
    event: Message | CallbackQuery,
    state: FSMContext,
):
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

    seed_key = await partner_data.get_my_seed_key(tg_id)
    refund_percent = await admin_data.get_refund_percent()

    text = (
        f"Приглашайте курьеров и клиентов, используя этот ключ. "
        f"За каждого привлеченного курьера вы будете получать <b>{refund_percent}%</b> от его подписки каждый месяц.\n\n"
        f"<b>🔑 Ваш ключ:</b> <code>{seed_key}</code>  👈 <i>Нажмите</i>"
    )

    await message.answer(
        text=text,
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


@partner_r.message(
    F.text == "/balance",
)
@partner_r.callback_query(
    F.data == "refresh_balance",
)
async def cmd_balance(
    event: Message | CallbackQuery,
    state: FSMContext,
):
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


@partner_r.message(
    F.text == "/support",
)
async def cmd_support(
    message: Message,
    state: FSMContext,
):
    """Обработчик команды /support."""

    current_state = PartnerState.default.state
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
    await rediska.set_state(partner_bot_id, tg_id, current_state)


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


@partner_r.callback_query(
    F.data == "business_card_courier",
)
@partner_r.callback_query(
    F.data == "business_card_customer",
)
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


@partner_r.callback_query(
    F.data == "buklet_courier",
)
@partner_r.callback_query(
    F.data == "buklet_customer",
)
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


@partner_r.callback_query(
    F.data == "QR_courier",
)
@partner_r.callback_query(
    F.data == "QR_customer",
)
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
            text=text,
            disable_web_page_preview=True,
            parse_mode="HTML",
        )

        await state.set_state(current_state)
        await rediska.set_state(partner_bot_id, tg_id, current_state)

    except Exception as e:
        await log.info(f"Ошибка при генерации QR-кода: {str(e)}")
        await callback_query.message.answer(f"Ошибка при генерации QR-кода")


@partner_r.callback_query(
    F.data == "logo",
)
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


@partner_r.callback_query(
    F.data == "seed_key",
)
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
    min_refund_amount = await partner_data.get_min_refund_amount()
    max_refund_amount = await partner_data.get_max_refund_amount()

    if balance >= min_refund_amount:
        if balance >= max_refund_amount:
            additional_message = f"<i>*Ваш баланс превышает максимальную сумму вывода.\nВозможна выплата в несколько этапов!</i>\n"
        else:
            additional_message = ""

        text = (
            f"✅ Ваш запрос принят!\n\n"
            f"С вами свяжется наш менеджер для уточнения деталей.\n\n"
            f"🔸 <b>Сумма вывода:</b> <b>{balance}₽</b>\n"
            f"<i>*Подготовьте номер своей банковской карты на которую нужно совершить перевод или номер телефона в случае с переводом через СПБ.\nВам будет переведена вся сумма на вашем балансе!</i>.\n\n"
            f"{additional_message}"
        )

        user = callback_query.from_user

        username = user.username
        user_link = (
            f"<a href='tg://user?id={tg_id}'>{username if username else tg_id}</a>"
        )

        await partner_data.create_new_earn_request(tg_id, user_link, balance)

    else:
        text = (
            f"🚫 <b>Минимальная сумма вывода: {min_refund_amount}₽</b>\n\n"
            f"Ваш текущий баланс: <b>{balance}₽</b>\n\n"
            f"Приглашайте больше клиентов и курьеров, чтобы увеличить свой доход!\n\n"
        )

    await callback_query.message.answer(
        text=text,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(partner_bot_id, tg_id, current_state)


@partner_r.message()
async def handle_unrecognized_message(
    message: Message,
):
    """Обрабатывает нераспознанные сообщения."""

    await message.delete()
