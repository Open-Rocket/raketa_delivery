import os
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery, CallbackQuery
from aiogram.filters import Command
from dotenv import load_dotenv
from aiogram.enums import ContentType

from app.common.message_handler import MessageHandler
from app.common.titles import get_image_title_courier
from app.c_pack.c_kb import get_courier_kb

test_payment_router = Router()
load_dotenv()


@test_payment_router.message(F.text == "/subs")
@test_payment_router.callback_query(F.data == "pay_sub")
async def payment_invoice(event: Message | CallbackQuery, state: FSMContext):
    handler = MessageHandler(state, event.bot)
    chat_id = event.chat.id if isinstance(event, Message) else event.message.chat.id

    if isinstance(event, Message):
        await handler.delete_previous_message(chat_id)

    prices = [
        LabeledPrice(
            label="Месячная подписка",
            amount=99000
        ),
    ]

    print(f"Sending invoice with prices: {prices}")

    new_message = await event.bot.send_invoice(
        chat_id=chat_id,
        title="Подписка Raketa",
        description=("Оформите подписку на сервис доставки, чтобы экономить на комиссиях за каждый заказ. "
                     "С подпиской вы получаете неограниченный доступ к заказам в течение 30 дней. "
                     "Оплатите подписку и начните пользоваться всеми преимуществами прямо сейчас!"),
        payload="Payment through a bot",
        provider_token=os.getenv("UKASSA_TEST"),
        currency="RUB",  # Валюта должна быть в верхнем регистре
        prices=prices,
        max_tip_amount=50000,
        # suggested_tip_amounts=[5000, 10000, 15000, 20000],
        start_parameter="",
        provider_data=None,
        photo_url="https://ltdfoto.ru/images/2024/08/31/subs.jpg",
        # photo_size=512,
        photo_width=1200,
        photo_height=720,
        need_name=True,
        need_phone_number=True,
        need_email=True,
        need_shipping_address=False,
        send_email_to_provider=False,
        send_phone_number_to_provider=False,
        is_flexible=False,
        disable_notification=False,
        protect_content=False,
        reply_to_message_id=None,
        allow_sending_without_reply=True,
        reply_markup=None,
        request_timeout=None
    )

    await handler.handle_new_message(new_message, event if isinstance(event, Message) else event.message)


@test_payment_router.pre_checkout_query()
async def pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    try:
        # Логи для отладки
        print(f"Currency: {pre_checkout_query.currency}, Amount: {pre_checkout_query.total_amount}")

        if pre_checkout_query.currency == 'RUB' and pre_checkout_query.total_amount == 99000:
            await pre_checkout_query.bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
        else:
            await pre_checkout_query.bot.answer_pre_checkout_query(pre_checkout_query.id, ok=False,
                                                                   error_message='Неверная сумма или валюта')
    except Exception as e:
        await pre_checkout_query.bot.answer_pre_checkout_query(pre_checkout_query.id, ok=False,
                                                               error_message=f'Ошибка: {str(e)}')
        print(f"Exception in pre_checkout_query: {e}")


@test_payment_router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def succesful_payment(message: Message, state: FSMContext):
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)
    photo_title = await get_image_title_courier("success_payment")
    text = f"Cпасибо за подписку!\nСумма: {message.successful_payment.total_amount // 100}{message.successful_payment.currency}"
    reply_kb = await get_courier_kb(text="success_payment")
    new_message = await message.answer_photo(photo=photo_title,
                                             caption=text,
                                             reply_markup=reply_kb)
    await handler.handle_new_message(new_message, message)
