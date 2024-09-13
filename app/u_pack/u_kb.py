from aiogram.types import Message, FSInputFile
from typing import Union, Optional
from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, InputFile,
                           InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery)


async def get_user_kb(message: Optional[Message] = None, callback_data: Optional[str] = None,
                      text: str = None) -> InlineKeyboardMarkup:
    kb = {
        "/order": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Начать", callback_data="ai_order")]
        ]),
        "phone_number": ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="Поделиться номером", request_contact=True)],
        ], resize_keyboard=True, one_time_keyboard=False, input_field_placeholder="***********"),
        "/ai": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Поддержка", callback_data="support")],
            [InlineKeyboardButton(text="Задать вопрос", callback_data="ask_question")],
            [InlineKeyboardButton(text="Отзывы и предложения", callback_data="reviews")]
        ]),
        "next_kb": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Регистрация", callback_data="reg", )],
        ]),
        "/profile": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Имя", callback_data="set_my_name")],
            [InlineKeyboardButton(text="Телефон", callback_data="set_my_phone")],
            [InlineKeyboardButton(text="Мои заказы", callback_data="my_orders")]
        ]),
        "voice_order_accept": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Отмена", callback_data="voice_order_stop"),
             InlineKeyboardButton(text="Перезаписать", callback_data="ai_order")],
            [InlineKeyboardButton(text="Разместить заказ", callback_data="order_sent")]

        ]),
        "/become_courier": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Go", url="https://t.me/raketadeliverywork_bot")]
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
