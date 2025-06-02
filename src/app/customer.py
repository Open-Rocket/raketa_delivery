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
    ReplyKeyboardRemove,
    defaultdict,
    time,
    Time,
    zlib,
    SUPER_ADMIN_TG_ID,
    handler,
    customer_bot,
    courier_bot,
    partner_bot,
    customer_bot_id,
    customer_r,
    customer_fallback,
    kb,
    title,
    customer_data,
    courier_data,
    admin_data,
    order_data,
    recognizer,
    rediska,
    assistant,
    gemini_assistant,
    formatter,
    cities,
    log,
    randint,
    find_closest_city,
    delete_message_after_delay,
    F,
)


# ---
# ---


@customer_r.message(
    CommandStart(),
)
async def cmd_start_customer(
    message: Message,
    state: FSMContext,
):
    """Обработчик команды /start для клиента."""

    tg_id = message.from_user.id
    is_reg = await rediska.is_reg(customer_bot_id, tg_id)
    new_message = None

    _ = await customer_data.check_click_customer(tg_id)

    if is_reg:
        current_state = CustomerState.default.state
        await message.answer(
            text=f"▼ <b>Выберите действие в • ≡ Меню •</b>",
            disable_notification=True,
            parse_mode="HTML",
        )

    else:
        current_state = CustomerState.reg_state.state
        photo_title = await title.get_title_customer("/start")
        text = (
            "Raketa — современный сервис доставки с минимальными ценами и удобством использования.\n\n"
            "Почему выбирают нас?\n\n"
            "◉ Низкие цены:\n"
            "Мы не берем комиссию с курьеров, что позволяет нам снижать цену доставки для клиентов.\n\n"
            "◉ Простота и удобство:\n"
            "С помощью ИИ вы можете легко и быстро оформить заказ и сразу отправить его на выполнение."
        )
        reply_kb = await kb.get_customer_kb("/start")
        new_message = await message.answer_photo(
            photo=photo_title,
            caption=text,
            reply_markup=reply_kb,
            disable_notification=True,
            parse_mode="HTML",
        )

        check_click_courier = await courier_data.check_click_customer(
            tg_id=tg_id,
        )

        if check_click_courier:
            log.info(f"Клиент {tg_id} нажал по кнопке /start")

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)

    if new_message:
        await handler.catch(
            bot=customer_bot,
            chat_id=message.chat.id,
            user_id=tg_id,
            new_message=new_message,
            current_message=message,
            delete_previous=True,
        )


