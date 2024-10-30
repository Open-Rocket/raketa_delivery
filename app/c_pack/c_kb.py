from aiogram.types import Message, FSInputFile
from typing import Union, Optional
from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, InputFile,
                           InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, )


async def get_courier_kb(message: Optional[Message] = None, callback_data: Optional[str] = None,
                         text: str = None) -> InlineKeyboardMarkup:
    kb = {
        "/run": ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="Отправить локацию 🧭", request_location=True)],
        ],
            resize_keyboard=True, one_time_keyboard=False),
        "/subs": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Оплатить", callback_data="pay_sub")]
        ]),
        "/ai": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Поддержка", callback_data="support")],
            [InlineKeyboardButton(text="Задать вопрос", callback_data="ask_question")],
            [InlineKeyboardButton(text="Отзывы и предложения", callback_data="reviews")]
        ]),
        "next_kb": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Регистрация", callback_data="reg", )],
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
        "phone_number": ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="Поделиться номером", request_contact=True)],
        ], resize_keyboard=True, one_time_keyboard=False, input_field_placeholder="✳︎✳︎✳︎✳︎✳︎✳︎✳︎✳︎✳︎✳︎"),
        "accept_tou": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Принять", callback_data="accept_tou")]
        ]),
        "one_order": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Принять заказ", callback_data="accept_order")]
        ]),
        "available_orders": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⇤", callback_data="back_left"),
             InlineKeyboardButton(text="⇥", callback_data="next_right")],
            [InlineKeyboardButton(text="Принять заказ", callback_data="accept_order")]
        ]),

    }

    if message:
        if message.text == "/start":
            return kb["next_kb"]
    if message and message.text in kb:
        return kb[message.text]

    if callback_data: pass

    if text:
        if text in kb:
            return kb[text]

    return kb["ok_kb"]
