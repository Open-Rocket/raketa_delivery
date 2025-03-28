from ._deps import (
    CommandStart,
    FSMContext,
    OrdersState,
    OrderStatus,
    ContentType,
    ReplyKeyboardRemove,
    filters,
    Message,
    CallbackQuery,
    PreCheckoutQuery,
    LabeledPrice,
    zlib,
    Time,
    json,
    F,
    orders_bot,
    orders_bot_id,
    orders_r,
    courier_data,
    orders_fallback,
    handler,
    kb,
    title,
    order_data,
    rediska,
    cities,
    log,
)

import asyncio


async def monitor_orders_for_courier(tg_id: int, city: str):
    """Периодически проверяет новые заказы для курьера в его городе и отправляет их по очереди."""
    sent_orders = set()
    while True:
        new_orders = await order_data.get_pending_orders_in_city(city)

        if new_orders:
            for order_id, order in new_orders.items():

                if order_id not in sent_orders:

                    await orders_bot.send_message(
                        tg_id,
                        text=f"# --- New order ---\n",
                    )

                    asyncio.wait(0.3)

                    await orders_bot.send_message(
                        tg_id,
                        text=f"{order['text']}",
                        parse_mode="HTML",
                    )
                    sent_orders.add(order_id)
                    await asyncio.sleep(2)

        await asyncio.sleep(10)


@orders_r.message(
    CommandStart(),
)
async def cmd_start_admin(
    message: Message,
    state: FSMContext,
):
    """Обработчик команды /start для бота рассылки заказов."""

    tg_id = message.from_user.id
    current_state = OrdersState.default.state

    name, _, city = await courier_data.get_courier_info(tg_id)

    if not name:

        text = (
            "Вы не зарегистрированы как курьер. Пожалуйста, зарегистрируйтесь, "
            "нажав на кнопку ниже."
        )
        reply_kb = await kb.get_customer_kb("/become_courier")

        await message.answer(
            text=text,
            reply_markup=reply_kb,
            disable_notification=True,
            parse_mode="HTML",
        )
        return

    asyncio.create_task(monitor_orders_for_courier(tg_id, city))

    await message.answer(
        text="Это бот рассылки заказов.",
        reply_markup=ReplyKeyboardRemove(),
        disable_notification=True,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(orders_bot_id, tg_id, current_state)


@orders_r.callback_query(
    F.data == "show_city_orders",
)
async def show_city_orders(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    """Обрабатывает запрос на просмотр всех заказов в городе."""

    data = await state.get_data()
    order_data = data.get("order_data", {})
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
        parse_mode="HTML",
    )

    await state.update_data(
        orders_data=orders_data,
        order_ids=order_ids,
        current_index=0,
        current_order_id=order_ids[0],
    )
    await rediska.save_fsm_state(state, bot_id, tg_id)

    for order_id in order_ids[1:]:
        await asyncio.sleep(1)
        await callback_query.message.edit_text(
            orders_data[order_id]["text"],
            reply_markup=reply_markup,
            parse_mode="HTML",
        )