@customer_r.callback_query(
    F.data == "reg",
)
async def data_reg_customer(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик коллбэка 'reg' для клиента."""

    await callback_query.answer("✍️ Регистрация", show_alert=False)

    current_state = CustomerState.reg_Name.state
    tg_id = callback_query.from_user.id

    text = (
        "Пройдите небольшую регистрацию.\n"
        "Это не займет много времени.\n\n"
        "<b>Как вас зовут?</b>"
    )

    new_message = await callback_query.message.answer(
        text=text,
        disable_notification=True,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)

    await handler.catch(
        bot=customer_bot,
        chat_id=callback_query.message.chat.id,
        user_id=tg_id,
        new_message=new_message,
        current_message=None,
        delete_previous=True,
    )


@customer_r.message(
    filters.StateFilter(
        CustomerState.reg_Name,
    ),
)
async def data_name_customer(
    message: Message,
    state: FSMContext,
):
    """Обработчик состояния 'CustomerState.reg_Name'."""

    current_state = CustomerState.reg_Phone.state
    tg_id = message.from_user.id
    customer_name = message.text
    reply_kb = await kb.get_customer_kb("phone_number")
    text = (
        f"Привет, {customer_name}!👋\n\nЧтобы мы могли быстро оформить заказ и курьер смог связаться с вами "
        f"в случае необходимости, пожалуйста, нажмите на кнопку 'Поделиться номером'!\n\n"
        f"<i>*Нажмите на значок команд рядом с полем ввода, справа ->.</i>\n\n"
        f"<b>⚡️ Отправка номера возможно только по клику на кнопку 'Поделиться номером'!</b>\n\n"
        f"<i>Если у вас возникли сложности с отправкой посмотрите</i> <a href='https://t.me/ruslanrocketman/43'>инструкцию</a>\n\n"
        f"<b>Ваш номер:</b>"
    )
    new_message = await message.answer(
        text=text,
        reply_markup=reply_kb,
        disable_notification=True,
        disable_web_page_preview=True,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)
    await rediska.set_name(customer_bot_id, tg_id, customer_name)

    await handler.catch(
        bot=customer_bot,
        chat_id=message.chat.id,
        user_id=tg_id,
        new_message=new_message,
        current_message=message,
        delete_previous=True,
    )


@customer_r.message(
    filters.StateFilter(
        CustomerState.reg_Phone,
    ),
)
async def data_phone_customer(
    message: Message,
    state: FSMContext,
):
    """Обработчик состояния 'CustomerState.reg_Phone'."""

    current_state = CustomerState.reg_City.state
    tg_id = message.from_user.id
    customer_phone = message.contact.phone_number

    text = (
        f"Последний шаг!\n\n"
        f"Для того чтобы каждый раз не указывать город доставки, "
        f"скажите, в каком городе вы будете в основном делать заказы, "
        f"и он автоматически будет подставляться.\n\n"
        f"<i>Доступны только города РФ.</i>\n\n"
        f"<b>Ваш город:</b>"
    )

    new_message = await message.answer(
        text=text,
        disable_notification=True,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)
    await rediska.set_phone(customer_bot_id, tg_id, customer_phone)

    await handler.catch(
        bot=customer_bot,
        chat_id=message.chat.id,
        user_id=tg_id,
        new_message=new_message,
        current_message=message,
        delete_previous=True,
    )


@customer_r.message(
    filters.StateFilter(
        CustomerState.reg_City,
    ),
)
async def data_city_customer(
    message: Message,
    state: FSMContext,
):
    """Обработчик состояния 'CustomerState.reg_City'."""

    tg_id = message.from_user.id
    russian_cities = await cities.get_cities()
    city, _ = await find_closest_city(message.text, russian_cities)

    if not city:

        new_message = await message.answer(
            text=f"Введите корректное название города!\n\n<b>Ваш город:</b>",
            disable_notification=True,
            parse_mode="HTML",
        )

    else:

        current_state = CustomerState.reg_tou.state
        reply_kb = await kb.get_customer_kb("accept_tou")
        text = (
            f"Начиная использование сервиса, вы соглашаетесь с "
            f"<a href='https://disk.yandex.ru/i/rFtwNvr9bguSLw'>"
            f"Пользовательским соглашением и правилами использования</a>, а также "
            f"<a href='https://telegram.org/privacy'>Политикой конфиденциальности</a>.\n\n"
            f"<i>*Обращаем внимание, что любые действия, связанные с заказами, "
            f"отправкой или получением посылок, должны соответствовать законодательству "
            f"вашего государства и общепринятым этическим нормам.</i>\n\n"
        )
        new_message = await message.answer(
            text=text,
            reply_markup=reply_kb,
            disable_notification=True,
            disable_web_page_preview=True,
            parse_mode="HTML",
        )

        await state.set_state(current_state)
        await rediska.set_state(customer_bot_id, tg_id, current_state)
        await rediska.set_city(customer_bot_id, tg_id, city)

    await handler.catch(
        bot=customer_bot,
        chat_id=message.chat.id,
        user_id=tg_id,
        new_message=new_message,
        current_message=message,
        delete_previous=True,
    )


@customer_r.callback_query(
    F.data == "accept_tou",
)
async def customer_accept_tou(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик коллбэка 'accept_tou' для клиента."""

    tg_id = callback_query.from_user.id
    accept_tou = (
        "Пользовательское соглашение и правила использования сервиса - Принимаю"
    )
    reply_kb = await kb.get_customer_kb("accept_tou")
    tou_text = (
        f"Начиная использование сервиса, вы соглашаетесь с "
        f"<a href='https://disk.yandex.ru/i/rFtwNvr9bguSLw'>"
        f"Пользовательским соглашением и правилами использования</a>, а также "
        f"<a href='https://telegram.org/privacy'>Политикой конфиденциальности</a>.\n\n"
        f"<i>*Обращаем внимание, что любые действия, связанные с заказами, "
        f"отправкой или получением посылок, должны соответствовать законодательству "
        f"вашего государства и общепринятым этическим нормам.</i>\n\n"
    )
    customer_name, customer_phone, customer_city = await rediska.get_user_info(
        customer_bot_id, tg_id
    )
    is_set_reg = await rediska.set_reg(
        customer_bot_id,
        tg_id,
        True,
    )

    is_set_customer_to_db = await customer_data.set_customer(
        tg_id,
        customer_name,
        customer_phone,
        customer_city,
        accept_tou,
    )

    if is_set_reg and is_set_customer_to_db:

        current_state = CustomerState.default.state
        await callback_query.answer("✅ Принято", show_alert=False)

        text = (
            f"Вы успешно зарегистрировались! 🎉\n\n"
            f"Имя: {customer_name}\n"
            f"Номер: {customer_phone}\n"
            f"Город: {customer_city}\n\n"
            f"<i>Введите PROMOKOD для активации скидки на первый заказ</i> /promo\n\n"
            f"<a href='https://t.me/raketadeliverychannel/22'>Инструкция</a>\n\n"
            f"▼ <b>Выберите действие в • ≡ Меню •</b>"
        )

        new_customers_info = (
            "Добро пожаловать!\n\n"
            "Это сервис, который быстро и удобно связывает вас с курьерами.\n\n"
            "<b>Преимущества:</b>\n"
            "• Цены в 2 раза ниже, чем у обычных доставок.\n"
            "• Заказ — в 10 раз проще с помощью ИИ.\n"
            "• Telegram-бот уже работает как полноценное приложение.\n"
            "• Скоро появятся нативные версии для Android и iOS.\n\n"
            "<b>Что можно доставить:</b>\n"
            "• p2p — личные поручения: ключи, документы, покупки.\n"
            "• b2c — доставка из магазинов и сервисов.\n\n"
            "⚡️ <b>Только легальные заказы. Без странностей и нарушений.</b>\n\n"
        )

        await callback_query.message.answer(
            text=new_customers_info,
            disable_notification=False,
            disable_web_page_preview=True,
            parse_mode="HTML",
        )
        new_message = await callback_query.message.answer(
            text=text,
            disable_notification=False,
            disable_web_page_preview=True,
            parse_mode="HTML",
        )

        await state.set_state(current_state)
        await rediska.set_state(customer_bot_id, tg_id, current_state)

    else:

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

    await handler.catch(
        bot=customer_bot,
        chat_id=callback_query.message.chat.id,
        user_id=tg_id,
        new_message=new_message,
        current_message=None,
        delete_previous=True,
    )


# ---
# ---


@customer_r.message(
    filters.StateFilter(CustomerState.ai_voice_order),
    F.content_type.in_([ContentType.VOICE, ContentType.TEXT]),
)
async def process_order(
    message: Message,
    state: FSMContext,
):
    """Обработчик заказа клиента."""

    start_time = time.perf_counter()

    current_state = CustomerState.assistant_run.state
    tg_id = message.from_user.id

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)

    wait_message = await message.answer(
        "🧿 Заказ обрабатывается, подождите ...",
        disable_notification=True,
    )

    if message.content_type == ContentType.VOICE:

        recognized_text = await recognizer.get_recognition_text(message)

        if not recognized_text:
            await _handle_error_response(
                message,
                wait_message,
                "unrecognized",
                state,
            )
            return

        text_msg = recognized_text
    else:
        text_msg = message.text

    try:

        await asyncio.wait_for(
            _process_order_logic(
                text_msg,
                message,
                state,
                wait_message,
            ),
            timeout=60,
        )
    except asyncio.TimeoutError:
        await _handle_error_response(
            message,
            wait_message,
            "timeout",
            state,
        )
        log.error("Error: asyncio.TimeoutError")
    except Exception as e:
        await _handle_error_response(
            message,
            wait_message,
            "general",
            state,
        )
        log.error(f"Error: {e}")

    execution_time = time.perf_counter() - start_time
    log.info(f"Execution time process_message: {execution_time:.4f} sec")


