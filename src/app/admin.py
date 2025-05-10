from ._deps import (
    CommandStart,
    FSMContext,
    AdminState,
    datetime,
    ReplyKeyboardRemove,
    Message,
    CallbackQuery,
    StateFilter,
    json,
    relativedelta,
    BufferedInputFile,
    filters,
    Dispatcher,
    Update,
    SUPER_ADMIN_TG_ID,
    F,
    pdf_creator,
    admin_data,
    kb,
    order_data,
    rediska,
    log,
    admin_r,
    admin_bot,
    customer_bot,
    courier_bot,
    partner_bot,
    admin_bot_id,
    partner_data,
    courier_data,
    customer_data,
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

    all_admins = await admin_data.get_all_admins()

    if tg_id == SUPER_ADMIN_TG_ID or tg_id in [
        admin.admin_tg_id for admin in all_admins
    ]:
        current_state = AdminState.default.state
        admin_status = "Super Admin" if tg_id == SUPER_ADMIN_TG_ID else "Admin"
        text = f"Вы <b>{admin_status}</b>.\n\n▼ <b>Выберите действие ...</b>"
        await message.answer(
            text=text,
            reply_markup=ReplyKeyboardRemove(),
            disable_notification=True,
            parse_mode="HTML",
        )

    else:
        current_state = AdminState.reg_adminPhone.state

        text = "Отправьте свой номер телефона для проверки вашего статуса."
        reply_kb = await kb.get_admin_kb("phone_kb")
        await message.answer(
            text=text,
            reply_markup=reply_kb,
            disable_notification=True,
        )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.message(
    filters.StateFilter(AdminState.reg_adminPhone),
)
async def reg_admin_phone(
    message: Message,
    state: FSMContext,
):
    """Обработчик ввода номера телефона для админа."""

    tg_id = message.from_user.id
    current_state = AdminState.default.state

    if not message.contact or message.contact.user_id != tg_id:
        await message.answer(
            '❗️Пожалуйста, нажмите кнопку "Отправить мой номер", а не пересылайте чужой контакт.',
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.set_state(current_state)
        await rediska.set_state(admin_bot_id, tg_id, current_state)
        return

    phone = message.contact.phone_number
    str_phone = "+" + str(phone)

    all_admins = await admin_data.get_all_admins()

    log.info(f"phone: {phone}")
    log.info(f"pho_db: {[admin.admin_phone for admin in all_admins]}")

    if "+" + str(phone) in [admin.admin_phone for admin in all_admins]:

        _ = await admin_data.reg_admin_tg_id(tg_id=tg_id, phone=str_phone)

        text = "✅ Доступ разрешен!\nПодтвердите ваш вход в систему."

        await message.answer(
            text="👍",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="HTML",
        )
        await message.answer(
            text=text,
            parse_mode="HTML",
        )
    else:
        text = "❌ Вы не являетесь администратором!"
        await message.answer(
            text=text,
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="HTML",
        )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


# --- Пользователи


@admin_r.message(
    F.text == "/users",
)
@admin_r.callback_query(
    F.data == "refresh_users",
)
@admin_r.callback_query(
    F.data == "back_to_users",
)
async def cmd_users(
    event: Message | CallbackQuery,
    state: FSMContext,
):
    """Обработчик команды /users и обновления списка пользователей."""

    tg_id = event.from_user.id
    data = await state.get_data()

    all_admins = await admin_data.get_all_admins()

    if tg_id != SUPER_ADMIN_TG_ID and tg_id not in [
        admin.admin_tg_id for admin in all_admins
    ]:
        await event.answer(
            text="❌ У вас нет доступа к этой команде.",
        )
        return

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
        users_msg = await event.answer(
            text=text,
            reply_markup=reply_kb,
            parse_mode="HTML",
        )

        try:
            users_msg_id = data.get("users_msg_id")
            if users_msg_id:
                await event.bot.delete_message(
                    chat_id=tg_id,
                    message_id=users_msg_id,
                )
                await state.update_data(users_msg_id=None)
                await rediska.save_fsm_state(state, admin_bot_id, tg_id)
                await event.delete()
        except Exception as e:
            log.warning(f"Не удалось удалить сообщение: {e}")

        await state.update_data(users_msg_id=users_msg.message_id)

    elif isinstance(event, CallbackQuery):

        if event.data == "refresh_users":
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

        if event.data == "back_to_users":
            await event.answer(
                text="↩️ Назад",
                show_alert=False,
            )

            await event.message.edit_text(
                text=text,
                reply_markup=reply_kb,
                parse_mode="HTML",
            )

    await state.set_state(current_state)
    await state.update_data(message_text_users=text, message_kb_users=new_kb_json)
    await rediska.set_state(admin_bot_id, tg_id, current_state)
    await rediska.save_fsm_state(state, admin_bot_id, tg_id)


# ---


@admin_r.callback_query(
    F.data == "choose_user",
)
async def data_user(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обрабатывает нажатие на кнопку Клиенты"""

    await callback_query.answer(
        text="👫 Клиенты",
        show_alert=False,
    )

    tg_id = callback_query.from_user.id
    current_state = AdminState.default.state

    text = (
        f"<b>👫 Клиенты</b>\n\n"
        f"Вы можете выбрать конкретного клиента по его id в базе или сделать рассылку всем клиентам сервиса"
    )

    reply_kb = await kb.get_admin_kb("choose_user")

    await callback_query.message.edit_text(
        text=text,
        reply_markup=reply_kb,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.callback_query(
    F.data == "choose_courier",
)
async def data_courier(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обрабатывает нажатие на кнопку Курьера"""

    await callback_query.answer(
        text="🥷 Курьеры",
        show_alert=False,
    )

    tg_id = callback_query.from_user.id
    current_state = AdminState.default.state

    text = (
        f"<b>🥷 Курьеры</b>\n\n"
        f"Вы можете выбрать конкретного курьера по его id в базе или сделать рассылку всем курьерам сервиса"
    )

    reply_kb = await kb.get_admin_kb("choose_courier")

    await callback_query.message.edit_text(
        text=text,
        reply_markup=reply_kb,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.callback_query(
    F.data == "choose_partner",
)
async def data_partner(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обрабатывает нажатие на кнопку Курьера"""

    await callback_query.answer(
        text="🤝 Партнеры",
        show_alert=False,
    )

    tg_id = callback_query.from_user.id
    current_state = AdminState.default.state

    text = (
        f"<b>🤝 Партнеры</b>\n\n"
        f"Вы можете выбрать конкретного партнера по его SEED или сделать рассылку всем партнерам сервиса"
    )

    reply_kb = await kb.get_admin_kb("choose_partner")

    await callback_query.message.edit_text(
        text=text,
        reply_markup=reply_kb,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


# ---


@admin_r.callback_query(
    F.data == "choose_user_by_ID",
)
async def call_choose_user_by_ID(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обрабатывает нажатие на кнопку выбрать пользователя по его ID"""

    tg_id = callback_query.from_user.id
    current_state = AdminState.choose_user_by_ID.state

    await callback_query.message.answer(
        text="Введите ID клиента:",
        disable_notification=True,
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.callback_query(
    F.data == "choose_courier_by_ID",
)
async def call_choose_courier_by_ID(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обрабатывает нажатие на кнопку выбрать курьера по его ID"""

    tg_id = callback_query.from_user.id
    current_state = AdminState.choose_courier_by_ID.state

    await callback_query.message.answer(
        text="Введите ID курьера:",
        disable_notification=True,
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.callback_query(
    F.data == "choose_partner_by_SEED",
)
async def call_choose_partner_by_SEED(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обрабатывает нажатие на кнопку выбрать партнера по его SEED"""

    tg_id = callback_query.from_user.id
    current_state = AdminState.choose_partner_by_SEED.state

    await callback_query.message.answer(
        text="Введите SEED партнера:",
        disable_notification=True,
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


# ---


@admin_r.callback_query(
    F.data.in_(
        [
            "mailing_users",
            "mailing_couriers",
            "mailing_partners",
        ],
    )
)
async def call_mailing(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обрабатывает нажатие на кнопку рассылки для клиентов"""

    tg_id = callback_query.from_user.id

    match callback_query.data:
        case "mailing_users":
            current_state = AdminState.mailing_users.state
            text = (
                f"<b>Рассылка для клиентов</b>\n\n"
                f"Напишите сообщение, которое собираетесь переслать всем клиентам сервиса:"
            )
        case "mailing_couriers":
            current_state = AdminState.mailing_couriers.state
            text = (
                f"<b>Рассылка для курьеров</b>\n\n"
                f"Напишите сообщение, которое собираетесь переслать всем курьерам сервиса:"
            )
        case "mailing_partners":
            current_state = AdminState.mailing_partners.state
            text = (
                f"<b>Рассылка для партнеров</b>\n\n"
                f"Напишите сообщение, которое собираетесь переслать всем партнерам сервиса:"
            )

    await callback_query.message.answer(
        text=text,
        disable_notification=True,
        parse_mode="HTML",
    )

    await callback_query.message.delete()

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.message(
    StateFilter(
        AdminState.mailing_users,
        AdminState.mailing_couriers,
        AdminState.mailing_partners,
    ),
)
async def send_mailing(
    message: Message,
    state: FSMContext,
):
    """Обрабатывает рассылку сообщения для клиентов"""

    tg_id = message.from_user.id
    msg_text_mailing = message.text.strip()
    current_state = await state.get_state()

    match current_state:
        case AdminState.mailing_users.state:
            all_customers_tg_ids = (
                await customer_data.get_all_customers_tg_ids_notify_status_true()
            )
            for tg_id in all_customers_tg_ids:
                await customer_bot.send_message(
                    chat_id=tg_id,
                    text=msg_text_mailing,
                    disable_notification=True,
                    disable_web_page_preview=True,
                    parse_mode="HTML",
                )
        case AdminState.mailing_couriers.state:
            all_couriers_tg_ids = (
                await courier_data.get_all_couriers_tg_ids_notify_status_true()
            )
            for tg_id in all_couriers_tg_ids:
                await courier_bot.send_message(
                    chat_id=tg_id,
                    text=msg_text_mailing,
                    disable_notification=True,
                    disable_web_page_preview=True,
                    parse_mode="HTML",
                )
        case AdminState.mailing_partners.state:
            all_couriers_tg_ids = await partner_data.get_all_partners_tg_ids()
            for tg_id in all_couriers_tg_ids:
                await partner_bot.send_message(
                    chat_id=tg_id,
                    text=msg_text_mailing,
                    disable_notification=True,
                    disable_web_page_preview=True,
                    parse_mode="HTML",
                )

    current_state = AdminState.default.state
    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


# ---


@admin_r.message(
    StateFilter(AdminState.choose_user_by_ID),
)
async def get_user_by_ID(
    message: Message,
    state: FSMContext,
):
    """Возвращает клиента по его ID"""

    tg_id = message.from_user.id
    current_state = AdminState.default.state

    user_ID_str = message.text.strip()

    try:
        user_ID = int(user_ID_str)
    except Exception as e:
        log.error(f"Exception {e}")
        await message.answer(
            text="Введите целое число",
            disable_notification=True,
        )

    customer_tg_id, name, phone, city, block_status = (
        await admin_data.get_customer_full_info_by_ID(id=user_ID)
    )

    if name != None:

        customer_link = f"<a href='tg://user?id={customer_tg_id}'>Профиль</a>"

        text = (
            f"<b>👫 Клиент</b>\n\n"
            f"Имя: {name}\n"
            f"Телефон: {phone}\n"
            f"Link: {customer_link}\n"
            f"Город: {city}\n\n"
            f"Статус: {'Заблокирован 🔒' if block_status else 'Активный 🍀'}"
        )

        reply_kb = await kb.get_user_manipulate_kb(
            type_of_user="customer",
            is_blocked=block_status,
        )

        await message.answer(
            text=text,
            reply_markup=reply_kb,
            disable_notification=True,
            parse_mode="HTML",
        )

    else:
        await message.answer(
            text="Данных нет",
            disable_notification=True,
        )

    await state.set_state(current_state)
    await state.update_data(customer_id=user_ID)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.message(
    StateFilter(AdminState.choose_courier_by_ID),
)
async def get_courier_by_ID(
    message: Message,
    state: FSMContext,
):
    """Возвращает курьера по его ID"""

    tg_id = message.from_user.id
    current_state = AdminState.default.state

    courier_ID_str = message.text.strip()

    try:
        courier_ID = int(courier_ID_str)
    except Exception as e:
        log.error(f"Exception {e}")
        await message.answer(
            text="Введите целое число",
            disable_notification=True,
        )

    courier_tg_id, name, phone, city, courier_XP, block_status = (
        await admin_data.get_courier_full_info_by_ID(id=courier_ID)
    )

    if name != None:

        courier_link = f"<a href='tg://user?id={courier_tg_id}'>Профиль</a>"

        text = (
            f"<b>🥷 Курьер</b>\n\n"
            f"Имя: {name}\n"
            f"Телефон: {phone}\n"
            f"Link: {courier_link}\n"
            f"Город: {city}\n"
            f"XP: {courier_XP}\n\n"
            f"Статус: {'Заблокирован 🔒' if block_status else 'Активный 🍀'}"
        )

        reply_kb = await kb.get_user_manipulate_kb(
            type_of_user="courier",
            is_blocked=block_status,
        )

        await message.answer(
            text=text,
            reply_markup=reply_kb,
            disable_notification=True,
            parse_mode="HTML",
        )

    else:
        await message.answer(
            text="Данных нет",
            disable_notification=True,
        )

    await state.set_state(current_state)
    await state.update_data(courier_id=courier_ID, courier_tg_id=courier_tg_id)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.message(
    StateFilter(AdminState.choose_partner_by_SEED),
)
async def get_partner_by_SEED(
    message: Message,
    state: FSMContext,
):
    """Возвращает партнера по его SEED"""

    tg_id = message.from_user.id
    current_state = AdminState.default.state

    partner_SEED = message.text.strip()

    partner_tg_id, balance, block_status = (
        await admin_data.get_partner_full_info_by_SEED(seed=partner_SEED)
    )

    if partner_tg_id != None:

        partner_link = f"<a href='tg://user?id={partner_tg_id}'>Профиль</a>"

        text = (
            f"<b>🤝 Партнеры</b>\n\n"
            f"Баланс: {balance if balance else 0}\n"
            f"Link: {partner_link}\n"
            f"Статус: {'Заблокирован 🔒' if block_status else 'Активный 🍀'}"
        )

        reply_kb = await kb.get_user_manipulate_kb(
            type_of_user="partner",
            is_blocked=block_status,
        )

        await message.answer(
            text=text,
            reply_markup=reply_kb,
            disable_notification=True,
            parse_mode="HTML",
        )

    else:
        await message.answer(
            text="Данных нет",
            disable_notification=True,
        )

    await state.set_state(current_state)
    await state.update_data(partner_seed=partner_SEED)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


# ---


@admin_r.callback_query(
    F.data == "add_XP",
)
async def data_add_XP(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обрабатывает нажатие на кнопку начисления XP"""

    tg_id = callback_query.from_user.id
    current_state = AdminState.add_XP.state
    data = await state.get_data()
    courier_id = data.get("courier_id")

    text = f"Сколько баллов XP начислить курьеру с ID {courier_id}:"

    await callback_query.message.answer(
        text=text,
        disable_notification=True,
    )

    await callback_query.message.delete()

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


# ---


@admin_r.message(
    StateFilter(AdminState.add_XP.state),
)
async def send_XP_to_courier(
    message: Message,
    state: FSMContext,
):
    """Начисляет XP курьеру"""

    tg_id = message.from_user.id
    current_state = AdminState.default.state
    data = await state.get_data()
    courier_id = data.get("courier_id")
    courier_tg_id = data.get("courier_tg_id")

    msg_XP = message.text.strip()

    try:
        new_XP = int(msg_XP)
    except Exception as e:
        log.error(f"Error {e}")
        await message.answer(
            text="Введите число",
            disable_notification=True,
        )

    is_update = await courier_data.update_courier_XP(
        tg_id=courier_tg_id,
        new_XP=new_XP,
    )

    if is_update:
        await courier_bot.send_message(
            chat_id=courier_tg_id,
            text=f"Вам было начислено <b>{new_XP}</b> очков! ✴️",
            parse_mode="HTML",
        )

        await message.answer(
            text=f"Курьеру c ID {courier_id} было начислено {new_XP} очков!",
            disable_notification=True,
        )

    else:

        await message.answer(
            text=f"Очки не были начислены, повторите действие!",
            disable_notification=True,
        )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


# ---


@admin_r.callback_query(
    F.data.in_(
        [
            "block_customer",
            "unblock_customer",
            "block_courier",
            "unblock_courier",
            "block_partner",
            "unblock_partner",
        ],
    )
)
async def call_block_unblock_customer(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обрабатывает нажатие на блок/разблок клиента"""

    tg_id = callback_query.from_user.id
    current_state = AdminState.default.state
    data = await state.get_data()
    customer_id = data.get("customer_id")
    courier_id = data.get("courier_id")
    partner_seed = data.get("partner_seed")

    match callback_query.data:
        case "block_customer":
            await admin_data.change_customer_block_status(
                id=customer_id,
                block_status=True,
            )
            await callback_query.message.answer(
                text=f"Клиент с ID {customer_id} был заблокирован 🔒",
                disable_notification=True,
            )

        case "unblock_customer":
            await admin_data.change_customer_block_status(
                id=customer_id,
                block_status=False,
            )
            await callback_query.message.answer(
                text=f"Клиент с ID {customer_id} был разблокирован 🔓",
                disable_notification=True,
            )

        case "block_courier":
            await admin_data.change_courier_block_status(
                id=courier_id,
                block_status=True,
            )
            await callback_query.message.answer(
                text=f"Курьер с ID {customer_id} был заблокирован 🔒",
                disable_notification=True,
            )

        case "unblock_courier":
            await admin_data.change_courier_block_status(
                id=courier_id,
                block_status=False,
            )
            await callback_query.message.answer(
                text=f"Курьер с SEED {partner_seed} был разблокирован 🔓",
                disable_notification=True,
            )

        case "block_partner":
            await admin_data.change_partner_block_status(
                seed=partner_seed,
                block_status=True,
            )
            await callback_query.message.answer(
                text=f"Партнер с SEED {partner_seed} был заблокирован 🔓",
                disable_notification=True,
            )

        case "unblock_partner":
            await admin_data.change_partner_block_status(
                seed=partner_seed,
                block_status=False,
            )
            await callback_query.message.answer(
                text=f"Партнер с ID {customer_id} был разблокирован 🔓",
                disable_notification=True,
            )

        case _:
            await callback_query.message.answer(
                text="❌ Ошибка! Неизвестная команда.",
            )
            return

    await callback_query.message.delete()

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


# --- Заказы


@admin_r.message(
    F.text == "/orders",
)
@admin_r.callback_query(
    F.data == "refresh_orders",
)
async def cmd_orders(
    event: Message | CallbackQuery,
    state: FSMContext,
):
    """Обработчик команды /orders для админа."""

    tg_id = event.from_user.id
    all_admins = await admin_data.get_all_admins()
    data = await state.get_data()

    if tg_id != SUPER_ADMIN_TG_ID and tg_id not in [
        admin.admin_tg_id for admin in all_admins
    ]:
        await event.answer(
            text="❌ У вас нет доступа к этой команде.",
        )
        return

    current_state = AdminState.default.state

    (
        pending_orders,
        active_orders,
        completed_orders,
        canceled_orders,
    ) = await order_data.get_all_orders()

    len_all_orders = (
        len(pending_orders)
        + len(active_orders)
        + len(completed_orders)
        + len(canceled_orders)
    )

    text = (
        f"<b>📋 Заказы</b>\n\n"
        f"Здесь вы можете просмотреть текущую статистику по заказам на платформе.\n\n"
        f" - Всего заказов: <b>{len_all_orders}</b>\n"
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

        try:
            orders_msg_id = data.get("orders_msg_id")
            if orders_msg_id:
                await event.bot.delete_message(
                    chat_id=event.chat.id,
                    message_id=orders_msg_id,
                )
                await state.update_data(orders_msg_id=None)
                await rediska.save_fsm_state(state, admin_bot_id, tg_id)
                await event.delete()
        except Exception as e:
            log.warning(f"Не удалось удалить сообщение: {e}")

        orders_msg = await event.answer(
            text=text,
            reply_markup=reply_kb,
            parse_mode="HTML",
        )

        await state.update_data(orders_msg_id=orders_msg.message_id)

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


@admin_r.callback_query(
    F.data == "choose_order",
)
async def call_choose_order(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обрабатывает нажатие на choose_order"""

    tg_id = callback_query.from_user.id
    current_state = AdminState.choose_order.state

    await callback_query.message.answer(
        text=f"Введите номер заказа:",
        disable_notification=True,
    )

    await callback_query.message.delete()

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.message(
    StateFilter(AdminState.choose_order),
)
async def get_entered_order(
    message: Message,
    state: FSMContext,
):
    """Возвращает данные по заказу"""

    tg_id = message.from_user.id
    current_state = AdminState.default.state

    order_id_str = message.text.strip()

    try:
        order_id = int(order_id_str)
    except Exception as e:
        current_state = AdminState.choose_order.state
        log.error(f"Error {e}")
        await message.answer(
            text=f"Введите корректно номер заказа:",
            disable_notification=True,
        )

    order_data_info = await order_data.get_order_dict_by_id(order_id=order_id)

    if order_data_info == None:
        await message.answer(text="Данных нет")

        await state.set_state(current_state)
        await rediska.set_state(admin_bot_id, tg_id, current_state)

        return

    pdf_path = await pdf_creator.create_order_data_pdf(data=order_data_info)

    with open(pdf_path, "rb") as f:
        file_data = f.read()

    await message.answer_document(
        document=BufferedInputFile(file_data, filename=pdf_path.name),
        caption="Данные по заказу",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


# --- global
# ---
# ---


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
    all_admins = await admin_data.get_all_admins()

    data = await state.get_data()

    if tg_id != SUPER_ADMIN_TG_ID and tg_id not in [
        admin.admin_tg_id for admin in all_admins
    ]:
        await event.answer(
            text="❌ У вас нет доступа к этой команде.",
        )
        return

    service_status = await admin_data.get_service_status()
    partner_program_status = await admin_data.get_partner_program_status()
    task_status = await admin_data.get_task_status()

    common_price, max_price = await admin_data.get_order_prices()
    subs_price = await admin_data.get_subscription_price() // 100
    discount_percent_first_order = await admin_data.get_first_order_discount()
    free_period_days = await admin_data.get_free_period_days()
    customers, couriers, partners = await admin_data.get_all_users()

    customers = len([c.customer_id for c in customers])
    couriers = len([c.courier_id for c in couriers])
    partners = len([p.partner_id for p in partners])
    all_users = customers + couriers + partners

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

    all_payments = await admin_data.get_all_payments()
    profit = await admin_data.get_profit()
    turnover = await admin_data.get_turnover()

    _, fastest_order_ever_speed = await order_data.get_fastest_order_speed_ever()
    fastest_order_ever_speed = (
        fastest_order_ever_speed if fastest_order_ever_speed else "..."
    )

    all_earn_waiting_requests = await partner_data.get_all_waiting_earn_requests()

    min_refund_amount = await partner_data.get_min_refund_amount()
    max_refund_amount = await partner_data.get_max_refund_amount()

    base_order_XP = await admin_data.get_base_order_XP()
    distance_XP = await admin_data.get_distance_XP()
    speed_XP = await admin_data.get_speed_XP()

    interval = await admin_data.get_new_orders_notification_interval()
    support_link = await admin_data.get_support_link()
    radius_km = await admin_data.get_distance_radius()

    max_orders_count = await admin_data.get_courier_max_active_orders_count()

    taxi_orders_count = await admin_data.get_taxi_orders_count()

    global_state_data = {
        "common_price": common_price,
        "max_price": max_price,
        "subs_price": subs_price,
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
        "base_order_XP": base_order_XP,
        "distance_XP": distance_XP,
        "speed_XP": speed_XP,
        "interval": interval,
        "support_link": support_link,
        "radius_km": radius_km,
        "max_orders_count": max_orders_count,
        "taxi_orders_count": taxi_orders_count,
    }

    text = (
        f"<b>🌎 Глобальное управление сервисом</b>\n\n"
        f"Здесь вы можете управлять всеми настройками сервиса и получать актуальную информацию.\n\n"
        f"<b>⚙️ Сервис</b>\n"
        f" ▸ Сервис: <b>{'ON ✅' if service_status else 'OFF ❌'}</b>\n"
        f" ▸ Партнерская программа: <b>{'ON ✅' if partner_program_status else 'OFF ❌'}</b>\n"
        f" ▸ Уведомления: <b>{'ON 🔔' if task_status else 'OFF 🔕'}</b>\n"
        f" •\n"
        f" Пользователей: <b>{all_users}</b>\n"
        f" Заказов: <b>{all_orders}</b>\n\n"
        f"🤑 <b>Финансы</b>\n"
        f" ▸ Подписки: <b>{len(all_payments)}</b>\n"
        f" ▸ Оборот заказов: <b>{turnover}₽</b>\n"
        f" ▸ Прибыль: <b>{profit}₽</b>\n\n"
        f"🏆 <b>Рекорды</b>\n"
        f"  ▸ Самый быстрый заказ: <b>{fastest_order_ever_speed} км/ч </b>\n\n"
        f"💰 <b>Тарифы</b>\n"
        f" ▸ Стоимость подписки: <b>{subs_price}₽</b>\n"
        f" ▸ Стандартная цена заказ за 1км: <b>{common_price}₽</b>\n"
        f" ▸ Повышенная цена заказа за 1км: <b>{max_price}₽</b>\n"
        f" •\n"
        f" ▸ Коэфф. 0 - 5 км: <b>{coefficient_less_5km}</b>\n"
        f" ▸ Коэфф. 5 - 10 км: <b>{coefficient_5_10_km}</b>\n"
        f" ▸ Коэфф. 10 - 20 км: <b>{coefficient_10_20_km}</b>\n"
        f" ▸ Коэфф. 20+ км: <b>{coefficient_more_20_km}</b>\n"
        f" •\n"
        f" ▸ Коэфф. 00 - 06: <b>{coefficient_00_06}</b>\n"
        f" ▸ Коэфф. 06 - 12: <b>{coefficient_06_12}</b>\n"
        f" ▸ Коэфф. 12 - 18: <b>{coefficient_12_18}</b>\n"
        f" ▸ Коэфф. 18 - 21: <b>{coefficient_18_21}</b>\n"
        f" ▸ Коэфф. 21 - 00: <b>{coefficient_21_00}</b>\n"
        f" •\n"
        f" ▸ Базовый XP за заказ: <b>{base_order_XP}</b>\n"
        f" ▸ XP за расстояние: <b>{distance_XP}</b>\n"
        f" ▸ XP за скорость: <b>{speed_XP}</b>\n"
        f" •\n"
        f" ▸ Коэфф. в больших городах: <b>{coefficient_big_cities}</b>\n"
        f" ▸ Коэфф. в остальных городах: <b>{coefficient_other_cities}</b>\n"
        f" •\n"
        f" ▸ Радиус поиска: <b>{radius_km} km</b>\n"
        f" ▸ Макс количество заказов за раз: <b>{max_orders_count}</b>\n\n"
        f"🎉 <b>Акции</b>\n"
        f" ▸ Скидка на первый заказ: <b>{discount_percent_first_order}%</b>\n"
        f" ▸ Бесплатный период: <b>{free_period_days} дней</b>\n"
        f" •\n"
        f" ▸ Партнерский процент: <b>{refund_percent}%</b>\n\n"
        f"💬 <b>Сообщения</b>\n"
        f" ▸ Запросы на выплату: <b>{len(all_earn_waiting_requests)}</b>\n"
        f" ▸ Минимальная выплата: <b>{min_refund_amount}₽</b>\n"
        f" ▸ Максимальная выплата: <b>{max_refund_amount}₽</b>\n\n"
        f"🔔 <b>уведомления</b>\n"
        f" ▸ Поддержка: <b>{support_link}</b>\n\n"
        f" ▸ Заказов Taxi: <b>{taxi_orders_count}</b>\n\n"
        f"<b>Выберите действие:</b>\n"
    )

    reply_kb = await kb.get_admin_kb("/global")

    state_data = await state.get_data()
    saved_text = state_data.get("message_text_global")
    saved_kb = state_data.get("message_kb_global")

    new_kb_json = json.dumps(reply_kb.model_dump())

    if isinstance(event, Message):

        try:
            global_msg_id = data.get("global_msg_id")
            if global_msg_id:
                await event.bot.delete_message(
                    chat_id=event.chat.id,
                    message_id=global_msg_id,
                )
                await state.update_data(my_profile_msg_id=None)
                await rediska.save_fsm_state(state, admin_bot_id, tg_id)
                await event.delete()
        except Exception as e:
            log.warning(f"Не удалось удалить сообщение: {e}")

        global_msg = await event.answer(
            text=text,
            reply_markup=reply_kb,
            disable_notification=True,
            disable_web_page_preview=True,
            parse_mode="HTML",
        )

        await state.update_data(global_msg_id=global_msg.message_id)

    elif isinstance(event, CallbackQuery):

        if event.data == "back_global_data":
            await event.answer(
                text="↩️ Назад",
                show_alert=False,
            )

            await event.message.edit_text(
                text=text,
                reply_markup=reply_kb,
                disable_web_page_preview=True,
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
                disable_web_page_preview=True,
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


# --- Сервис


@admin_r.callback_query(
    F.data.in_(
        [
            "service_data",
            "turn_on_service",
            "turn_off_service",
            "turn_on_partner",
            "turn_off_partner",
            "turn_on_task",
            "turn_off_task",
        ],
    )
)
async def data_service_data(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик кнопки "Сервисные данные" для админа."""

    tg_id = callback_query.from_user.id
    current_state = AdminState.default.state

    match callback_query.data:
        case "service_data":
            await callback_query.answer(
                text="⚙️ Сервис",
                show_alert=False,
            )
        case "turn_on_service":
            await admin_data.change_service_status(status=True)
            await callback_query.answer(
                text="Service ON✅",
                show_alert=False,
            )

        case "turn_off_service":
            await admin_data.change_service_status(status=False)
            await callback_query.answer(
                text="Service OFF❌",
                show_alert=False,
            )

        case "turn_on_partner":
            await admin_data.change_partner_program(status=True)
            await callback_query.answer(
                text="Partner program ON✅",
                show_alert=False,
            )

        case "turn_off_partner":
            await admin_data.change_partner_program(status=False)
            await callback_query.answer(
                text="Partner program OFF❌",
                show_alert=False,
            )

        case "turn_on_task":
            await admin_data.change_task_status(task_status=True)
            await callback_query.answer(
                text="Task ON✅",
                show_alert=False,
            )

        case "turn_off_task":
            await admin_data.change_task_status(task_status=False)
            await callback_query.answer(
                text="Task OFF❌",
                show_alert=False,
            )

        case _:
            await callback_query.answer("Неизвестное действие", show_alert=True)

    service_status = await admin_data.get_service_status()
    partner_program_status = await admin_data.get_partner_program_status()
    task_status = await admin_data.get_task_status()

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
        f"<b>⚙️ Сервис</b>\n\n"
        f" ▸ Сервис: <b>{'ON ✅' if service_status else 'OFF ❌'}</b>\n"
        f" ▸ Партнерская программа: <b>{'ON ✅' if partner_program_status else 'OFF ❌'}</b>\n"
        f" ▸ Уведомления: <b>{'ON 🔔' if task_status else 'OFF 🔕'}</b>\n"
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
        status_service=not service_status,
        status_partner=not partner_program_status,
        task_status=not task_status,
    )

    await callback_query.message.edit_text(
        text=text,
        reply_markup=reply_kb,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


# --- Финансы


@admin_r.callback_query(
    F.data == "finance",
)
async def data_finance(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик кнопки "Финансы" для админа."""

    await callback_query.answer(
        text="🤑 Финансы",
        show_alert=False,
    )

    tg_id = callback_query.from_user.id
    current_state = AdminState.default.state

    all_payments = await admin_data.get_all_payments()
    profit = await admin_data.get_profit()
    turnover = await admin_data.get_turnover()

    text = (
        f"🤑 <b>Финансы</b>\n\n"
        f" ▸ Подписки: <b>{len(all_payments)}</b>\n"
        f" ▸ Оборот: <b>{turnover}₽</b>\n"
        f" ▸ Прибыль: <b>{profit}₽</b>\n"
    )

    reply_kb = await kb.get_admin_kb("finance")

    await callback_query.message.edit_text(
        text=text,
        reply_markup=reply_kb,
        disable_web_page_preview=True,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.callback_query(
    F.data == "full_finance_report_by_date",
)
async def call_finance_full_report_by_date(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик кнопки full_report_by_date, нужно ввести дату"""

    tg_id = callback_query.from_user.id
    current_state = AdminState.full_financial_report_by_date.state

    today = datetime.today().strftime("%Y-%m-%d")

    text = (
        f"📅 <b>Полный отчет по дате</b>\n\n"
        f"Введите дату в формате <b>YYYY-MM-DD</b>.\n\n"
        f"Пример: <code>{today}</code>"
    )

    await callback_query.message.edit_text(
        text=text,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.callback_query(
    F.data == "full_finance_report_by_period",
)
async def call_finance_full_report_by_period(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик кнопки full_report_by_period, нужно ввести даты"""

    tg_id = callback_query.from_user.id
    current_state = AdminState.full_financial_report_by_period.state

    today = datetime.today().date()
    today_str = datetime.today().strftime("%Y-%m-%d")
    month_ago = today - relativedelta(months=1)

    text = (
        f"📅 <b>Полный отчет по дате</b>\n\n"
        f"Введите даты в формате <b>YYYY-MM-DD</b> через пробел.\n\n"
        f"Пример: <code>{month_ago}:{today_str}</code>"
    )

    await callback_query.message.edit_text(
        text=text,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.message(
    StateFilter(AdminState.full_financial_report_by_period),
)
async def get_finance_full_report_by_period(
    message: Message,
    state: FSMContext,
):
    """Обработчик ввода для полного отчета по финансам за период."""

    tg_id = message.from_user.id
    current_state = AdminState.default.state

    start_date_str, end_date_str = message.text.strip().split(":")

    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except ValueError:
        await message.answer(text="❌ Неверный формат даты. Попробуйте снова.")
        return

    if start_date > end_date:
        await message.answer(
            text="❌ Начальная дата больше конечной. Попробуйте снова."
        )
        return

    payments = await admin_data.get_period_payments(start_date, end_date)
    turnover = await admin_data.get_turnover_by_period(start_date, end_date)
    profit = await admin_data.get_profit_by_period(start_date, end_date)

    text = (
        f"📅 Полный отчет за <b>{start_date}:{end_date}</b>:\n\n"
        f" ▸ Подписки: <b>{len(payments)}</b>\n"
        f" ▸ Оборот заказов: <b>{turnover}₽</b>\n"
        f" ▸ Прибыль: <b>{profit}₽</b>\n"
    )

    await message.answer(
        text=text,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.message(
    StateFilter(AdminState.full_financial_report_by_date),
)
async def get_finance_full_report_by_date(
    message: Message,
    state: FSMContext,
):
    """Обработчик ввода для полного отчета по финансам за дату."""

    tg_id = message.from_user.id
    current_state = AdminState.default.state

    date_str = message.text.strip()

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        await message.answer(text="❌ Неверный формат даты. Попробуйте снова.")
        return

    payments = await admin_data.get_date_payments(date)
    turnover = await admin_data.get_date_turnover(date)
    profit = await admin_data.get_date_profit(date)

    text = (
        f"📅 Полный отчет за <b>{date}</b>:\n\n"
        f" ▸ Подписки: <b>{len(payments)}</b>\n"
        f" ▸ Оборот заказов: <b>{turnover}₽</b>\n"
        f" ▸ Прибыль: <b>{profit}₽</b>\n"
    )

    await message.answer(
        text=text,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


# --- Рекорды
#
# ---
# ---


@admin_r.callback_query(
    F.data == "records",
)
@admin_r.callback_query(
    F.data == "back_records",
)
async def data_records(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик кнопки "Рекорды" для админа."""

    await callback_query.answer(
        text="🏆 Рекорды",
        show_alert=False,
    )

    tg_id = callback_query.from_user.id
    current_state = AdminState.default.state

    text = (
        f"🏆 <b>Рекорды сервиса</b>\n\n"
        f"Здесь ты можешь узнать, кто добился наибольших результатов среди всех курьеров. "
        f"Показатели обновляются автоматически по завершению заказов.\n\n"
        f"<b>Метрики:</b>\n\n"
        f"🚀 <b>Скорость</b> — кто выполнил заказ быстрее всех. Считается по времени между взятием и завершением заказа.\n\n"
        f"📏 <b>Пройденная дистанция</b> — кто прошёл больше всех километров за всё время. Учитываются все завершённые доставки.\n\n"
        f"📦 <b>Количество заказов</b> — кто выполнил больше всего заказов. Только завершённые заказы.\n\n"
        f"💰 <b>Заработал ₽</b> — кто получил больше всего денег от клиентов за доставку. Суммируется по всем завершённым заказам.\n\n"
        f"Выберите метрику.\n\n"
    )

    reply_kb = await kb.get_admin_kb("records")

    await callback_query.message.edit_text(
        text=text,
        reply_markup=reply_kb,
        disable_web_page_preview=True,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


# Скорость


@admin_r.callback_query(
    F.data == "speed_records",
)
async def data_records_speed(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик кнопки "Скорость" для админа."""
    await callback_query.answer(
        text="💨 Скорость",
        show_alert=False,
    )

    tg_id = callback_query.from_user.id
    current_state = AdminState.default.state

    courier_id, fastest_order_ever_speed = (
        await order_data.get_fastest_order_speed_ever()
    )
    fastest_order_ever_speed = (
        fastest_order_ever_speed if fastest_order_ever_speed else "..."
    )

    name, phone, city = await courier_data.get_courier_info_by_id(id=courier_id)

    text = (
        f"💨 <b>Скорость</b>\n\n"
        f"Курьер: <b>{name if name else '...'}</b>\n"
        f"Номер курьера: {phone if phone else '...'}\n"
        f"Город: <b>{city if city else '...'}</b>\n"
        f"ID курьера: <b>{courier_id if courier_id else '...'}</b>\n"
        f" •\n"
        f"Самый быстрый заказ: <b>{fastest_order_ever_speed}</b> км/ч\n\n"
    )

    reply_kb = await kb.get_admin_kb("speed_records")

    await callback_query.message.edit_text(
        text=text,
        reply_markup=reply_kb,
        disable_web_page_preview=True,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.callback_query(
    F.data == "full_speed_report_by_date",
)
async def call_records_full_report_by_date(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик кнопки full_report_by_date, нужно ввести дату"""

    tg_id = callback_query.from_user.id
    current_state = AdminState.full_speed_report_by_date.state

    today = datetime.today().strftime("%Y-%m-%d")

    text = (
        f"📅 <b>Полный отчет по дате</b>\n\n"
        f"Введите дату в формате <b>YYYY-MM-DD</b>.\n\n"
        f"Пример: <code>{today}</code>"
    )

    await callback_query.message.edit_text(
        text=text,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.callback_query(
    F.data == "full_speed_report_by_period",
)
async def call_records_full_report_by_period(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик кнопки full_speed_report_by_period, нужно ввести даты"""

    tg_id = callback_query.from_user.id
    current_state = AdminState.full_speed_report_by_period.state

    today = datetime.today().date()
    today_str = datetime.today().strftime("%Y-%m-%d")
    month_ago = today - relativedelta(months=1)

    text = (
        f"📅 <b>Полный отчет по дате</b>\n\n"
        f"Введите даты в формате <b>YYYY-MM-DD</b> через пробел.\n\n"
        f"Пример: <code>{month_ago}:{today_str}</code>"
    )

    await callback_query.message.edit_text(
        text=text,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.message(
    StateFilter(AdminState.full_speed_report_by_date),
)
async def get_records_full_report_by_date(
    message: Message,
    state: FSMContext,
):
    """Обработчик ввода для полного отчета по рекордам за дату."""

    tg_id = message.from_user.id
    current_state = AdminState.default.state

    date_str = message.text.strip()

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        await message.answer(text="❌ Неверный формат даты. Попробуйте снова.")
        return

    (
        order_id,
        courier_tg_id,
        courier_name,
        courier_username,
        courier_phone,
        city,
        speed,
        distance,
        execution_time_seconds,
    ) = await order_data.get_fastest_order_by_date(date)

    if order_id:

        tg_link = (
            f"<a href='tg://user?id={courier_tg_id}'>Написать</a>"
            if not courier_username
            else f"<a href='https://t.me/{courier_username}'>{courier_username}</a>"
        )
        day_reward = await admin_data.get_reward_for_day_fastest_speed()
        month_reward = await admin_data.get_reward_for_month_fastest_speed()

        execution_time_hours = int(execution_time_seconds // 3600)
        execution_time_minutes = int(execution_time_seconds % 3600 // 60)

        text = (
            f"📅 Полный отчет за <b>{date_str}</b>:\n\n"
            f"Заказ: №<b>{order_id}</b>\n"
            f"Город: <b>{city}</b>\n"
            f"Дистанция: <b>{distance} км</b>\n"
            f"Время доставки <b>{execution_time_hours} ч {execution_time_minutes} мин</b>\n"
            f"Скорость: <b>{speed} км/ч</b>\n"
            f"Курьер: <b>{courier_name}</b>\n"
            f"Номер курьера: {courier_phone}\n"
            f"Telegram курьера: {tg_link}\n"
            f" •\n"
            f"Месячная награда: <b>{month_reward}₽</b>\n"
            f"Дневная награда: <b>{day_reward}₽</b>\n"
        )

    else:
        text = f"📅 Полный отчет за <b>{date_str}</b>:\n" f"Данных не найдено."

    await message.answer(
        text=text,
        disable_notification=True,
        disable_web_page_preview=True,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.message(
    StateFilter(AdminState.full_speed_report_by_period),
)
async def get_records_full_report_by_period(
    message: Message,
    state: FSMContext,
):
    """Обработчик ввода для полного отчета по рекордам за период."""

    tg_id = message.from_user.id
    current_state = AdminState.default.state

    start_date_str, end_date_str = message.text.strip().split(":")

    try:

        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except ValueError:
        await message.answer(text="❌ Неверный формат даты. Попробуйте снова.")
        return

    (
        order_id,
        courier_tg_id,
        courier_name,
        courier_username,
        courier_phone,
        city,
        speed,
        distance,
        execution_time_seconds,
    ) = await order_data.get_fastest_order_by_period(start_date, end_date)

    if order_id:

        tg_link = (
            f"<a href='tg://user?id={courier_tg_id}'>Написать</a>"
            if not courier_username
            else f"<a href='https://t.me/{courier_username}'>{courier_username}</a>"
        )
        day_reward = await admin_data.get_reward_for_day_fastest_speed()
        month_reward = await admin_data.get_reward_for_month_fastest_speed()

        execution_time_hours = int(execution_time_seconds // 3600)
        execution_time_minutes = int(execution_time_seconds % 3600 // 60)

        text = (
            f"📅 Полный отчет за <b>{start_date_str}:{end_date_str}</b>:\n\n"
            f"Самый быстрый заказ: №<b>{order_id}</b>\n"
            f"Город: <b>{city}</b>\n"
            f"Дистанция: <b>{distance} км</b>\n"
            f"Время доставки <b>{execution_time_hours} ч {execution_time_minutes} мин</b>\n"
            f"Скорость: <b>{speed} км/ч</b>\n"
            f"Курьер: <b>{courier_name}</b>\n"
            f"Номер курьера: {courier_phone}\n"
            f"Telegram курьера: {tg_link}\n"
            f" •\n"
            f"Дневная награда: <b>{day_reward}₽</b>\n"
            f"Месячная награда: <b>{month_reward}₽</b>\n"
        )

    else:
        text = (
            f"📅 Полный отчет за <b>{start_date_str}:{end_date_str}</b>:\n"
            f"Данных не найдено."
        )

    await message.answer(
        text=text,
        disable_notification=True,
        disable_web_page_preview=True,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


# Дистанция


@admin_r.callback_query(
    F.data == "distance_records",
)
async def data_records_distance(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """
    Обработчик кнопки "Общая дистанция" для админа.
    Выводит рекорд по пройденной дистанции среди курьеров за все время.
    - Курьер
    - Дистанция
    """

    await callback_query.answer(
        text="📏 Пройденная дистанция",
        show_alert=False,
    )

    tg_id = callback_query.from_user.id
    current_state = AdminState.default.state

    courier_id, total_distance = (
        await admin_data.get_courier_info_by_max_distance_covered_ever()
    )

    name, phone, city = await courier_data.get_courier_info_by_id(id=courier_id)

    text = (
        f"📏 <b>Пройденная дистанция</b>\n\n"
        f"Курьер: <b>{name}</b>\n"
        f"Номер курьера: {phone}\n"
        f"Город: <b>{city}</b>\n"
        f"ID курьера: <b>{courier_id if courier_id else '...'}</b>\n"
        f" •\n"
        f"Дальность: <b>{total_distance if total_distance else '...'}</b> км\n"
    )

    reply_kb = await kb.get_admin_kb("distance_records")

    await callback_query.message.edit_text(
        text=text,
        reply_markup=reply_kb,
        disable_web_page_preview=True,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.callback_query(
    F.data == "full_distance_report_by_date",
)
async def call_records_full_report_by_date(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик кнопки full_report_by_date, нужно ввести дату"""
    tg_id = callback_query.from_user.id
    current_state = AdminState.full_distance_report_by_date.state

    today = datetime.today().strftime("%Y-%m-%d")

    text = (
        f"📅 <b>Полный отчет по дате</b>\n\n"
        f"Введите дату в формате <b>YYYY-MM-DD</b>.\n\n"
        f"Пример: <code>{today}</code>"
    )

    await callback_query.message.edit_text(
        text=text,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.message(
    StateFilter(AdminState.full_distance_report_by_date),
)
async def get_records_distance_full_report_by_date(
    message: Message,
    state: FSMContext,
):
    """Обработчик ввода для полного отчета по рекордам за дату."""
    tg_id = message.from_user.id
    current_state = AdminState.default.state

    date_str = message.text.strip()

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        await message.answer(text="❌ Неверный формат даты. Попробуйте снова.")
        return

    courier_id, total_distance = (
        await admin_data.get_courier_info_by_max_date_distance_covered(date=date)
    )

    if courier_id:
        name, phone, city = await courier_data.get_courier_info_by_id(id=courier_id)
        text = (
            f"📅 Полный отчет за <b>{date_str}</b>:\n\n"
            f"Курьер: <b>{name}</b>\n"
            f"Номер курьера: {phone}\n"
            f"Город: <b>{city}</b>\n"
            f"ID курьера: <b>{courier_id if courier_id else '...'}</b>\n"
            f" •\n"
            f"Дистанция: <b>{total_distance} км</b>\n"
        )
    else:
        text = f"📅 Полный отчет за <b>{date_str}</b>:\n" f"Данных не найдено."

    await message.answer(
        text=text,
        disable_notification=True,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.callback_query(
    F.data == "full_distance_report_by_period",
)
async def call_records_distance_full_report_by_period(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик кнопки full_report_by_period, нужно ввести даты"""
    tg_id = callback_query.from_user.id
    current_state = AdminState.full_distance_report_by_period.state

    today = datetime.today().date()
    today_str = datetime.today().strftime("%Y-%m-%d")
    month_ago = today - relativedelta(months=1)

    text = (
        f"📅 <b>Полный отчет по дате</b>\n\n"
        f"Введите даты в формате <b>YYYY-MM-DD</b> через пробел.\n\n"
        f"Пример: <code>{month_ago}:{today_str}</code>"
    )

    await callback_query.message.edit_text(
        text=text,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.message(
    StateFilter(AdminState.full_distance_report_by_period),
)
async def get_records_distance_full_report_by_period(
    message: Message,
    state: FSMContext,
):
    """Обработчик ввода для полного отчета по рекордам за период."""
    tg_id = message.from_user.id
    current_state = AdminState.default.state

    start_date_str, end_date_str = message.text.strip().split(":")

    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except ValueError:
        await message.answer(text="❌ Неверный формат даты. Попробуйте снова.")
        return

    if start_date > end_date:
        await message.answer(
            text="❌ Начальная дата больше конечной. Попробуйте снова."
        )
        return

    courier_id, total_distance = (
        await admin_data.get_courier_info_by_max_period_distance_covered(
            start_date=start_date,
            end_date=end_date,
        )
    )

    if courier_id:
        name, phone, city = await courier_data.get_courier_info_by_id(id=courier_id)
        text = (
            f"📅 Полный отчет за <b>{start_date}:{end_date}</b>:\n\n"
            f"Курьер: <b>{name}</b>\n"
            f"Номер курьера: {phone}\n"
            f"Город: <b>{city}</b>\n"
            f"ID курьера: <b>{courier_id if courier_id else '...'}</b>\n"
            f" •\n"
            f"Дистанция: <b>{total_distance} км</b>\n"
        )
    else:
        text = (
            f"📅 Полный отчет за <b>{start_date}:{end_date}</b>:\n"
            f"Данных не найдено."
        )

    await message.answer(
        text=text,
        disable_notification=True,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


# Количество заказов


@admin_r.callback_query(
    F.data == "orders_records",
)
async def data_records_orders(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик кнопки "Количество заказов" для админа."""

    await callback_query.answer(
        text="📦 Количество заказов",
        show_alert=False,
    )

    tg_id = callback_query.from_user.id
    current_state = AdminState.default.state

    courier_id, total_orders = (
        await admin_data.get_courier_info_by_max_orders_count_ever()
    )

    name, phone, city = await courier_data.get_courier_info_by_id(id=courier_id)

    text = (
        f"📦 <b>Количество заказов</b>\n\n"
        f"Курьер: <b>{name}</b>\n"
        f"Номер курьера: {phone}\n"
        f"Город: <b>{city}</b>\n"
        f"ID курьера: <b>{courier_id if courier_id else '...'}</b>\n"
        f" •\n"
        f"Заказов: <b>{total_orders if total_orders else '...'}</b>\n"
    )

    reply_kb = await kb.get_admin_kb("orders_records")

    await callback_query.message.edit_text(
        text=text,
        reply_markup=reply_kb,
        disable_web_page_preview=True,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.callback_query(
    F.data == "full_orders_report_by_date",
)
async def call_records_full_report_by_date(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик кнопки full_report_by_date, нужно ввести дату"""
    tg_id = callback_query.from_user.id
    current_state = AdminState.full_orders_report_by_date.state

    today = datetime.today().strftime("%Y-%m-%d")

    text = (
        f"📅 <b>Полный отчет по дате</b>\n\n"
        f"Введите дату в формате <b>YYYY-MM-DD</b>.\n\n"
        f"Пример: <code>{today}</code>"
    )

    await callback_query.message.edit_text(
        text=text,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.message(
    StateFilter(AdminState.full_orders_report_by_date),
)
async def get_records_full_report_by_date(
    message: Message,
    state: FSMContext,
):
    """Обработчик ввода для полного отчета по рекордам за дату."""
    tg_id = message.from_user.id
    current_state = AdminState.default.state

    date_str = message.text.strip()

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        await message.answer(text="❌ Неверный формат даты. Попробуйте снова.")
        return

    courier_id, total_orders = (
        await admin_data.get_courier_info_by_max_date_orders_count(date=date)
    )

    if courier_id:
        name, phone, city = await courier_data.get_courier_info_by_id(id=courier_id)
        text = (
            f"📅 Полный отчет за <b>{date_str}</b>:\n\n"
            f"Курьер: <b>{name}</b>\n"
            f"Номер курьера: {phone}\n"
            f"Город: <b>{city}</b>\n"
            f"ID курьера: <b>{courier_id if courier_id else '...'}</b>\n"
            f" •\n"
            f"Заказов: <b>{total_orders} шт</b>\n"
        )
    else:
        text = f"📅 Полный отчет за <b>{date_str}</b>:\n" f"Данных не найдено."

    await message.answer(
        text=text,
        disable_notification=True,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.callback_query(
    F.data == "full_orders_report_by_period",
)
async def call_records_full_report_by_period(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик кнопки full_report_by_period, нужно ввести даты"""

    tg_id = callback_query.from_user.id
    current_state = AdminState.full_orders_report_by_period.state

    today = datetime.today().date()
    today_str = datetime.today().strftime("%Y-%m-%d")
    month_ago = today - relativedelta(months=1)

    text = (
        f"📅 <b>Полный отчет по дате</b>\n\n"
        f"Введите даты в формате <b>YYYY-MM-DD</b> через пробел.\n\n"
        f"Пример: <code>{month_ago}:{today_str}</code>"
    )

    await callback_query.message.edit_text(
        text=text,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.message(
    StateFilter(AdminState.full_orders_report_by_period),
)
async def get_records_full_report_by_period(
    message: Message,
    state: FSMContext,
):
    """Обработчик ввода для полного отчета по рекордам за период."""

    tg_id = message.from_user.id
    current_state = AdminState.default.state

    start_date_str, end_date_str = message.text.strip().split(":")

    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except ValueError:
        await message.answer(text="❌ Неверный формат даты. Попробуйте снова.")
        return

    if start_date > end_date:
        await message.answer(
            text="❌ Начальная дата больше конечной. Попробуйте снова."
        )
        return

    courier_id, total_orders = (
        await admin_data.get_courier_info_by_max_period_orders_count(
            start_date=start_date,
            end_date=end_date,
        )
    )

    if courier_id:
        name, phone, city = await courier_data.get_courier_info_by_id(id=courier_id)
        text = (
            f"📅 Полный отчет за <b>{start_date}:{end_date}</b>:\n\n"
            f"Курьер: <b>{name}</b>\n"
            f"Номер курьера: {phone}\n"
            f"Город: <b>{city}</b>\n"
            f"ID курьера: <b>{courier_id if courier_id else '...'}</b>\n"
            f" •\n"
            f"Заказов: <b>{total_orders} шт</b>\n"
        )
    else:
        text = (
            f"📅 Полный отчет за <b>{start_date}:{end_date}</b>:\n"
            f"Данных не найдено."
        )

    await message.answer(
        text=text,
        disable_notification=True,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


# Заработок


@admin_r.callback_query(
    F.data == "earn_courier_record",
)
async def data_records_earn(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик кнопки "Заработок" для админа."""

    await callback_query.answer(
        text="💵 Заработок",
        show_alert=False,
    )

    tg_id = callback_query.from_user.id
    current_state = AdminState.default.state

    courier_id, total_earnings = await admin_data.get_courier_info_by_max_earned_ever()

    name, phone, city = await courier_data.get_courier_info_by_id(id=courier_id)

    text = (
        f"💵 <b>Заработок</b>\n\n"
        f"Курьер: <b>{name}</b>\n"
        f"Номер курьера: {phone}\n"
        f"Город: <b>{city}</b>\n"
        f"ID курьера: <b>{courier_id if courier_id else '...'}</b>\n"
        f" •\n"
        f"Заработок: <b>{total_earnings if total_earnings else '...'}</b> ₽\n"
    )

    reply_kb = await kb.get_admin_kb("earn_courier_record")

    await callback_query.message.edit_text(
        text=text,
        reply_markup=reply_kb,
        disable_web_page_preview=True,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.callback_query(
    F.data == "full_earned_report_by_date",
)
async def call_records_full_report_by_date(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик кнопки full_report_by_date, нужно ввести дату"""

    tg_id = callback_query.from_user.id
    current_state = AdminState.full_earned_report_by_date.state

    today = datetime.today().strftime("%Y-%m-%d")

    text = (
        f"📅 <b>Полный отчет по дате</b>\n\n"
        f"Введите дату в формате <b>YYYY-MM-DD</b>.\n\n"
        f"Пример: <code>{today}</code>"
    )

    await callback_query.message.edit_text(
        text=text,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.message(
    StateFilter(AdminState.full_earned_report_by_date),
)
async def get_records_full_report_by_date(
    message: Message,
    state: FSMContext,
):
    """Обработчик ввода для полного отчета по рекордам за дату."""

    tg_id = message.from_user.id
    current_state = AdminState.default.state

    date_str = message.text.strip()

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        await message.answer(text="❌ Неверный формат даты. Попробуйте снова.")
        return

    courier_id, total_earnings = await admin_data.get_courier_info_by_max_date_earnings(
        date=date
    )

    if courier_id:
        name, phone, city = await courier_data.get_courier_info_by_id(id=courier_id)
        text = (
            f"📅 Полный отчет за <b>{date_str}</b>:\n\n"
            f"Курьер: <b>{name}</b>\n"
            f"Номер курьера: {phone}\n"
            f"Город: <b>{city}</b>\n"
            f"ID курьера: <b>{courier_id if courier_id else '...'}</b>\n"
            f" •\n"
            f"Заработок: <b>{total_earnings} ₽</b>\n"
        )
    else:
        text = f"📅 Полный отчет за <b>{date_str}</b>:\n" f"Данных не найдено."

    await message.answer(
        text=text,
        disable_notification=True,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.callback_query(
    F.data == "full_earned_report_by_period",
)
async def call_records_full_report_by_period(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик кнопки full_report_by_period, нужно ввести даты"""

    tg_id = callback_query.from_user.id
    current_state = AdminState.full_earned_report_by_period.state

    today = datetime.today().date()
    today_str = datetime.today().strftime("%Y-%m-%d")
    month_ago = today - relativedelta(months=1)

    text = (
        f"📅 <b>Полный отчет по дате</b>\n\n"
        f"Введите даты в формате <b>YYYY-MM-DD</b> через пробел.\n\n"
        f"Пример: <code>{month_ago}:{today_str}</code>"
    )

    await callback_query.message.edit_text(
        text=text,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.message(
    StateFilter(AdminState.full_earned_report_by_period),
)
async def get_records_full_report_by_period(
    message: Message,
    state: FSMContext,
):
    """Обработчик ввода для полного отчета по рекордам за период."""

    tg_id = message.from_user.id
    current_state = AdminState.default.state

    start_date_str, end_date_str = message.text.strip().split(":")

    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except ValueError:
        await message.answer(text="❌ Неверный формат даты. Попробуйте снова.")
        return

    if start_date > end_date:
        await message.answer(
            text="❌ Начальная дата больше конечной. Попробуйте снова."
        )
        return

    courier_id, total_earnings = (
        await admin_data.get_courier_info_by_max_period_earnings(
            start_date=start_date,
            end_date=end_date,
        )
    )

    if courier_id:
        name, phone, city = await courier_data.get_courier_info_by_id(id=courier_id)
        text = (
            f"📅 Полный отчет за <b>{start_date}:{end_date}</b>:\n\n"
            f"Курьер: <b>{name}</b>\n"
            f"Номер курьера: {phone}\n"
            f"Город: <b>{city}</b>\n"
            f"ID курьера: <b>{courier_id if courier_id else '...'}</b>\n"
            f" •\n"
            f"Заработок: <b>{total_earnings} ₽</b>\n"
        )
    else:
        text = (
            f"📅 Полный отчет за <b>{start_date}:{end_date}</b>:\n"
            f"Данных не найдено."
        )

    await message.answer(
        text=text,
        disable_notification=True,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


# ---
# ---
#
# --- Тарифы


@admin_r.callback_query(
    F.data == "prices_and_tariffs",
)
async def data_prices_and_tariffs(
    callback_query: CallbackQuery,
    state: FSMContext,
):
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
    base_order_XP = global_state_data.get("base_order_XP")
    distance_XP = global_state_data.get("distance_XP")
    speed_XP = global_state_data.get("speed_XP")
    radius_km = global_state_data.get("radius_km")
    max_orders_count = global_state_data.get("max_orders_count")
    taxi_orders_count = global_state_data.get("taxi_orders_count")

    text = (
        f"<b>💰 Тарифы</b>\n\n"
        f" ▸ Стоимость подписки: <b>{subs_price}₽</b>\n"
        f" ▸ Стандартная цена заказ за 1км: <b>{common_price}₽</b>\n"
        f" ▸ Повышенная цена заказа за 1км: <b>{max_price}₽</b>\n"
        f" •\n"
        f" ▸ Коэфф. 0 - 5 км: <b>{coefficient_less_5km}</b>\n"
        f" ▸ Коэфф. 5 - 10 км: <b>{coefficient_5_10_km}</b>\n"
        f" ▸ Коэфф. 10 - 20 км: <b>{coefficient_10_20_km}</b>\n"
        f" ▸ Коэфф. 20+ км: <b>{coefficient_more_20_km}</b>\n"
        f" •\n"
        f" ▸ Коэфф. 00 - 06: <b>{coefficient_00_06}</b>\n"
        f" ▸ Коэфф. 06 - 12: <b>{coefficient_06_12}</b>\n"
        f" ▸ Коэфф. 12 - 18: <b>{coefficient_12_18}</b>\n"
        f" ▸ Коэфф. 18 - 21: <b>{coefficient_18_21}</b>\n"
        f" ▸ Коэфф. 21 - 00: <b>{coefficient_21_00}</b>\n"
        f" •\n"
        f" ▸ Базовый XP за заказ: <b>{base_order_XP}</b>\n"
        f" ▸ XP за расстояние: <b>{distance_XP}</b>\n"
        f" ▸ XP за скорость: <b>{speed_XP}</b>\n"
        f" •\n"
        f" ▸ Коэфф. в больших городах: <b>{coefficient_big_cities}</b>\n"
        f" ▸ Коэфф. в остальных городах: <b>{coefficient_other_cities}</b>\n"
        f" •\n"
        f" ▸ Радиус поиска: <b>{radius_km} km</b>\n"
        f" ▸ Макс количество заказов за раз: <b>{max_orders_count}</b>\n\n"
        f" ▸ Заказов Taxi: <b>{taxi_orders_count}</b>\n\n"
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
            "change_min_refund_amount",
            "change_max_refund_amount",
            "change_base_order_XP",
            "change_distance_XP",
            "change_speed_XP",
            "change_radius_km",
            "change_max_orders_count",
        ]
    )
)
async def call_change_price(
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
        case "change_min_refund_amount":
            current_state = AdminState.change_min_refund_amount.state
            text = "Введите новую минимальную сумму выплаты партнеру:"
        case "change_max_refund_amount":
            current_state = AdminState.change_max_refund_amount.state
            text = "Введите новую максимальную сумму выплаты партнеру:"
        case "change_base_order_XP":
            current_state = AdminState.change_base_order_XP.state
            text = "Введите новый базовый XP за заказ:"
        case "change_distance_XP":
            current_state = AdminState.change_distance_XP.state
            text = "Введите новый XP за дистанцию:"
        case "change_speed_XP":
            current_state = AdminState.change_speed_XP.state
            text = "Введите новый XP за скорость:"
        case "change_radius_km":
            current_state = AdminState.change_radius_km.state
            text = "Введите новый радиус поиска в км:"
        case "change_max_orders_count":
            current_state = AdminState.change_max_orders_count.state
            text = "Введите максимальное количество выполняемых заказов:"

        case _:
            await callback_query.answer(
                "❌ Ошибка! Неизвестная команда.", show_alert=True
            )
            return

    await callback_query.message.delete()

    tg_id = callback_query.from_user.id
    await callback_query.message.answer(
        text,
        disable_notification=True,
    )
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
        AdminState.change_min_refund_amount,
        AdminState.change_max_refund_amount,
        AdminState.change_base_order_XP,
        AdminState.change_distance_XP,
        AdminState.change_speed_XP,
        AdminState.change_radius_km,
        AdminState.change_max_orders_count,
    )
)
async def change_prices_filer(
    message: Message,
    state: FSMContext,
):
    """Обработчик изменения цен и коэффициентов для админа."""

    new_value = message.text

    log.info(f"new_value: {new_value}")

    if isinstance(new_value, str):
        try:
            new_value = float(new_value.replace(",", "."))  # Заменяем запятую на точку
        except ValueError:
            await message.answer(
                text="❌ Ошибка! Введите корректное число (например, 0.8)."
            )
            return

    current_state = await state.get_state()

    match current_state:
        case AdminState.change_subscription_price.state:
            await admin_data.change_subscription_price(int(new_value))
            text = f"✅ Новая цена подписки: {int(new_value)}₽"

        case AdminState.change_standard_order_price.state:
            await admin_data.change_standard_order_price(new_price=int(new_value))
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

        case AdminState.change_min_refund_amount.state:
            await partner_data.set_min_refund_amount(new_value)
            text = f"✅ Новая минимальная сумма выплаты партнеру: {new_value}₽"

        case AdminState.change_max_refund_amount.state:
            await partner_data.set_max_refund_amount(new_value)
            text = f"✅ Новая максимальная сумма выплаты партнеру: {new_value}₽"

        case AdminState.change_base_order_XP.state:
            await admin_data.change_base_order_XP(new_value)
            text = f"✅ Новый базовый XP за заказ: {new_value}"

        case AdminState.change_distance_XP.state:
            await admin_data.change_distance_XP(new_value)
            text = f"✅ Новый XP за дистанцию: {new_value}"

        case AdminState.change_speed_XP.state:
            await admin_data.change_speed_XP(new_value)
            text = f"✅ Новый XP за скорость: {new_value}"

        case AdminState.change_radius_km.state:
            await admin_data.change_distance_radius(new_value)
            text = f"✅ Новый радиус поиска: {new_value} км"

        case AdminState.change_max_orders_count.state:
            await admin_data.change_courier_max_active_orders_count(new_value)
            text = f"✅ Максимальное число выполняемых заказов: {int(new_value)}"

        case _:
            await message.answer(
                text="❌ Ошибка! Неизвестная команда.",
            )
            return

    tg_id = message.from_user.id
    current_state = AdminState.default.state

    await message.answer(
        text=text,
        disable_notification=True,
        disable_web_page_preview=True,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


# --- Акции


@admin_r.callback_query(
    F.data == "discounts_and_promotions",
)
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
    discount_percent_first_order = global_state_data.get("discount_percent_first_order")
    free_period_days = global_state_data.get("free_period_days")
    refund_percent = global_state_data.get("refund_percent")

    text = (
        f"<b>🎉 Акции</b>\n\n"
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
async def call_change_discount_and_promotions(
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
    await callback_query.message.answer(
        text,
        disable_notification=True,
    )
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

    await message.answer(
        text=text,
        disable_notification=True,
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


# --- Админы


@admin_r.callback_query(
    F.data == "admins",
)
async def data_admins(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик admins для админа."""

    await callback_query.answer(
        text="👨‍💼 Администраторы",
        show_alert=False,
    )

    tg_id = callback_query.from_user.id
    current_state = AdminState.default.state

    if tg_id != SUPER_ADMIN_TG_ID:
        await callback_query.message.answer(
            text="❌ У вас нет доступа к этой команде.",
        )
        return

    admins = await admin_data.get_all_admins()

    admins_name = [admin.admin_name for admin in admins]
    admins_phone = [admin.admin_phone for admin in admins]

    admins_text = "\n".join(
        f" - {i+1}. {name} {phone}"
        for i, (name, phone) in enumerate(
            zip(
                admins_name,
                admins_phone,
            )
        )
    )

    text = (
        f"<b>👨‍💼 Администраторы</b>\n\n"
        f"Всего администраторов: {len(admins)}\n\n"
        f"{admins_text if admins_text else ''}"
    )

    reply_kb = await kb.get_admin_kb("admins")

    await callback_query.message.edit_text(
        text=text,
        reply_markup=reply_kb,
        disable_notification=True,
        parse_mode="HTML",
    )

    await state.update_data(admins=text)
    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.callback_query(
    F.data == "set_admin",
)
async def set_admin(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик кнопки "Добавить администратора" для админа."""

    tg_id = callback_query.from_user.id
    current_state = AdminState.set_new_admin.state

    text = (
        f"<b>👨‍💼 Добавить администратора</b>\n\n"
        f"Введите имя и телефон администратора в формате <b>+79998887766</b>.\n\n"
        f"Пример: <code>Имя, +79998887766</code>"
    )

    await callback_query.message.edit_text(
        text=text,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.message(
    StateFilter(AdminState.set_new_admin),
)
async def set_new_admin(
    message: Message,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    """Обработчик ввода телефона нового администратора."""

    mdw_state = await state.get_state()

    if mdw_state != AdminState.set_new_admin.state:
        update = Update(update_id=0, message=message)
        await dispatcher.feed_update(bot=admin_bot, update=update)
        return

    tg_id = message.from_user.id
    current_state = AdminState.default.state

    name, phone = message.text.strip().split(", ")

    if not phone.startswith("+") or len(phone) != 12:
        await message.answer(
            text="❌ Неверный формат телефона. Попробуйте еще раз.",
        )
        return

    await admin_data.set_new_admin(name=name, phone=phone)
    await message.answer(
        text=f"✅ Администратор {name} с номером {phone} добавлен!",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.callback_query(
    F.data == "del_admin",
)
async def del_admin(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик кнопки "Удалить администратора" для админа."""

    tg_id = callback_query.from_user.id
    current_state = AdminState.del_admin.state
    admins = (await state.get_data()).get("admins")

    text = (
        f"<b>❌ Удалить администратора</b>\n\n"
        f"Введите номер телефона администратора в формате <b>+79998887766</b>.\n\n"
        f"----------------------\n"
        f"{admins}"
    )

    await callback_query.message.edit_text(
        text=text,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.message(
    filters.StateFilter(AdminState.del_admin),
)
async def call_del_admin(
    message: Message,
    state: FSMContext,
):
    """Обработчик ввода телефона удаляемого администратора."""

    tg_id = message.from_user.id
    current_state = AdminState.default.state

    phone = message.text.strip()

    if not phone.startswith("+") or len(phone) != 12:
        await message.answer(
            text="❌ Неверный формат телефона. Попробуйте еще раз.",
        )
        return

    await admin_data.del_admin(phone=phone)
    await message.answer(
        text=f"✅ Администратор с номером {phone} удален!",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


# --- Сообщения


@admin_r.callback_query(
    F.data == "messages",
)
async def data_messages(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик кнопки 'Сообщения' для админа с PDF-файлом запросов."""
    await callback_query.answer(text="💬 Сообщения", show_alert=False)

    tg_id = callback_query.from_user.id
    current_state = AdminState.default.state

    all_earn_waiting_requests = await partner_data.get_all_waiting_earn_requests()

    pdf_path = await pdf_creator.create_earn_requests_pdf(all_earn_waiting_requests)

    with open(pdf_path, "rb") as f:
        file_data = f.read()

    await callback_query.message.answer_document(
        document=BufferedInputFile(file_data, filename=pdf_path.name),
        caption="📄 Список запросов на выплаты",
    )

    total_sum = sum(data[3] for data in all_earn_waiting_requests.values())

    summary_text = (
        f"💬 <b>Сообщения</b>\n\n"
        f"<b>Запросы на выплату:</b> {len(all_earn_waiting_requests)}\n"
        f"<b>Общая сумма к выплате:</b> {total_sum}₽"
    )

    reply_kb = await kb.get_admin_kb("messages")

    await callback_query.message.answer(
        text=summary_text,
        reply_markup=reply_kb,
        parse_mode="HTML",
    )

    await callback_query.message.delete()

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.callback_query(
    F.data == "process_request",
)
async def process_request(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик кнопки 'Обработать запрос' для админа."""

    tg_id = callback_query.from_user.id
    current_state = AdminState.process_request.state

    text = (
        f"<b>💰 Обработать запрос</b>\n\n"
        f"Введите номер запроса на выплату в формате <b>123456789</b>.\n\n"
        f"Пример: <code>123456789</code>"
    )

    await callback_query.message.answer(
        text=text,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.message(
    StateFilter(AdminState.process_request),
)
async def process_request_input(
    message: Message,
    state: FSMContext,
):
    """Обработчик ввода номера запроса на выплату для админа."""

    tg_id = message.from_user.id
    current_state = AdminState.default.state

    request_id = message.text.strip()

    if not request_id.isdigit():
        await state.set_state(current_state)
        await message.answer(
            text="❌ Неверный формат номера запроса. Попробуйте еще раз.",
        )
        return

    else:
        request_id = int(request_id)

    partner_tg_id, partner_user_lin, amount, date = (
        await partner_data.get_waiting_earn_request_by_id(request_id)
    )

    if not partner_tg_id:
        await state.set_state(current_state)
        await message.answer(
            text="❌ Запрос не найден. Проверьте номер и попробуйте снова.",
        )
        return

    reply_kb = await kb.get_admin_kb("process_request")

    text = (
        f"<b>Запрос на выплату №{request_id}</b>\n\n"
        f"<b> - 👤 Пользователь:</b> {partner_user_lin}\n"
        f"<b> - 💰 Сумма:</b> {amount}₽\n"
        f"<b> - 📅 Дата запроса:</b> {date}\n\n"
        f"После выплаты подтвердите его обработку!\n\n"
    )

    await message.answer(
        text=text,
        reply_markup=reply_kb,
        disable_notification=True,
        parse_mode="HTML",
    )

    await state.update_data(
        request_id=request_id,
        partner_tg_id=partner_tg_id,
        amount=amount,
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.callback_query(
    F.data == "confirm_request",
)
async def confirm_request(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик кнопки 'Подтвердить запрос' для админа."""

    tg_id = callback_query.from_user.id
    current_state = AdminState.default.state

    data = await state.get_data()
    request_id = data.get("request_id")
    partner_tg_id = data.get("partner_tg_id")
    amount = data.get("amount")

    _ = await partner_data.update_earn_request_status_and_balance(
        request_id=request_id,
        partner_tg_id=partner_tg_id,
    )

    text = f"✅ Запрос на выплату №{request_id} обработан!\n\n"

    await callback_query.message.edit_text(
        text=text,
        parse_mode="HTML",
    )

    try:
        await partner_bot.send_message(
            chat_id=partner_tg_id,
            text=f"💰 Запрос на выплату №{request_id} обработан!\n\n"
            f"Вам было отправлено {amount}₽.\n\n"
            f"💸 Спасибо, что работаете с нами!",
        )
    except Exception as e:
        log.error(f"Ошибка отправки сообщения пользователю {partner_tg_id}: {e}")

    await callback_query.message.delete()

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


# --- Уведомления


@admin_r.callback_query(
    F.data == "notifications",
)
async def data_notifications(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик кнопки 'Уведомления'"""
    await callback_query.answer(text="🔔 Уведомления", show_alert=False)

    tg_id = callback_query.from_user.id
    current_state = AdminState.default.state

    data = await state.get_data()
    global_state_data: dict = data.get("global_state_data", {})
    # interval = global_state_data.get("interval")
    interval = await admin_data.get_new_orders_notification_interval()
    support_link = global_state_data.get("support_link")

    text = (
        f"🔔 <b>Уведомления</b>\n\n"
        f"Новые заказы: <b>{interval} сек</b>\n"
        f"Поддержка: <b>{support_link}</b>"
    )

    reply_kb = await kb.get_admin_kb("notifications")

    await callback_query.message.edit_text(
        text=text,
        reply_markup=reply_kb,
        disable_web_page_preview=True,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.callback_query(
    F.data == "change_interval",
)
async def change_interval(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик кнопки 'Изменить интервал'"""

    tg_id = callback_query.from_user.id
    current_state = AdminState.change_interval.state

    await callback_query.message.answer(
        text="Задайте интервал в секундах:",
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.callback_query(
    F.data == "change_support_link",
)
async def change_support_link(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик кнопки 'Изменить ссылку поддержки'"""

    tg_id = callback_query.from_user.id
    current_state = AdminState.change_support_link.state

    await callback_query.message.answer(
        text="Задайте новую ссылку:",
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


@admin_r.message(
    StateFilter(AdminState.change_interval),
)
async def confirm_interval(
    message: Message,
    state: FSMContext,
):
    """Принимает изменения изменения интервала"""

    tg_id = message.from_user.id
    current_state = AdminState.default.state
    new_interval = message.text.strip()

    try:
        new_interval = int(new_interval)
        if new_interval > 10:
            await admin_data.change_new_orders_notification_interval(
                interval_seconds=new_interval
            )
            await message.answer(
                text=f"Новый интервал уведомлений: {new_interval} сек",
                parse_mode="HTML",
            )

            await state.set_state(current_state)
            await rediska.set_state(admin_bot_id, tg_id, current_state)

        else:
            await message.answer("Введите число побольше:")
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число.")


@admin_r.message(
    StateFilter(AdminState.change_support_link),
)
async def confirm_link(
    message: Message,
    state: FSMContext,
):
    """Принимает изменения изменения интервала"""

    tg_id = message.from_user.id
    current_state = AdminState.change_support_link.state
    new_link = message.text.strip()

    await admin_data.change_support_link(link=new_link)

    await message.answer(
        text=f"Новая ссылка поддержки: {new_link}",
        disable_notification=True,
        disable_web_page_preview=True,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(admin_bot_id, tg_id, current_state)


# ---
# ---
# ---


@admin_r.message()
async def handle_unrecognized_message(
    message: Message,
):
    """Обрабатывает нераспознанные сообщения."""

    await message.delete()
