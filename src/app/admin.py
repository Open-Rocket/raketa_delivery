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
    StateFilter,
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

    all_users = len(customers) + len(couriers) + len(partners)

    text = (
        f"<b>👥 Пользователи</b>\n\n"
        f"Здесь вы можете посмотреть основную статистику по пользователям платформы.\n\n"
        f" - Всего пользователей: <b>{all_users}</b>\n"
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

    if tg_id != SUPER_ADMIN_TG_ID:
        await message.answer(
            text="❌ У вас нет доступа к этой команде.",
        )

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
@admin_r.callback_query(
    F.data == "refresh_global_data",
)
@admin_r.callback_query(
    F.data == "back_global_data",
)
async def cmd_global(
    event: Message | CallbackQuery,
    state: FSMContext,
):
    """Обработчик команды /global для админа."""

    tg_id = event.from_user.id
    current_state = AdminState.default.state

    if tg_id != SUPER_ADMIN_TG_ID:
        await event.answer(
            text="❌ У вас нет доступа к этой команде.",
        )
        return

    service_status = await admin_data.get_service_status()
    partner_program_status = await admin_data.get_partner_program_status()
    common_price, max_price = await admin_data.get_order_prices()
    subs_price = await admin_data.get_subscription_price() // 100
    discount_percent_courier = await admin_data.get_discount_percent_courier()
    discount_percent_first_order = await admin_data.get_first_order_discount()
    free_period_days = await admin_data.get_free_period_days()
    customers, couriers, partners = await admin_data.get_all_users()

    customers = len([c.customer_id for c in customers])
    couriers = len([c.courier_id for c in couriers])
    partners = len([p.partner_id for p in partners])
    all_users = customers + couriers + partners

    profit = await admin_data.get_profit()
    turnover = await admin_data.get_turnover()
    (
        pending_orders,
        active_orders,
        completed_orders,
        canceled_orders,
    ) = await order_data.get_all_orders()

    pending_orders = len(pending_orders)
    active_orders = len(active_orders)
    completed_orders = len(completed_orders)
    canceled_orders = len(canceled_orders)
    all_orders = pending_orders + active_orders + completed_orders + canceled_orders

    coefficient_less_5km = await admin_data.get_distance_coefficient_less_5()
    coefficient_5_10_km = await admin_data.get_distance_coefficient_5_10()
    coefficient_10_20_km = await admin_data.get_distance_coefficient_10_20()
    coefficient_more_20_km = await admin_data.get_distance_coefficient_more_20()

    coefficient_00_06 = await admin_data.get_time_coefficient_00_06()
    coefficient_06_12 = await admin_data.get_time_coefficient_06_12()
    coefficient_12_18 = await admin_data.get_time_coefficient_12_18()
    coefficient_18_21 = await admin_data.get_time_coefficient_18_21()
    coefficient_21_00 = await admin_data.get_time_coefficient_21_00()

    coefficient_big_cities = await admin_data.get_big_cities_coefficient()
    coefficient_other_cities = await admin_data.get_small_cities_coefficient()

    refund_percent = await admin_data.get_refund_percent()

    fastest_order_ever = await order_data.get_fastest_order_ever()

    log.info(f"fastest_order_ever: {fastest_order_ever}")

    fastest_order_ever_speed = (
        fastest_order_ever.speed_kmh if fastest_order_ever else "..."
    )

    global_state_data = {
        "common_price": common_price,
        "max_price": max_price,
        "subs_price": subs_price,
        "discount_percent_courier": discount_percent_courier,
        "discount_percent_first_order": discount_percent_first_order,
        "free_period_days": free_period_days,
        "coefficient_less_5km": coefficient_less_5km,
        "coefficient_5_10_km": coefficient_5_10_km,
        "coefficient_10_20_km": coefficient_10_20_km,
        "coefficient_more_20_km": coefficient_more_20_km,
        "coefficient_00_06": coefficient_00_06,
        "coefficient_06_12": coefficient_06_12,
        "coefficient_12_18": coefficient_12_18,
        "coefficient_18_21": coefficient_18_21,
        "coefficient_21_00": coefficient_21_00,
        "coefficient_big_cities": coefficient_big_cities,
        "coefficient_other_cities": coefficient_other_cities,
        "refund_percent": refund_percent,
        "profit": profit,
        "turnover": turnover,
        "all_users": all_users,
        "customers": customers,
        "couriers": couriers,
        "partners": partners,
        "all_orders": all_orders,
        "pending_orders": pending_orders,
        "active_orders": active_orders,
        "completed_orders": completed_orders,
        "canceled_orders": canceled_orders,
    }

    text = (
        f"<b>🌎 Глобальное управление сервисом</b>\n\n"
        f"Здесь вы можете управлять всеми настройками сервиса и получать актуальную информацию.\n\n"
        f"<b>⚙️ Сервис и Данные</b>\n"
        f" ▸ Сервис: <b>{'ON ✅' if service_status else 'OFF ❌'}</b>\n"
        f" ▸ Партнерская программа: <b>{'ON ✅' if partner_program_status else 'OFF ❌'}</b>\n"
        f" •\n"
        f" ▸ Пользователей: <b>{all_users}</b>\n"
        f" ▸ Заказов: <b>{all_orders}</b>\n"
        f" ▸ Оборот: <b>{turnover}₽</b>\n"
        f" ▸ Прибыль: <b>{profit}₽</b>\n\n"
        f"🏆 <b>Рекорды</b>\n"
        f"  ▸ Самый быстрый заказ: {fastest_order_ever_speed} км/ч\n\n"
        f"💰 <b>Цены и Тарифы</b>\n"
        f" ▸ Стоимость подписки: <b>{subs_price}₽</b>\n"
        f" ▸ Стандартная цена заказ за 1км: <b>{common_price}₽</b>\n"
        f" ▸ Максимальная цена заказа за 1км: <b>{max_price}₽</b>\n"
        f" •\n"
        f" ▸ Коэффициент 0 - 5 км: <b>{coefficient_less_5km}</b>\n"
        f" ▸ Коэффициент 5 - 10 км: <b>{coefficient_5_10_km}</b>\n"
        f" ▸ Коэффициент 10 - 20 км: <b>{coefficient_10_20_km}</b>\n"
        f" ▸ Коэффициент 20+ км: <b>{coefficient_more_20_km}</b>\n"
        f" •\n"
        f" ▸ Коэффициент 00 - 06: <b>{coefficient_00_06}</b>\n"
        f" ▸ Коэффициент 06 - 12: <b>{coefficient_06_12}</b>\n"
        f" ▸ Коэффициент 12 - 18: <b>{coefficient_12_18}</b>\n"
        f" ▸ Коэффициент 18 - 21: <b>{coefficient_18_21}</b>\n"
        f" ▸ Коэффициент 21 - 00: <b>{coefficient_21_00}</b>\n"
        f" •\n"
        f" ▸ Коэффициент в больших городах: <b>{coefficient_big_cities}</b>\n"
        f" ▸ Коэффициент в остальных городах: <b>{coefficient_other_cities}</b>\n\n"
        f"🎉 <b>Акции и Скидки %</b>\n"
        f" ▸ Скидка на подписку курьеру: <b>{discount_percent_courier}%</b>\n"
        f" ▸ Скидка на первый заказ: <b>{discount_percent_first_order}%</b>\n"
        f" ▸ Бесплатный период: <b>{free_period_days} дней</b>\n"
        f" •\n"
        f" ▸ Партнерский процент: <b>{refund_percent}%</b>\n\n"
        f"<b>Выберите действие:</b>\n"
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

        if event.data == "back_global_data":
            await event.answer(
                text="↩️ Назад",
                show_alert=False,
            )

            await event.message.edit_text(
                text=text,
                reply_markup=reply_kb,
                parse_mode="HTML",
            )

        elif event.data == "refresh_global_data":
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
    await state.update_data(
        message_text_global=text,
        message_kb_global=new_kb_json,
        global_state_data=global_state_data,
    )
    await rediska.set_state(admin_bot_id, tg_id, current_state)
    await rediska.save_fsm_state(state, admin_bot_id, tg_id)


# ---
# ---
# ---


@admin_r.callback_query(F.data == "service_data")
async def data_service_data(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик кнопки "Сервисные данные" для админа."""

    await callback_query.answer(
        text="⚙️ Сервис и Данные",
        show_alert=False,
    )

    tg_id = callback_query.from_user.id
    current_state = AdminState.default.state

    service_status = await admin_data.get_service_status()
    partner_program_status = await admin_data.get_partner_program_status()

    data = await state.get_data()
    global_state_data: dict = data.get("global_state_data")
    all_users = global_state_data.get("all_users")
    profit = global_state_data.get("profit")
    turnover = global_state_data.get("turnover")
    customers = global_state_data.get("customers")
    couriers = global_state_data.get("couriers")
    partners = global_state_data.get("partners")
    all_orders = global_state_data.get("all_orders")
    pending_orders = global_state_data.get("pending_orders")
    active_orders = global_state_data.get("active_orders")
    completed_orders = global_state_data.get("completed_orders")
    canceled_orders = global_state_data.get("canceled_orders")

    text = (
        f"<b>⚙️ Сервис и Данные</b>\n\n"
        f" ▸ Сервис: <b>{'ON ✅' if service_status else 'OFF ❌'}</b>\n"
        f" ▸ Партнерская программа: <b>{'ON ✅' if partner_program_status else 'OFF ❌'}</b>\n"
        f" •\n"
        f" ▸ Пользователей: <b>{all_users}</b>\n"
        f"   ‣ Клиентов: <b>{customers}</b>\n"
        f"   ‣ Курьеров: <b>{couriers}</b>\n"
        f"   ‣ Партнеров: <b>{partners}</b>\n"
        f" ▸ Заказов: <b>{all_orders}</b>\n"
        f"   ‣ Ожидают курьера: <b>{pending_orders}</b>\n"
        f"   ‣ Выполняются: <b>{active_orders}</b>\n"
        f"   ‣ Завершенные: <b>{completed_orders}</b>\n"
        f"   ‣ Отмененные: <b>{canceled_orders}</b>\n"
        f" ▸ Оборот: <b>{turnover}₽</b>\n"
        f" ▸ Прибыль: <b>{profit}₽</b>\n"
    )

    log.info(f"service_status_1: {service_status}")

    reply_kb = await kb.get_turn_status_kb(
        key="service_and_data",
        status=not service_status,
    )

    await callback_query.message.edit_text(
        text=text,
        reply_markup=reply_kb,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.callback_query(F.data == "turn_on_service")
@admin_r.callback_query(F.data == "turn_off_service")
async def data_status_service(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик кнопки "Включить/Выключить сервис" для админа."""

    tg_id = callback_query.from_user.id
    current_state = AdminState.default.state

    service_status = await admin_data.get_service_status()

    if callback_query.data == "turn_on_service":
        await admin_data.change_service_status(status=True)
        await callback_query.message.answer(
            text=f"✅ Сервис включен! \n\n",
        )

    elif callback_query.data == "turn_off_service":
        await admin_data.change_service_status(status=False)

        await callback_query.message.answer(
            text=f"❌ Сервис выключен!",
        )

    service_status = await admin_data.get_service_status()
    log.info(f"service_status_2: {service_status}")

    await callback_query.message.delete()

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.callback_query(F.data == "turn_on_partner")
@admin_r.callback_query(F.data == "turn_off_partner")
async def data_status_service(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик кнопки "Включить/Выключить партнерки" для админа."""

    tg_id = callback_query.from_user.id
    current_state = AdminState.default.state

    partner_program_status = await admin_data.get_partner_program_status()

    if callback_query.data == "turn_on_partner":
        await admin_data.change_partner_program(status=True)
        await callback_query.message.answer(
            text=f"✅ Партнерская программа включена! \n\n",
        )
    elif callback_query.data == "turn_off_partner":
        await admin_data.change_partner_program(status=False)
        await callback_query.message.answer(
            text=f"❌ Партнерская программа выключена!",
        )
    partner_program_status = await admin_data.get_partner_program_status()
    log.info(f"partner_program_status: {partner_program_status}")
    await callback_query.message.delete()
    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


# ---
# ---


@admin_r.callback_query(F.data == "prices_and_tariffs")
async def data_prices_and_tariffs(callback_query: CallbackQuery, state: FSMContext):
    """Обработчик кнопки "Цены и Тарифы" для админа."""

    await callback_query.answer(
        text="💰 Цены и Тарифы",
        show_alert=False,
    )

    tg_id = callback_query.from_user.id
    current_state = AdminState.default.state

    data = await state.get_data()
    global_state_data: dict = data.get("global_state_data")
    common_price = global_state_data.get("common_price")
    max_price = global_state_data.get("max_price")
    subs_price = global_state_data.get("subs_price")
    coefficient_less_5km = global_state_data.get("coefficient_less_5km")
    coefficient_5_10_km = global_state_data.get("coefficient_5_10_km")
    coefficient_10_20_km = global_state_data.get("coefficient_10_20_km")
    coefficient_more_20_km = global_state_data.get("coefficient_more_20_km")
    coefficient_00_06 = global_state_data.get("coefficient_00_06")
    coefficient_06_12 = global_state_data.get("coefficient_06_12")
    coefficient_12_18 = global_state_data.get("coefficient_12_18")
    coefficient_18_21 = global_state_data.get("coefficient_18_21")
    coefficient_21_00 = global_state_data.get("coefficient_21_00")
    coefficient_big_cities = global_state_data.get("coefficient_big_cities")
    coefficient_other_cities = global_state_data.get("coefficient_other_cities")

    text = (
        f"<b>💰 Цены и Тарифы</b>\n\n"
        f" ▸ Стоимость подписки: <b>{subs_price}₽</b>\n"
        f" ▸ Стандартная цена заказ за 1км: <b>{common_price}₽</b>\n"
        f" ▸ Максимальная цена заказа за 1км: <b>{max_price}₽</b>\n"
        f" •\n"
        f" ▸ Коэффициент 0 - 5 км: <b>{coefficient_less_5km}</b>\n"
        f" ▸ Коэффициент 5 - 10 км: <b>{coefficient_5_10_km}</b>\n"
        f" ▸ Коэффициент 10 - 20 км: <b>{coefficient_10_20_km}</b>\n"
        f" ▸ Коэффициент 20+ км: <b>{coefficient_more_20_km}</b>\n"
        f" •\n"
        f" ▸ Коэффициент 00 - 06: <b>{coefficient_00_06}</b>\n"
        f" ▸ Коэффициент 06 - 12: <b>{coefficient_06_12}</b>\n"
        f" ▸ Коэффициент 12 - 18: <b>{coefficient_12_18}</b>\n"
        f" ▸ Коэффициент 18 - 21: <b>{coefficient_18_21}</b>\n"
        f" ▸ Коэффициент 21 - 00: <b>{coefficient_21_00}</b>\n"
        f" •\n"
        f" ▸ Коэффициент в больших городах: <b>{coefficient_big_cities}</b>\n"
        f" ▸ Коэффициент в остальных городах: <b>{coefficient_other_cities}</b>\n\n"
    )

    reply_kb = await kb.get_admin_kb("prices_and_tariffs")

    await callback_query.message.edit_text(
        text=text,
        reply_markup=reply_kb,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.callback_query(
    F.data.in_(
        [
            "subscription_price",
            "standard_order_price",
            "max_order_price",
            "distance_coefficient_less_5",
            "distance_coefficient_5_10",
            "distance_coefficient_10_20",
            "distance_coefficient_more_20",
            "time_coefficient_00_06",
            "time_coefficient_06_12",
            "time_coefficient_12_18",
            "time_coefficient_18_21",
            "time_coefficient_21_00",
            "big_cities_coefficient",
            "small_cities_coefficient",
        ]
    )
)
async def data_change_price(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик кнопки "Изменить цену" для админа."""

    match callback_query.data:
        case "subscription_price":
            current_state = AdminState.change_subscription_price.state
            text = "Введите новую цену подписки :"
        case "standard_order_price":
            current_state = AdminState.change_standard_order_price.state
            text = "Введите новую цену за 1 км:"
        case "max_order_price":
            current_state = AdminState.change_max_order_price.state
            text = "Введите новую максимальную цену за 1 км:"
        case "distance_coefficient_less_5":
            current_state = AdminState.change_distance_coefficient_less_5.state
            text = "Введите новый коэффициент для расстояния 0 - 5 км:"
        case "distance_coefficient_5_10":
            current_state = AdminState.change_distance_coefficient_5_10.state
            text = "Введите новый коэффициент для расстояния 5 - 10 км:"
        case "distance_coefficient_10_20":
            current_state = AdminState.change_distance_coefficient_10_20.state
            text = "Введите новый коэффициент для расстояния 10 - 20 км:"
        case "distance_coefficient_more_20":
            current_state = AdminState.change_distance_coefficient_more_20.state
            text = "Введите новый коэффициент для расстояния 20+ км:"
        case "time_coefficient_00_06":
            current_state = AdminState.change_time_coefficient_00_06.state
            text = "Введите новый коэффициент для времени 00 - 06:"
        case "time_coefficient_06_12":
            current_state = AdminState.change_time_coefficient_06_12.state
            text = "Введите новый коэффициент для времени 06 - 12:"
        case "time_coefficient_12_18":
            current_state = AdminState.change_time_coefficient_12_18.state
            text = "Введите новый коэффициент для времени 12 - 18:"
        case "time_coefficient_18_21":
            current_state = AdminState.change_time_coefficient_18_21.state
            text = "Введите новый коэффициент для времени 18 - 21:"
        case "time_coefficient_21_00":
            current_state = AdminState.change_time_coefficient_21_00.state
            text = "Введите новый коэффициент для времени 21 - 00:"
        case "big_cities_coefficient":
            current_state = AdminState.change_big_cities_coefficient.state
            text = "Введите новый коэффициент для больших городов:"
        case "small_cities_coefficient":
            current_state = AdminState.change_small_cities_coefficient.state
            text = "Введите новый коэффициент для остальных городов:"
        case _:
            await callback_query.answer(
                "❌ Ошибка! Неизвестная команда.", show_alert=True
            )
            return

    await callback_query.message.delete()

    log.info(f"current_state:, {current_state}")

    tg_id = callback_query.from_user.id
    await callback_query.message.answer(text)
    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.message(
    StateFilter(
        AdminState.change_subscription_price,
        AdminState.change_standard_order_price,
        AdminState.change_max_order_price,
        AdminState.change_distance_coefficient_less_5,
        AdminState.change_distance_coefficient_5_10,
        AdminState.change_distance_coefficient_10_20,
        AdminState.change_distance_coefficient_more_20,
        AdminState.change_time_coefficient_00_06,
        AdminState.change_time_coefficient_06_12,
        AdminState.change_time_coefficient_12_18,
        AdminState.change_time_coefficient_18_21,
        AdminState.change_time_coefficient_21_00,
        AdminState.change_big_cities_coefficient,
        AdminState.change_small_cities_coefficient,
    )
)
async def change_prices_filer(
    message: Message,
    state: FSMContext,
):
    """Обработчик изменения цен и коэффициентов для админа."""

    new_value = message.text

    if isinstance(new_value, str):
        if new_value.isdigit():
            new_value = float(new_value)
        else:
            await message.answer(
                text="❌ Ошибка! Введите корректное значение.",
            )
            return

    current_state = await state.get_state()

    match current_state:
        case AdminState.change_subscription_price.state:
            await admin_data.change_subscription_price(int(new_value))
            text = f"✅ Новая цена подписки: {int(new_value)}₽"

        case AdminState.change_standard_order_price.state:
            await admin_data.change_standard_order_price(int(new_value))
            text = f"✅ Новая цена за 1 км: {int(new_value)}₽"

        case AdminState.change_max_order_price.state:
            await admin_data.change_max_order_price(int(new_value))
            text = f"✅ Новая максимальная цена за 1 км: {int(new_value)}₽"

        case AdminState.change_distance_coefficient_less_5.state:
            await admin_data.change_distance_coefficient_less_5(new_value)
            text = f"✅ Новый коэффициент для расстояния 0 - 5 км: {new_value}"

        case AdminState.change_distance_coefficient_5_10.state:
            await admin_data.change_distance_coefficient_5_10(new_value)
            text = f"✅ Новый коэффициент для расстояния 5 - 10 км: {new_value}"

        case AdminState.change_distance_coefficient_10_20.state:
            await admin_data.change_distance_coefficient_10_20(new_value)
            text = f"✅ Новый коэффициент для расстояния 10 - 20 км: {new_value}"

        case AdminState.change_distance_coefficient_more_20.state:
            await admin_data.change_distance_coefficient_more_20(new_value)
            text = f"✅ Новый коэффициент для расстояния 20+ км: {new_value}"

        case AdminState.change_time_coefficient_00_06.state:
            await admin_data.change_time_coefficient_00_06(new_value)
            text = f"✅ Новый коэффициент для времени 00 - 06: {new_value}"

        case AdminState.change_time_coefficient_06_12.state:
            await admin_data.change_time_coefficient_06_12(new_value)
            text = f"✅ Новый коэффициент для времени 06 - 12: {new_value}"

        case AdminState.change_time_coefficient_12_18.state:
            await admin_data.change_time_coefficient_12_18(new_value)
            text = f"✅ Новый коэффициент для времени 12 - 18: {new_value}"

        case AdminState.change_time_coefficient_18_21.state:
            await admin_data.change_time_coefficient_18_21(new_value)
            text = f"✅ Новый коэффициент для времени 18 - 21: {new_value}"

        case AdminState.change_time_coefficient_21_00.state:
            await admin_data.change_time_coefficient_21_00(new_value)
            text = f"✅ Новый коэффициент для времени 21 - 00: {new_value}"

        case AdminState.change_big_cities_coefficient.state:
            await admin_data.change_big_cities_coefficient(new_value)
            text = f"✅ Новый коэффициент для больших городов: {new_value}"

        case AdminState.change_small_cities_coefficient.state:
            await admin_data.change_small_cities_coefficient(new_value)
            text = f"✅ Новый коэффициент для остальных городов: {new_value}"

        case _:
            await message.answer(
                text="❌ Ошибка! Неизвестная команда.",
            )
            return

    tg_id = message.from_user.id
    current_state = AdminState.default.state

    await message.answer(text=text)

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.callback_query(F.data == "discounts_and_promotions")
async def data_discounts_and_promotions(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик кнопки "Акции и Скидки %" для админа."""

    await callback_query.answer(
        text="🎉 Акции и Скидки %",
        show_alert=False,
    )

    tg_id = callback_query.from_user.id
    current_state = AdminState.default.state

    data = await state.get_data()
    global_state_data: dict = data.get("global_state_data")
    discount_percent_courier = global_state_data.get("discount_percent_courier")
    discount_percent_first_order = global_state_data.get("discount_percent_first_order")
    free_period_days = global_state_data.get("free_period_days")
    refund_percent = global_state_data.get("refund_percent")

    text = (
        f"<b>🎉 Акции и Скидки %</b>\n\n"
        f" ▸ Скидка на подписку курьеру: <b>{discount_percent_courier}%</b>\n"
        f" ▸ Скидка на первый заказ: <b>{discount_percent_first_order}%</b>\n"
        f" ▸ Бесплатный период: <b>{free_period_days} дней</b>\n"
        f" •\n"
        f" ▸ Партнерский процент: <b>{refund_percent}%</b>\n"
    )

    reply_kb = await kb.get_admin_kb("discounts_and_promotions")

    await callback_query.message.edit_text(
        text=text,
        reply_markup=reply_kb,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.callback_query(
    F.data.in_(
        [
            "change_subscription_discount",
            "change_first_order_discount",
            "change_free_period",
            "change_refund_percent",
        ]
    )
)
async def data_change_discount_and_promotions(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик кнопки "Изменить скидку" для админа."""

    match callback_query.data:
        case "change_subscription_discount":
            current_state = AdminState.change_subscription_discount.state
            text = "Введите новую скидку на подписку курьеру (%):"
        case "change_first_order_discount":
            current_state = AdminState.change_first_order_discount.state
            text = "Введите новую скидку на первый заказ (%):"
        case "change_free_period":
            current_state = AdminState.change_free_period.state
            text = "Введите новый бесплатный период (дней):"
        case "change_refund_percent":
            current_state = AdminState.change_refund_percent.state
            text = "Введите новый партнерский процент (%):"
        case _:
            await callback_query.answer(
                "❌ Ошибка! Неизвестная команда.", show_alert=True
            )
            return

    await callback_query.message.delete()

    log.info(f"current_state:, {current_state}")

    tg_id = callback_query.from_user.id
    await callback_query.message.answer(text)
    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.message(
    StateFilter(
        AdminState.change_subscription_discount,
        AdminState.change_first_order_discount,
        AdminState.change_free_period,
        AdminState.change_refund_percent,
    )
)
async def change_discount_and_promotions(
    message: Message,
    state: FSMContext,
):
    """Обработчик изменения скидок и акций для админа."""

    new_value = message.text

    if isinstance(new_value, str):
        if new_value.isdigit():
            new_value = int(new_value)
        else:
            await message.answer(
                text="❌ Ошибка! Введите корректное значение.",
            )
            return

    current_state = await state.get_state()

    match current_state:
        case AdminState.change_subscription_discount.state:

            if new_value > 75:
                new_value = 75
            elif new_value < 0:
                new_value = 0

            await admin_data.change_discount_percent_courier(new_value)
            text = f"✅ Новая скидка на подписку курьеру: {new_value}%"

        case AdminState.change_first_order_discount.state:

            if new_value > 75:
                new_value = 75
            elif new_value < 0:
                new_value = 0

            await admin_data.change_first_order_discount(new_value)
            text = f"✅ Новая скидка на первый заказ: {new_value}%"

        case AdminState.change_free_period.state:

            if new_value > 30:
                new_value = 30
            elif new_value < 0:
                new_value = 0

            await admin_data.change_free_period_days(new_value)
            text = f"✅ Новый бесплатный период: {new_value} дней"

        case AdminState.change_refund_percent.state:

            if new_value > 50:
                new_value = 50
            elif new_value < 10:
                new_value = 10

            await admin_data.change_refund_percent(new_value)
            text = f"✅ Новый партнерский процент: {new_value}%"

        case _:
            await message.answer(
                text="❌ Ошибка! Неизвестная команда.",
            )
            return

    tg_id = message.from_user.id
    current_state = AdminState.default.state

    await message.answer(text=text)

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)