async def _process_order_logic(
    text_msg: str,
    message: Message,
    state: FSMContext,
    wait_message: Message,
):
    """Логика обработки заказа клиента."""

    current_state = CustomerState.assistant_run.state
    tg_id = message.from_user.id
    customer_name, customer_phone, customer_city = await rediska.get_user_info(
        customer_bot_id,
        tg_id,
    )
    moscow_time = await Time.get_moscow_time()

    try:
        is_moderation, city, addresses, delivery_object, description = (
            await assistant.process_order(
                text_msg,
                customer_city,
            )
        )

        # log.info(f"moderation status: {is_moderation}")

        if is_moderation is False:
            await _handle_error_response(
                message,
                wait_message,
                "moderation_failed",
                state,
            )
            return

        if city is None:
            await _handle_error_response(
                message,
                wait_message,
                "general",
                state,
            )
            log.error(f"Error: {e}")
            return

    except Exception as e:
        await _handle_error_response(
            message,
            wait_message,
            "general",
            state,
        )
        log.error(f"Error: {e}")
        return

    prepare_dict = await formatter._prepare_data(
        time=moscow_time,
        customer_name=customer_name,
        customer_phone=customer_phone,
        city=city,
        addresses=addresses,
        delivery_object=delivery_object,
        description=description,
    )

    if not prepare_dict:
        await _handle_error_response(
            message,
            wait_message,
            "general",
            state,
        )
        return

    customer_discount = await customer_data.get_customer_discount(tg_id)

    order_info_data = await formatter.format_order_form(
        prepare_dict,
        customer_discount,
    )

    show_discount = False

    if len(order_info_data) == 4:
        order_info, price, discount_price, hide_phone_info = order_info_data
        prepare_dict["price"] = discount_price
        show_discount = True

    elif len(order_info_data) == 2:
        order_info, hide_phone_info = order_info_data
        show_discount = False

    reply_kb = await kb.get_customer_kb("voice_order_accept")

    await message.answer(
        text=f"Проверяйте правильность заказа!",
        disable_notification=True,
        parse_mode="HTML",
    )

    await message.answer(
        text=order_info,
        reply_markup=reply_kb,
        disable_notification=False,
        disable_web_page_preview=True,
        parse_mode="HTML",
    )

    if show_discount:
        await message.answer(
            text=f"🪙 Ваша скидка 50% = <s>{price}₽</s> {discount_price}₽",
            disable_notification=True,
            parse_mode="HTML",
        )

    if wait_message:
        await wait_message.delete()

    await state.set_state(current_state)
    await state.update_data(
        current_order_info=(
            prepare_dict,
            order_info,
            hide_phone_info,
        )
    )
    await rediska.set_state(customer_bot_id, tg_id, current_state)
    await rediska.save_fsm_state(state, customer_bot_id, tg_id)


async def _handle_error_response(
    message: Message,
    wait_message: Message,
    error_key: str,
    state: FSMContext,
):
    """Функция для обработки и отправки сообщения об ошибке."""

    current_state = CustomerState.default.state
    tg_id = message.from_user.id

    error_messages = {
        "general": "<b>‼️ Ошибка при обработке заказа!</b>\n\nПопробуйте снова",
        "timeout": "<b>‼️ Превышено время ожидания!</b>\n\nПопробуйте снова",
        "unrecognized": "<b>‼️ Не удалось распознать голосовое сообщение!</b>\n\nПопробуйте снова",
        "moderation_failed": (
            "<b>‼️ Модерация не прошла!</b>\n\n"
            "Ваше сообщение не соответствует требованиям сервиса.\n\n"
            "⛔ Запрещено:\n"
            "— вызывать такси,\n"
            "— заказывать доставку табака, вейпов, алкоголя,\n"
            "— передавать наркотики или любые товары, противоречащие законодательству.\n"
            "— Вести общение не по теме заказа.\n\n"
            "Пожалуйста, оформите <b>законный и допустимый заказ на доставку или поручение</b> в пределах города.\n"
            "Попробуйте снова"
        ),
    }

    reply_kb = await kb.get_customer_kb("rerecord")

    if wait_message:
        await wait_message.delete()

    await message.answer(
        error_messages[error_key],
        reply_markup=reply_kb,
        disable_notification=False,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)

    log.warning(f"Error response sent: {error_key}")


# ---


@customer_r.callback_query(
    F.data == "order_sent_to_create_order",
)
async def set_order_to_db(callback_query: CallbackQuery, state: FSMContext):
    """Обработчик коллбэка 'order_sent_to_create_order' для клиента. Добавляет заказ в БД."""

    tg_id = callback_query.from_user.id
    current_state = CustomerState.default.state

    state_data = await state.get_data()

    # 🔐 Проверка на флаг: если заказ уже создаётся — выходим
    if state_data.get("order_in_progress"):
        await callback_query.answer(
            "⏳ Заказ уже создается. Подождите немного...", show_alert=False
        )
        return

    # 🛡️ Ставим флаг, чтобы защитить от повторного входа
    await state.update_data(order_in_progress=True)

    try:
        await callback_query.answer("🧾 Создаем заказ ...", show_alert=False)
        await asyncio.sleep(1)

        current_order_info = state_data.get("current_order_info")
        hide_phone_forma = state_data.get("hide_phone_info")

        if not current_order_info:
            log.error("Ключ 'current_order_info' отсутствует в состоянии FSM")
            await callback_query.answer(
                "‼️ Ошибка: данные заказа не найдены.",
                disable_notification=True,
                show_alert=True,
            )
            return

        data, order_forma, hide_phone_forma = [*current_order_info]
        order_forma = zlib.compress(order_forma.encode("utf-8"))
        hide_phone_forma = zlib.compress(hide_phone_forma.encode("utf-8"))

        order_number = await order_data.create_order(
            tg_id=tg_id,
            username=callback_query.from_user.username,
            data=data,
            order_forma=order_forma,
            hide_phone_forma=hide_phone_forma,
        )

        if not order_number:
            raise Exception("Ошибка при создании заказа")

        text = (
            f"Заказ <b>№{order_number}</b> успешно создан! 🎉\n"
            f"Мы ищем курьера для вашего заказа 🔎\n\n"
            f"<i>*Информацию о заказах можно посмотреть в разделе</i> <b>Мои заказы</b>.\n- /my_orders\n\n"
            f"▼ <b>Выберите действие в • ≡ Меню •</b>"
        )

        try:
            order_city = data.get("city")
            price_rub = data.get("price")
            description = data.get("description")
            yandex_maps_url = data.get("yandex_maps_url")
            routing_addresses = (
                f"⦿⌁⦿ <a href='{yandex_maps_url}'>Посмотреть маршрут заказа</a>"
                if yandex_maps_url != "-"
                else ""
            )

            all_couriers_tg_ids_in_order_city = await courier_data.get_all_couriers_tg_ids_notify_status_true_in_current_city(
                city=order_city
            )

            add_text = ""
            if int(price_rub) == 0:
                add_text = "\nЕсли цена не указана, то возможно это поручение, свяжитесь с заказчиком для уточнения деталей."

            notification_for_couriers = (
                f"📍 Город: <b>{order_city}</b>\n"
                f"💸 Новый заказ на сумму: <b>{price_rub}₽</b>\n"
                f"<i>{add_text}</i>\n\n"
                f"📦 Маршрут:\n{routing_addresses}\n\n"
                f"📄 <b>Описание:</b>\n{description}\n\n"
                f"●\n\n"
                f"🚀 <b>Начать работу!</b> — /run"
            )

            for courier_tg_id in all_couriers_tg_ids_in_order_city:
                try:
                    msg = await courier_bot.send_message(
                        chat_id=courier_tg_id,
                        text=notification_for_couriers,
                        disable_web_page_preview=True,
                        parse_mode="HTML",
                    )

                    asyncio.create_task(
                        delete_message_after_delay(
                            courier_bot,
                            courier_tg_id,
                            msg.message_id,
                            delay=900,
                        )
                    )
                except Exception as e:
                    log.error(
                        f"Ошибка при отправке уведомления курьеру {courier_tg_id}: {e}"
                    )

        except Exception as e:
            log.error(f"Ошибка при рассылке курьерам: {e}")

        await callback_query.message.answer(
            text=text,
            disable_notification=True,
            parse_mode="HTML",
        )

        await callback_query.answer("🧾 Заказ создан", show_alert=False)
        await callback_query.message.delete()

        await customer_data.set_customer_discount(tg_id, 0)

        await state.set_state(current_state)
        await rediska.set_state(customer_bot_id, tg_id, current_state)

    except Exception as e:
        log.error(f"Ошибка при создании заказа: {str(e)}")
        await callback_query.answer(
            "‼️ Ошибка при создании заказа. Попробуйте позже.", show_alert=True
        )

    finally:
        # 🧹 Обязательно убираем замок!
        await state.update_data(order_in_progress=False)


