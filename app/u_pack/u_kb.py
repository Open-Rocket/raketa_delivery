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
        "next_kb": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Регистрация", callback_data="reg", )],
        ]),
        "/profile": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Имя", callback_data="set_my_name")],
            [InlineKeyboardButton(text="Номер", callback_data="set_my_phone")],
            [InlineKeyboardButton(text="Мои заказы", callback_data="get_my_orders")]
        ]),
        "voice_order_accept": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Отмена", callback_data="cancel_order"),
             InlineKeyboardButton(text="Перезаписать", callback_data="ai_order")],
            [InlineKeyboardButton(text="Разместить заказ", callback_data="order_sent")]

        ]),
        "/become_courier": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Go", url="https://t.me/raketadeliverywork_bot")]
        ]),
        "/test": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⇤", callback_data="back_left"),
             InlineKeyboardButton(text="⇥", callback_data="next_right")]

        ]),
        "get_my_orders": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⇤", callback_data="back_left_mo"),
             InlineKeyboardButton(text="⇥", callback_data="next_right_mo")]

        ]),
    }

    if message:
        if message.text == "/start":
            return kb["next_kb"]
    if message and message.text in kb:
        return kb[message.text]

    if callback_data:
        if callback_data in kb:
            return kb[callback_data]

    if text:
        if text in kb:
            return kb[text]

    return kb["ok_kb"]
