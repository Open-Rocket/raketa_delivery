from ._deps import (
    CommandStart,
    FSMContext,
    AdminState,
    ContentType,
    ReplyKeyboardRemove,
    filters,
    Message,
    CallbackQuery,
    OrderStatus,
    PreCheckoutQuery,
    LabeledPrice,
    zlib,
    Time,
    json,
    F,
    find_closest_city,
    admin_data,
    courier_bot_id,
    handler,
    courier_r,
    courier_fallback,
    courier_data,
    payment_r,
    kb,
    title,
    courier_bot_id,
    order_data,
    rediska,
    cities,
    payment_provider,
    log,
    courier_bot,
    customer_bot,
    admin_r,
    admin_fallback,
    admin_bot_id,
    admin_bot,
    SUPER_ADMIN_TG_ID,
)


# ---
# ---


@admin_r.message(
    CommandStart(),
)
async def cmd_start_admin(
    message: Message,
    state: FSMContext,
):
    """Обработчик команды /start для админа."""

    tg_id = message.from_user.id
    current_state = AdminState.default.state

    admin_status = "Super Admin" if tg_id == SUPER_ADMIN_TG_ID else "Admin"

    text = f"Вы вошли как <b>{admin_status}</b>.\n\n▼ <b>Выберите действие ...</b>"

    await message.answer(
        text=text,
        reply_markup=ReplyKeyboardRemove(),
        disable_notification=True,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.message(F.text == "/users")
@admin_r.callback_query(F.data == "refresh_users")
async def cmd_users(
    event: Message | CallbackQuery,
    state: FSMContext,
):
    """Обработчик команды /users и обновления списка пользователей."""

    tg_id = event.from_user.id
    current_state = AdminState.default.state

    customers, couriers, partners = await admin_data.get_all_users()

    text = (
        f"<b>👥 Пользователи</b>\n\n"
        f"Здесь вы можете посмотреть основную статистику по пользователям платформы.\n\n"
        f" - Всего пользователей: <b>{len(customers) + len(couriers)}</b>\n"
        f" - Клиентов: <b>{len(customers)}</b>\n"
        f" - Курьеров: <b>{len(couriers)}</b>\n"
        f" - Партнеров: <b>{len(partners)}</b>\n\n"
    )

    reply_kb = await kb.get_admin_kb("/users")

    state_data = await state.get_data()
    saved_text = state_data.get("message_text_users")
    saved_kb = state_data.get("message_kb_users")

    new_kb_json = json.dumps(reply_kb.model_dump())

    if isinstance(event, Message):
        await event.answer(
            text=text,
            reply_markup=reply_kb,
            parse_mode="HTML",
        )

    elif isinstance(event, CallbackQuery):

        await event.answer(
            text="🔄 Обновление пользователей...",
            show_alert=False,
        )

        if saved_text != text or saved_kb != new_kb_json:

            await event.message.edit_text(
                text=text,
                reply_markup=reply_kb,
                parse_mode="HTML",
            )

    await state.set_state(current_state)
    await state.update_data(message_text_users=text, message_kb_users=new_kb_json)
    await rediska.set_state(admin_bot_id, tg_id, current_state)
    await rediska.save_fsm_state(state, admin_bot_id, tg_id)


@admin_r.message(
    F.text == "/orders",
)
@admin_r.callback_query(F.data == "refresh_orders")
async def cmd_orders(
    event: Message | CallbackQuery,
    state: FSMContext,
):
    """Обработчик команды /orders для админа."""

    tg_id = event.from_user.id
    current_state = AdminState.default.state

    (
        all_orders,
        pending_orders,
        active_orders,
        completed_orders,
        canceled_orders,
    ) = await order_data.get_all_orders()

    text = (
        f"<b>📋 Заказы</b>\n\n"
        f"Здесь вы можете просмотреть текущую статистику по заказам на платформе.\n\n"
        f" - Всего заказов: <b>{len(all_orders)}</b>\n"
        f" - Ожидают курьера: <b>{len(pending_orders)}</b>\n"
        f" - Выполняются: <b>{len(active_orders)}</b>\n"
        f" - Завершенные: <b>{len(completed_orders)}</b>\n"
        f" - Отмененные: <b>{len(canceled_orders)}</b>\n\n"
    )

    reply_kb = await kb.get_admin_kb("/orders")

    state_data = await state.get_data()
    saved_text = state_data.get("message_text_orders")
    saved_kb = state_data.get("message_kb_orders")

    new_kb_json = json.dumps(reply_kb.model_dump())

    if isinstance(event, Message):
        await event.answer(
            text=text,
            reply_markup=reply_kb,
            parse_mode="HTML",
        )

    elif isinstance(event, CallbackQuery):

        await event.answer(
            text="🔄 Обновление заказов...",
            show_alert=False,
        )

        if saved_text != text or saved_kb != new_kb_json:

            await event.message.edit_text(
                text=text,
                reply_markup=reply_kb,
                parse_mode="HTML",
            )

    await state.set_state(current_state)
    await state.update_data(message_text_orders=text, message_kb_orders=new_kb_json)
    await rediska.set_state(admin_bot_id, tg_id, current_state)
    await rediska.save_fsm_state(state, admin_bot_id, tg_id)


@admin_r.message(
    F.text == "/admins",
)
async def cmd_admins(
    message: Message,
    state: FSMContext,
):
    """Обработчик команды /admins для админа."""

    tg_id = message.from_user.id
    current_state = AdminState.default.state

    admins = await admin_data.get_all_admins()
    admins_phone = [admin.phone for admin in admins]

    admins_text = "\n".join(
        f" - {i+1}. {phone}" for i, phone in enumerate(admins_phone)
    )

    text = (
        f"<b>👨‍💼 Администраторы</b>\n\n"
        f" - Всего администраторов: {len(admins)}\n"
        f"{admins_text if admins_text else ''}"
    )

    reply_kb = await kb.get_admin_kb("/admins")

    await message.answer(
        text=text,
        reply_markup=reply_kb,
        disable_notification=True,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.message(
    F.text == "/global",
)
@admin_r.callback_query(F.data == "refresh_global_data")
async def cmd_global(
    event: Message | CallbackQuery,
    state: FSMContext,
):
    """Обработчик команды /global для админа."""

    tg_id = event.from_user.id
    current_state = AdminState.default.state

    service_status = await admin_data.get_service_status()
    common_price, max_price = await admin_data.get_order_prices()
    subs_price = await admin_data.get_subscription_price() // 100
    discount_percent_courier = await admin_data.get_discount_percent_courier()
    discount_percent_first_order = await admin_data.get_first_order_discount()
    free_period_days = await admin_data.get_free_period_days()

    text = (
        f"<b>🌎 Глобальное управление сервисом</b>\n\n"
        f"Здесь вы можете управлять всеми настройками сервиса и получать актуальную информацию.\n\n"
        f"<b>⚙️ Сервис и Данные</b>\n"
        f" - Текущее состояние сервиса: <b>{'Активен' if service_status else 'На профилактике'}</b>\n\n"
        f"<b>💰 Цены и Тарифы</b>\n"
        f" - Стоимость подписки: <b>{subs_price}₽</b>\n"
        f" - Стандартная цена заказ за 1км: <b>{common_price}₽</b>\n"
        f" - Максимальная цена заказа за 1км: <b>{max_price}₽</b>\n\n"
        f"<b>🎉 Акции и Скидки %</b>\n"
        f" - Скидка на подписку курьеру: <b>{discount_percent_courier}%</b>\n"
        f" - Скидка на первый заказ: <b>{discount_percent_first_order}%</b>\n"
        f" - Бесплатный период: <b>{free_period_days} дней</b>\n\n"
        f"Выберите действие:\n"
    )
    reply_kb = await kb.get_admin_kb("/global")

    state_data = await state.get_data()
    saved_text = state_data.get("message_text_global")
    saved_kb = state_data.get("message_kb_global")

    new_kb_json = json.dumps(reply_kb.model_dump())

    if isinstance(event, Message):
        await event.answer(
            text=text,
            reply_markup=reply_kb,
            parse_mode="HTML",
        )

    elif isinstance(event, CallbackQuery):

        await event.answer(
            text="🔄 Обновление глобальных данных...",
            show_alert=False,
        )

        if saved_text != text or saved_kb != new_kb_json:

            await event.message.edit_text(
                text=text,
                reply_markup=reply_kb,
                parse_mode="HTML",
            )

    await state.set_state(current_state)
    await state.update_data(message_text_global=text, message_kb_global=new_kb_json)
    await rediska.set_state(admin_bot_id, tg_id, current_state)
    await rediska.save_fsm_state(state, admin_bot_id, tg_id)