@customer_r.callback_query(
    F.data == "cancel_order",
)
async def cancel_order(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик коллбэка 'cancel_order' для клиента. Отменяет заказ."""

    await callback_query.answer("⃠ Заказ не размещен", show_alert=False)

    current_state = CustomerState.default.state
    tg_id = callback_query.from_user.id

    await callback_query.message.answer(
        text=f"▼ <b>Выберите действие в • ≡ Меню •</b>",
        disable_notification=True,
        parse_mode="HTML",
    )

    await callback_query.message.delete()

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)


# ---
# ---


@customer_r.message(
    F.text == "/order",
)
async def cmd_order(
    message: Message,
    state: FSMContext,
):
    """Обработчик команды /order для клиента."""

    tg_id = message.from_user.id
    is_read_info = await rediska.is_read_info(customer_bot_id, tg_id)
    is_set_key = await customer_data.is_set_key(tg_id)

    log.info(f"set_key: {is_set_key}")

    is_block = await admin_data.get_customer_block_status(tg_id=tg_id)

    if is_block:
        await message.answer(
            text="🚫 <b>Вы были заблокированы и не можете больше делать заказы!</b>",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="HTML",
        )
        return

    if is_read_info:

        current_state = CustomerState.ai_voice_order.state
        text = (
            f"<i>*Вы можете отправить как голосовое сообщение, так и текстовое — "
            f"заказ будет оформлен в считанные секунды.</i>\n\n"
            f"<b>⚡️ Обязательно указывайте точные адреса, а не только название объектов, от этого зависит правильность маршрута!</b>\n\n"
            f"ゞ <b>Опишите ваш заказ ...</b>"
        )
        await message.answer(
            text=text,
            disable_notification=True,
            parse_mode="HTML",
        )

    else:

        current_state = CustomerState.default.state
        photo_title = await title.get_title_customer("/order")
        reply_kb = await kb.get_customer_kb("/order")
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

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)


@customer_r.callback_query(
    F.data == "ai_order",
)
async def data_ai(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик коллбэка 'ai_order' для клиента."""

    await callback_query.answer("🤖 ИИ ассистент готов принять заказ", show_alert=False)

    current_state = CustomerState.ai_voice_order.state
    tg_id = callback_query.from_user.id
    is_read_info = await rediska.is_read_info(customer_bot_id, tg_id)

    _, _, customer_city = await customer_data.get_customer_info(tg_id=tg_id)

    if is_read_info:
        text = (
            f"<i>*Вы можете отправить как голосовое сообщение, так и текстовое — "
            f"заказ будет оформлен в считанные секунды.</i>\n\n"
            f"<b>⚡️ Обязательно указывайте точные адреса, а не только название объектов, от этого зависит правильность маршрута!</b>\n\n"
            f"ゞ <b>Опишите ваш заказ ...</b>"
        )

    else:
        text = (
            f"<i>*Вы можете отправить как голосовое сообщение так и текстовое, "
            f"заказ будет оформлен в считанные секунды.</i>\n\n"
            f"<b>Пример:</b>\n"
            f"<code>Нужно сделать доставку документов с улицы Арбат дом 12  строение 1  подъезд 1 квартира 6 "
            f"и отвезти на Пресненскую набережную, дом 10, офис 417.</code>\n\n"
            f"👆 <i>Нажмите чтобы скопировать</i>\n\n"
            f"<i>Можете использовать текст выше в качестве шаблона или описать заказ так как вам удобно. *ИИ готов принять заказ</i>\n\n"
            f"<b>⚡️ Обязательно указывайте точные адреса, а не только название объектов, от этого зависит правильность маршрута!</b>\n\n"
            f"ゞ <b>Опишите ваш заказ ...</b>"
        )

    await callback_query.message.answer(
        text=text,
        disable_notification=True,
        parse_mode="HTML",
    )

    await callback_query.message.delete()

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)
    await rediska.set_read_info(customer_bot_id, tg_id, True)


# ---
# ---


@customer_r.message(
    F.text == "/promo",
)
async def cmd_promo(
    message: Message,
    state: FSMContext,
):
    """Обработчик команды /promo для клиента."""

    current_state = CustomerState.default.state
    tg_id = message.from_user.id
    data = await state.get_data()

    customer_seed_key = await customer_data.get_customer_seed_key(tg_id)

    if customer_seed_key:
        text = (
            f"🎉 <b>PROMOKOD</b>\n\n"
            f"Вы являетесь участником PROMO акций!\n\n"
            f"Ваш PROMOKOD: <code>{customer_seed_key}</code>"
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

        reply_kb = await kb.get_customer_kb("promo")

        promo_msg = await message.answer(
            text=text,
            reply_markup=reply_kb,
            disable_notification=True,
            parse_mode="HTML",
        )

        try:
            promo_msg_id = data.get("promo_msg_id")
            if promo_msg_id:
                await message.bot.delete_message(
                    chat_id=tg_id,
                    message_id=promo_msg_id,
                )
                await state.update_data(promo_msg_id=None)
                await rediska.save_fsm_state(state, customer_bot_id, tg_id)
                await message.delete()
        except Exception as e:
            log.warning(f"Не удалось удалить сообщение: {e}")

        await state.update_data(promo_msg_id=promo_msg.message_id)

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)


