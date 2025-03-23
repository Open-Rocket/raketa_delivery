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
    orders_fallback,
    handler,
    kb,
    title,
    order_data,
    rediska,
    cities,
    log,
)


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

    await message.answer(
        text="Это бот рассылки заказов.",
        reply_markup=ReplyKeyboardRemove(),
        disable_notification=True,
        parse_mode="HTML",
    )

    await state.set_state(current_state)
    await rediska.set_state(orders_bot_id, tg_id, current_state)
