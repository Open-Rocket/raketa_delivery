from aiogram.types import Message, FSInputFile
from typing import Union, Optional
from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, InputFile,
                           InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, )


async def get_courier_kb(message: Optional[Message] = None, callback_data: Optional[str] = None,
                      text: str = None) -> InlineKeyboardMarkup:
    kb = {
        "/order": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Начать", callback_data="ai_order")]
        ]),
        "/run": ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="Отправить локацию 🧭", request_location=True)],
        ], resize_keyboard=True, one_time_keyboard=False),
        "phone_number": ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="Поделиться номером", request_contact=True)],
        ], resize_keyboard=True, one_time_keyboard=False),
        "/separate_actions": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Сделать заказ", callback_data="make_order"),
             InlineKeyboardButton(text="Доставить", callback_data="make_run")]
        ]),
        "/subs": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Оплатить", callback_data="pay_sub")]
        ]),
        "/ai": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Поддержка", callback_data="support")],
            [InlineKeyboardButton(text="Задать вопрос", callback_data="ask_quest")],
            [InlineKeyboardButton(text="Сделать заказ", callback_data="ai_order")]
        ]),
        "/admin": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Войти", callback_data="admin_enter")]
        ]),
        "ok_kb": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Дальше", callback_data="next")]
        ]),
        "success_payment": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Полетели! ⇢ К заказам", callback_data="lets_go")]
        ]),
        "/profile": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Имя", callback_data="set_my_name")],
            [InlineKeyboardButton(text="Телефон", callback_data="set_my_phone")],
            [InlineKeyboardButton(text="Почта", callback_data="set_my_email")],
            [InlineKeyboardButton(text="Мои заказы", callback_data="my_orders")]
        ]),
        "voice_order_accept": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Отмена", callback_data="voice_order_stop"),
             InlineKeyboardButton(text="Перезаписать", callback_data="ai_order")],
            [InlineKeyboardButton(text="Разместить заказ", callback_data="voice_order_sent")]

        ]),
        "/become_courier": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Go", url="https://t.me/raketadeliverywork_bot")]
        ]),
    }

    if message:
        if message.text == "/start":
            return kb["ok_kb"]
    if message and message.text in kb:
        return kb[message.text]

    if callback_data:
        if callback_data == "okey":
            return kb["/profile"]
        if callback_data == "make_order":
            return kb["/order"]
        if callback_data == "make_run":
            return kb["/run"]
        if callback_data == "p_customer":
            return kb["/pcustomer"]
        if callback_data == "p_courier":
            return kb["/pcourier"]

    if text:
        if text in kb:
            return kb[text]

    return kb["ok_kb"]