@customer_r.callback_query(
    F.data == "PROMOKOD",
)
async def data_set_PROMOKOD(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик коллбэка 'PROMOKOD' для клиента."""

    tg_id = callback_query.from_user.id
    await callback_query.answer("🎉 PROMOKOD", show_alert=False)

    is_set_key = await customer_data.is_set_key(tg_id)

    if is_set_key:
        text = f"Вы уже применили свой PROMOKOD!\n\n"
    else:
        current_state = CustomerState.set_seed_key.state
        text = f"Ваш PROMOKOD:"

    await callback_query.message.answer(
        text=text,
        disable_notification=True,
        parse_mode="HTML",
    )

    await callback_query.message.delete()

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)


@customer_r.message(
    filters.StateFilter(CustomerState.set_seed_key),
)
async def data_PROMOKOD(
    message: Message,
    state: FSMContext,
):
    """Обработчик состояния 'CustomerState.set_seed_key'."""

    current_state = CustomerState.default.state
    tg_id = message.from_user.id
    seed_key = message.text.strip().upper()

    (
        partner_tg_id,
        _,
        _,
    ) = await admin_data.get_partner_full_info_by_SEED(seed=seed_key)

    if partner_tg_id == None:

        text = "‼️ Ошибка при установке PROMOKOD-а\n\nВозможно такого промокода не существует!"
        await message.answer(
            text=text,
            parse_mode="HTML",
        )

        await state.set_state(current_state)
        await rediska.set_state(customer_bot_id, tg_id, current_state)

        return

    if tg_id != SUPER_ADMIN_TG_ID:
        if tg_id == partner_tg_id:
            await message.answer(
                text="Вы не можете быть рефералом самому себе, используйте другой PROMOKOD!",
                parse_mode="HTML",
            )

            await state.set_state(current_state)
            await rediska.set_state(customer_bot_id, tg_id, current_state)

            return

    is_set_key = await customer_data.set_customer_seed_key(tg_id, seed_key)

    log.info(f"is_set_key: {is_set_key}")

    discount = await admin_data.get_first_order_discount()

    if is_set_key:
        await customer_data.set_customer_discount(tg_id, discount)
        text = f"✅ PROMOKOD успешно установлен!\n\nСкидка на следующий заказ <b>{discount}%</b>"

        (
            partner_tg_id,
            balance,
            is_blocked,
        ) = await admin_data.get_partner_full_info_by_SEED(seed=seed_key)

        partner_program_status = await admin_data.get_partner_program_status()

        if partner_program_status:
            if not is_blocked:
                await partner_bot.send_message(
                    chat_id=partner_tg_id,
                    text=f"Вашим ключем <b>{seed_key}</b> только что воспользовались!👍\nПродолжайте в том же духе!",
                    disable_notification=True,
                    parse_mode="HTML",
                )

    else:
        text = "‼️ Ошибка при установке PROMOKOD-а\n\nВозможно такого промокода не существует!"

    await message.answer(
        text=text,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)


# ---
# ---


@customer_r.message(
    F.text == "/profile",
)
async def cmd_profile(
    message: Message,
    state: FSMContext,
):
    """Обработчик команды /profile для клиента."""

    current_state = CustomerState.default.state
    tg_id = message.from_user.id
    data = await state.get_data()

    await title.get_title_customer(message.text)
    name, phone, city = await rediska.get_user_info(
        customer_bot_id,
        tg_id,
    )
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

    my_profile_msg = await message.answer(
        text=text,
        reply_markup=reply_kb,
        disable_notification=True,
        parse_mode="HTML",
    )

    try:
        my_profile_msg_id = data.get("my_profile_msg_id")
        if my_profile_msg_id:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=my_profile_msg_id,
            )
            await state.update_data(my_profile_msg_id=None)
            await rediska.save_fsm_state(state, customer_bot_id, tg_id)
            await message.delete()
    except Exception as e:
        log.warning(f"Не удалось удалить сообщение: {e}")

    await state.update_data(my_profile_msg_id=my_profile_msg.message_id)

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)


@customer_r.message(
    F.text == "/info",
)
async def cmd_info(
    message: Message,
    state: FSMContext,
):
    """Обработчик команды /info."""

    current_state = CustomerState.default.state
    tg_id = message.from_user.id
    data = await state.get_data()

    text = (
        f"ℹ️ <b>Информация</b>\n\n"
        f"Здесь вы можете ознакомиться с основной информацией о сервисе, задать вопрос или предложить свою идею!\n\n"
        f"<a href='https://disk.yandex.ru/i/PGll6-rJV7QhNA'>О Нас 'Raketa'</a>\n"
        f"<a href='https://disk.yandex.ru/i/NiwitOTuU0YPXQ'>Частые вопросы и ответы на них</a>\n"
        f" •\n"
        f"<a href='https://t.me/raketadeliverychannel/14'>Вопросы - Обсуждения - Предложения</a>\n"
        f"<a href='https://t.me/raketadeliverychannel/22'>Инструкция</a>"
    )

    info_msg = await message.answer(
        text=text,
        disable_notification=True,
        disable_web_page_preview=True,
        parse_mode="HTML",
    )

    try:
        info_msg_id = data.get("info_msg_id")
        if info_msg_id:
            await message.bot.delete_message(
                chat_id=tg_id,
                message_id=info_msg_id,
            )
            await state.update_data(info_msg_id=None)
            await rediska.save_fsm_state(state, customer_bot_id, tg_id)
            await message.delete()
    except Exception as e:
        log.warning(f"Не удалось удалить сообщение: {e}")

    await state.update_data(info_msg_id=info_msg.message_id)

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)


@customer_r.message(
    F.text == "/rules",
)
async def cmd_rules(
    message: Message,
    state: FSMContext,
):
    """Обработчик команды /rules для клиента."""

    current_state = CustomerState.default.state
    tg_id = message.from_user.id
    data = await state.get_data()

    text = (
        f"⚖️ <b>Правила сервиса</b>\n\n"
        f"Начиная использование сервиса, вы соглашаетесь с "
        f"<a href='https://disk.yandex.ru/i/rFtwNvr9bguSLw'>"
        f"Пользовательским соглашением и правилами использования</a>, а также "
        f"<a href='https://telegram.org/privacy'>Политикой конфиденциальности</a>.\n\n"
        f"<i>*Обращаем внимание, что любые действия, связанные с заказами, "
        f"отправкой или получением посылок, должны соответствовать законодательству "
        f"вашего государства и общепринятым этическим нормам.</i>\n\n"
    )

    rules_msg = await message.answer(
        text=text,
        disable_notification=True,
        disable_web_page_preview=True,
        parse_mode="HTML",
    )

    try:
        rules_msg_id = data.get("rules_msg_id")
        if rules_msg_id:
            await message.bot.delete_message(
                chat_id=tg_id,
                message_id=rules_msg_id,
            )
            await state.update_data(rules_msg_id=None)
            await rediska.save_fsm_state(state, customer_bot_id, tg_id)
            await message.delete()
    except Exception as e:
        log.warning(f"Не удалось удалить сообщение: {e}")

    await state.update_data(rules_msg_id=rules_msg.message_id)

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)


@customer_r.message(
    F.text == "/channel",
)
async def cmd_channel(
    message: Message,
    state: FSMContext,
):
    """Обрабатывает запрос на переход в телеграмм канал. /channel"""

    current_state = CustomerState.default.state
    tg_id = message.from_user.id
    data = await state.get_data()

    text = (
        f"📺 <b>Официальный канал Raketa Delivery</b>\n\n"
        f"🔹 <b>Актуальные новости</b> сервиса и важные объявления\n"
        f"🔹 <b>Полезные советы</b> для курьеров и партнеров\n"
        f"🔹 <b>Информация</b> о новых функциях и возможностях\n\n"
        f"🚀 <b>Подписывайтесь, чтобы быть в курсе всех обновлений!</b>\n\n"
    )

    reply_kb = await kb.get_customer_kb("/channel")

    channel_msg = await message.answer(
        text=text,
        reply_markup=reply_kb,
        disable_notification=True,
        parse_mode="HTML",
    )

    try:
        channel_msg_id = data.get("channel_msg_id")
        if channel_msg_id:
            await message.bot.delete_message(
                chat_id=tg_id,
                message_id=channel_msg_id,
            )
            await state.update_data(channel_msg_id=None)
            await rediska.save_fsm_state(state, customer_bot_id, tg_id)
            await message.delete()
    except Exception as e:
        log.warning(f"Не удалось удалить сообщение: {e}")

    await state.update_data(channel_msg_id=channel_msg.message_id)

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)


@customer_r.message(
    F.text == "/become_courier",
)
async def cmd_become_courier(
    message: Message,
    state: FSMContext,
):
    """Обработчик команды /become_courier для клиента."""

    current_state = CustomerState.default.state
    tg_id = message.from_user.id
    data = await state.get_data()

    photo_title = await title.get_title_customer("/become_courier")
    text = (
        f"📦 <b>Стать курьером у нас</b> — это отличный способ заработать без комиссии! 💸\n\n"
        f"⏰ <b>Работайте в удобное время</b>, выбирайте заказы рядом и получайте бонусы за быструю доставку 🏃‍♂️💨\n\n"
        f"💰 <b>Зарабатывайте от 5000₽ в день</b> уже сегодня!"
    )
    reply_kb = await kb.get_customer_kb("/become_courier")

    become_courier_msg = await message.answer_photo(
        photo=photo_title,
        caption=text,
        reply_markup=reply_kb,
        disable_notification=True,
        parse_mode="HTML",
    )

    try:
        become_courier_msg_id = data.get("become_courier_msg_id")
        if become_courier_msg_id:
            await message.bot.delete_message(
                chat_id=tg_id,
                message_id=become_courier_msg_id,
            )
            await state.update_data(become_courier_msg_id=None)
            await rediska.save_fsm_state(state, customer_bot_id, tg_id)
            await message.delete()
    except Exception as e:
        log.warning(f"Не удалось удалить сообщение: {e}")

    await state.update_data(become_courier_msg_id=become_courier_msg.message_id)

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)


@customer_r.message(
    F.text == "/become_partner",
)
async def cmd_become_partner(
    message: Message,
    state: FSMContext,
):
    """Обрабатывает запрос на переход в бота для партнеров. /become_partner"""

    current_state = CustomerState.default.state
    tg_id = message.from_user.id
    data = await state.get_data()

    refund_percent = await admin_data.get_refund_percent()

    text = (
        f"💼 <b>Станьте партнёром Raketa Delivery!</b>\n\n"
        f"🚀 <b>Зарабатывайте на привлечении курьеров и клиентов!</b>\n\n"
        f"🔹 Приглашайте курьеров и получайте <b>{refund_percent}%</b> с их подписки\n"
        f"🔹 Продвигайте сервис среди клиентов и увеличивайте свои доходы\n"
        f"🔹 Работайте когда хотите — без вложений и рисков!\n\n"
        f"💰 Чем больше курьеров — тем больше доход! Присоединяйтесь!"
    )
    ttl = await title.get_title_customer("/become_partner")
    reply_kb = await kb.get_customer_kb("/become_partner")

    partners_msg = await message.answer_photo(
        photo=ttl,
        caption=text,
        reply_markup=reply_kb,
        disable_notification=True,
        parse_mode="HTML",
    )

    try:
        partners_msg_id = data.get("partners_msg_id")
        if partners_msg_id:
            await message.bot.delete_message(
                chat_id=tg_id,
                message_id=partners_msg_id,
            )
            await state.update_data(partners_msg_id=None)
            await rediska.save_fsm_state(state, customer_bot_id, tg_id)
            await message.delete()
    except Exception as e:
        log.warning(f"Не удалось удалить сообщение: {e}")

    await state.update_data(partners_msg_id=partners_msg.message_id)

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)


# ---


@customer_r.message(
    F.text == "/notify",
)
async def cmd_notify(
    message: Message,
    state: FSMContext,
):
    """Обработчик команды /notify"""

    current_state = CustomerState.default.state
    tg_id = message.from_user.id
    data = await state.get_data()

    notify_status = await customer_data.get_customer_notify_status(tg_id=tg_id)

    log.info(f"notify status: {notify_status}")

    text = (
        f"Уведомления: {'<b>ON🔔</b>' if notify_status else '<b>OFF🔕</b>'}\n\n"
        f"{'<i>*Вы будете получать уведомления об активных курьерах и акциях сервиса!</i>' if notify_status else '<i>*Включите уведомления, чтобы получать информацию об активных курьерах и акциях сервиса!</i>'}\n\n"
    )

    reply_kb = await kb.get_turn_status_kb(
        "notify",
        status_notify=not notify_status,
    )

    notify_msg = await message.answer(
        text=text,
        reply_markup=reply_kb,
        disable_notification=True,
        parse_mode="HTML",
    )

    try:
        notify_msg_id = data.get("notify_msg_id")
        if notify_msg_id:
            await message.bot.delete_message(
                chat_id=tg_id,
                message_id=notify_msg_id,
            )
            await state.update_data(notify_msg_id=None)
            await rediska.save_fsm_state(state, customer_bot_id, tg_id)
            await message.delete()
    except Exception as e:
        log.warning(f"Не удалось удалить сообщение: {e}")

    await state.update_data(notify_msg_id=notify_msg.message_id)

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)


@customer_r.callback_query(
    F.data == "turn_on_notify",
)
@customer_r.callback_query(
    F.data == "turn_off_notify",
)
async def data_turn_on_notify(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик 'turn_on_notify' и 'turn_off_notify' для клиента."""

    tg_id = callback_query.from_user.id
    notify_status = await customer_data.get_customer_notify_status(tg_id=tg_id)

    log.info(f"notify status: {notify_status}")

    notify_status = not notify_status
    await customer_data.set_customer_notify_status(
        tg_id=tg_id,
        status=notify_status,
    )

    text = (
        f"Уведомления: {'<b>ON🔔</b>' if notify_status else '<b>OFF🔕</b>'}\n\n"
        f"{'<i>*Вы будете получать уведомления об активных курьерах и акциях сервиса.</i>' if notify_status else '<i>*Включите уведомления, чтобы получать информацию об активных курьерах и акциях сервиса.</i>'}\n\n"
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

    await state.set_state(CustomerState.default.state)
    await rediska.set_state(customer_bot_id, tg_id, CustomerState.default.state)


# ---


@customer_r.message(
    F.text == "/support",
)
async def cmd_support(
    message: Message,
    state: FSMContext,
):
    """Обработчик команды /support."""

    current_state = CustomerState.default.state
    tg_id = message.from_user.id
    data = await state.get_data()

    text = (
        f"👨‍💼 <b>Поддержка</b>\n\n"
        f"Если у вас возникли вопросы или проблемы, "
        f"вы можете обратиться в нашу службу поддержки.\n\n"
        f"<i>*Мы всегда готовы помочь вам!</i>"
    )

    reply_kb = await kb.get_customer_kb("/support")

    support_msg = await message.answer(
        text=text,
        reply_markup=reply_kb,
        disable_notification=True,
        parse_mode="HTML",
    )

    try:
        support_msg_id = data.get("support_msg_id")
        if support_msg_id:
            await message.bot.delete_message(
                chat_id=tg_id,
                message_id=support_msg_id,
            )
            await state.update_data(support_msg_id=None)
            await rediska.save_fsm_state(state, customer_bot_id, tg_id)
            await message.delete()
    except Exception as e:
        log.warning(f"Не удалось удалить сообщение: {e}")

    await state.update_data(support_msg_id=support_msg.message_id)

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)


# ---
# ---


@customer_r.message(
    F.text == "/my_orders",
)
@customer_r.callback_query(
    F.data == "back_myOrders",
)
async def cmd_my_orders(
    event: Message | CallbackQuery,
    state: FSMContext,
):
    """Обработчик команды /my_orders для клиента."""

    current_state = CustomerState.myOrders.state
    is_callback = isinstance(event, CallbackQuery)
    is_message = isinstance(event, Message)
    tg_id = event.from_user.id
    data = await state.get_data()

    if is_callback:
        await event.answer("↩️ Назад", show_alert=False)

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)

    pending_count = len(await order_data.get_pending_orders(tg_id))
    active_count = len(await order_data.get_active_orders(tg_id))

    reply_kb = await kb.get_customer_orders_kb(
        pending_count,
        active_count,
    )
    text = (
        f"📦 <b>Мои заказы</b>\n\n"
        f"Здесь вы можете посмотреть статус ваших заказов, "
        f"а также статистику за все время использования нашего сервиса.\n\n"
        f"<b>Статус ваших заказов:</b>"
    )

    if is_callback:
        await event.message.edit_text(
            text,
            reply_markup=reply_kb,
            disable_notification=True,
            parse_mode="HTML",
        )
    elif is_message:
        my_orders_message = await event.answer(
            text,
            reply_markup=reply_kb,
            disable_notification=True,
            parse_mode="HTML",
        )

        try:
            my_orders_message_id = data.get("my_orders_message_id")
            if my_orders_message_id:
                await event.bot.delete_message(
                    chat_id=event.chat.id, message_id=my_orders_message_id
                )
                await state.update_data(my_orders_message_id=None)
                await rediska.save_fsm_state(state, customer_bot_id, tg_id)
                await event.delete()
        except Exception as e:
            log.warning(f"Не удалось удалить сообщение: {e}")

        await state.update_data(my_orders_message_id=my_orders_message.message_id)

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)


