from ._deps import (
    payment_provider,
    payment,
    log,
    FSMContext,
    Message,
    LabeledPrice,
    PreCheckoutQuery,
    CallbackQuery,
    ContentType,
    MessageHandler,
    title,
    kb,
    F,
)


@payment.message(F.text == "/subs")
@payment.callback_query(F.data == "pay_sub")
async def payment_invoice(event: Message | CallbackQuery, state: FSMContext):

    handler = MessageHandler(state, event.bot)
    chat_id = event.chat.id if isinstance(event, Message) else event.message.chat.id

    if isinstance(event, Message):
        await handler.delete_previous_message(chat_id)

    prices = [
        LabeledPrice(
            label="Месячная подписка",
            amount=99000,  # Сумма указана в копейках (990 рублей)
        ),
    ]

    if not payment_provider:
        log.info("Ошибка: provider_token не найден. Проверьте переменные окружения.")
        return

    # Отправка инвойса пользователю
    new_message = await event.bot.send_invoice(
        chat_id=chat_id,
        title="Подписка Raketa",
        description="Оформите подписку на сервис доставки...",
        payload="Payment through a bot",
        provider_token=provider_token,
        currency="RUB",
        prices=prices,
        max_tip_amount=50000,
        start_parameter="",
        photo_url="https://ltdfoto.ru/images/2024/08/31/subs.jpg",
        photo_width=1200,
        photo_height=720,
        need_name=True,
        need_phone_number=True,
        need_email=True,
        reply_markup=None,
    )

    await handler.handle_new_message(
        new_message, event if isinstance(event, Message) else event.message
    )


@payment.pre_checkout_query()
async def pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    try:
        if (
            pre_checkout_query.currency == "RUB"
            and pre_checkout_query.total_amount == 99000
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
        await pre_checkout_query.bot.answer_pre_checkout_query(
            pre_checkout_query.id, ok=False, error_message=f"Ошибка: {str(e)}"
        )


@payment.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def succesful_payment(message: Message, state: FSMContext):
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)
    ttl = await title.get_title_courier("success_payment")
    text = f"Cпасибо за подписку!\nСумма: {message.successful_payment.total_amount // 100}{message.successful_payment.currency}"
    reply_kb = await kb.get_courier_kb(text="success_payment")
    new_message = await message.answer_photo(
        photo=ttl, caption=text, reply_markup=reply_kb
    )
    await handler.handle_new_message(new_message, message)