@customer_r.callback_query(
    F.data.in_(
        [
            "pending_orders",
            "active_orders",
        ],
    )
)
async def get_my_orders(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик коллбэка для просмотра заказов клиента. pending_orders, active_orders, completed_orders"""

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

        courier_name = order.courier_name if order.courier_name else "..."
        courier_phone = order.courier_phone if order.courier_phone else "..."
        base_info = (
            f"<b>{index}/{len(customer_orders)}</b>\n"
            f"<b>Заказ: №{order.order_id}</b>\n"
            f"---------------------------------------------\n"
            f"<b>Курьер: </b>{courier_name}\n"
            f"<b>Телефон: </b>{courier_phone}\n"
            f"---------------------------------------------\n"
            f"{order_forma}"
        )
        orders_data[order.order_id] = {"text": base_info, "index": index - 1}

    if not orders_data:
        await callback_query.answer(
            f"У вас нет {status_text} заказов.",
            show_alert=False,
        )
        return
    else:

        if callback_query.data == "pending_orders":
            text_answer = "📋 Ожидающие"
        elif callback_query.data == "active_orders":
            text_answer = "📋 Активные"
        await callback_query.answer(text_answer, show_alert=False)

    first_order_id = list(orders_data.keys())[0]
    await state.update_data(
        orders_data=orders_data,
        counter=0,
        current_order_id=first_order_id,
    )

    await state.set_state(state_status)
    await rediska.save_fsm_state(state, customer_bot_id, tg_id)

    reply_kb = await kb.get_customer_kb("one" if len(orders_data) == 1 else "many")

    await callback_query.message.edit_text(
        orders_data[first_order_id]["text"],
        reply_markup=reply_kb,
        disable_notification=True,
        disable_web_page_preview=True,
        parse_mode="HTML",
    )


@customer_r.callback_query(
    F.data.in_(
        [
            "next_right_mo",
            "back_left_mo",
        ],
    ),
)
async def handle_order_navigation(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик коллбэка для навигации по заказам клиента. next_right_mo, back_left_mo"""

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

    if callback_query.data == "next_right_mo":
        counter = (counter + 1) % total_orders
        await callback_query.answer(f"{counter+1}/{total_orders} ⏩", show_alert=False)
    else:
        counter = (counter - 1) % total_orders
        await callback_query.answer(f"⏪ {counter+1}/{total_orders}", show_alert=False)

    current_order_id = order_ids[counter]

    await state.update_data(counter=counter, current_order_id=current_order_id)
    await rediska.save_fsm_state(state, bot_id, tg_id)

    try:
        await callback_query.message.edit_text(
            orders_data[current_order_id]["text"],
            reply_markup=callback_query.message.reply_markup,
            disable_web_page_preview=True,
            parse_mode="HTML",
        )

    except Exception as e:
        log.error(
            f"Ошибка при обновлении текста сообщения для заказа {current_order_id}: {e}"
        )
        await callback_query.answer(
            "Ошибка при обновлении информации о заказе.",
            show_alert=True,
        )


@customer_r.callback_query(
    F.data == "cancel_my_order",
)
async def cancel_my_order(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик коллбэка 'cancel_my_order' для клиента. Отменяет заказ."""

    tg_id = callback_query.from_user.id

    data = await state.get_data()
    current_order_id = data.get("current_order_id")

    if not current_order_id:
        log.warning("Не удалось найти current_order_id в состоянии FSM")
        await callback_query.message.answer(
            "Не удалось найти заказ для отмены.",
            parse_mode="HTML",
        )
        return

    order = await order_data.get_order_by_id(current_order_id)

    if not order:
        log.error(f"Заказ с ID {current_order_id} не найден в базе данных")
        await callback_query.message.answer(
            f"Заказ №{current_order_id} не найден.",
            parse_mode="HTML",
        )
        return

    current_order_status = order.order_status

    if order.order_status == OrderStatus.CANCELLED:
        await callback_query.message.answer(
            f"Заказ №{current_order_id} уже отменен.", disable_notification=False
        )
        await callback_query.message.delete()
        return

    try:

        is_update_order_status = await order_data.update_order_status(
            current_order_id, OrderStatus.CANCELLED
        )

        if not is_update_order_status:
            raise Exception("Ошибка при обновлении статуса заказа")

        text = (
            f"Заказ <b>№{current_order_id}</b> успешно отменён.\n\n"
            f"▼ <b>Выберите действие в • ≡ Меню •</b>"
        )
        await callback_query.message.answer(
            text=text,
            disable_notification=False,
            parse_mode="HTML",
        )

        if current_order_status == OrderStatus.IN_PROGRESS:
            courier_tg_id = await order_data.get_courier_tg_id_by_order_id(
                order_id=current_order_id
            )

            cancelled_message = f"❌ Клиент отменил заказ <b>№{current_order_id}</b>"

            await courier_bot.send_message(
                chat_id=courier_tg_id,
                text=cancelled_message,
                parse_mode="HTML",
            )

        await callback_query.answer("❌ Заказ отменен", show_alert=False)

        await callback_query.message.delete()

        await state.update_data(canceled_order_id=current_order_id)
        await rediska.save_fsm_state(state, customer_bot_id, tg_id)

    except Exception as e:
        log.error(f"Ошибка при отмене заказа {current_order_id}: {e}")
        await callback_query.answer(
            "Ошибка при отмене заказа.",
            show_alert=True,
        )


# ---
# ---


@customer_r.callback_query(
    F.data == "set_my_name",
)
async def set_name(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик коллбэка 'set_my_name' для клиента. Изменяет имя клиента."""

    await callback_query.answer("Изменить имя:", show_alert=False)

    current_state = CustomerState.change_Name.state
    tg_id = callback_query.from_user.id

    text = f"Изменить данные профиля.\n\n" f"<b>Ваше имя:</b>"
    await callback_query.message.answer(
        text=text,
        reply_markup=ReplyKeyboardRemove(),
        disable_notification=True,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)


@customer_r.callback_query(
    F.data == "set_my_phone",
)
async def set_phone(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик коллбэка 'set_my_phone' для клиента. Изменяет телефон клиента."""

    await callback_query.answer("Изменить телефон:", show_alert=False)

    current_state = CustomerState.change_Phone.state
    tg_id = callback_query.from_user.id

    reply_kb = await kb.get_customer_kb("phone_number")
    text = (
        f"Изменить данные профиля.\n\n"
        f"<i>Если у вас возникли сложности с отправкой посмотрите</i> <a href='https://t.me/ruslanrocketman/43'>инструкцию</a>\n\n"
        f"<b>Ваш Телефон:</b>"
    )
    await callback_query.message.answer(
        text=text,
        disable_notification=True,
        disable_web_page_preview=True,
        reply_markup=reply_kb,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)


@customer_r.callback_query(
    F.data == "set_my_city",
)
async def set_city(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обработчик коллбэка 'set_my_city' для клиента. Изменяет город клиента."""

    await callback_query.answer("Изменить город:", show_alert=False)

    current_state = CustomerState.change_City.state
    tg_id = callback_query.from_user.id

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)

    text = f"Изменить данные профиля.\n\n" f"<b>Ваш город:</b>"
    await callback_query.message.answer(
        text=text,
        reply_markup=ReplyKeyboardRemove(),
        disable_notification=True,
        parse_mode="HTML",
    )


# ---
# ---


@customer_r.message(
    filters.StateFilter(
        CustomerState.change_Name,
    ),
)
async def change_name(
    message: Message,
    state: FSMContext,
):
    """Обработчик изменения имени клиента. CustomerState.change_Name"""

    current_state = CustomerState.default.state
    tg_id = message.from_user.id

    name = message.text

    text = (
        f"Имя было изменено на {name} 🎉\n\n" f"▼ <b>Выберите действие в • ≡ Меню •</b>"
    )

    await message.answer(
        text=text,
        disable_notification=True,
        parse_mode="HTML",
    )

    await customer_data.update_customer_name(tg_id, name)
    await rediska.set_name(customer_bot_id, tg_id, name)

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)


@customer_r.message(
    filters.StateFilter(
        CustomerState.change_Phone,
    ),
)
async def change_phone(
    message: Message,
    state: FSMContext,
):
    """Обработчик изменения телефона клиента. CustomerState.change_Phone"""

    current_state = CustomerState.default.state
    tg_id = message.from_user.id
    phone = message.contact.phone_number

    text = (
        f"Номер был изменено на {phone} 🎉\n\n"
        f"▼ <b>Выберите действие в • ≡ Меню •</b>"
    )

    await message.answer(
        text=text,
        disable_notification=True,
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="HTML",
    )

    await customer_data.update_customer_phone(tg_id, phone)
    await rediska.set_phone(customer_bot_id, tg_id, phone)

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)


@customer_r.message(
    filters.StateFilter(
        CustomerState.change_City,
    ),
)
async def change_city(
    message: Message,
    state: FSMContext,
):
    """Обработчик изменения города клиента. CustomerState.change_City"""

    tg_id = message.from_user.id

    russian_cities = await cities.get_cities()
    city, _ = await find_closest_city(message.text, russian_cities)

    if not city:

        current_state = CustomerState.change_City.state
        text = f"Введите корректное название города!\n\n<b>Ваш город:</b>"
        await message.answer(
            text,
            disable_notification=True,
            parse_mode="HTML",
        )

    else:

        current_state = CustomerState.default.state
        text = (
            f"Город был изменен на {city} 🎉\n\n"
            f"▼ <b>Выберите действие в • ≡ Меню •</b>"
        )

        _ = await customer_data.update_customer_city(tg_id, city)
        _ = await rediska.set_city(customer_bot_id, tg_id, city)

        await message.answer(
            text=text,
            disable_notification=True,
            parse_mode="HTML",
        )

    await state.set_state(current_state)
    await rediska.set_state(customer_bot_id, tg_id, current_state)


# ---
# ---


@customer_fallback.message()
async def handle_unrecognized_message(
    message: Message,
):
    """Обработчик нераспознанных сообщений клиента."""

    await message.delete()
