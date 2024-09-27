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
        ], resize_keyboard=True, one_time_keyboard=False, input_field_placeholder="✳︎✳︎✳︎✳︎✳︎✳︎✳︎✳︎✳︎✳︎"),
        "next_kb": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Регистрация", callback_data="reg", )],
        ]),
        "/profile": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Имя", callback_data="set_my_name")],
            [InlineKeyboardButton(text="Номер", callback_data="set_my_phone")],
            [InlineKeyboardButton(text="Город", callback_data="set_my_city")],
        ]),
        "voice_order_accept": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Отмена 🆇", callback_data="cancel_order"),
             InlineKeyboardButton(text="Перезаписать ゞ", callback_data="ai_order")],
            [InlineKeyboardButton(text="Разместить заказ ✎", callback_data="order_sent")]

        ]),
        "/become_courier": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Go", url="https://t.me/raketadeliverywork_bot")]
        ]),
        "/test": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⇤", callback_data="back_left"),
             InlineKeyboardButton(text="⇥", callback_data="next_right")],
            [InlineKeyboardButton(text="Принять заказ", callback_data="accept_order")]

        ]),
        "one_order": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Принять заказ", callback_data="accept_order")]

        ]),

        "pending_orders": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⇤", callback_data="back_left_mo"),
             InlineKeyboardButton(text="⇥", callback_data="next_right_mo")],
            [InlineKeyboardButton(text="Отменить заказ", callback_data="cancel_my_order")],
            [InlineKeyboardButton(text="Назад", callback_data="back_myOrders")]

        ]),
        "one_my_order": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data="back_myOrders")]

        ]),
        "one_my_pending": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Отменить заказ", callback_data="cancel_my_order")],
            [InlineKeyboardButton(text="Назад", callback_data="back_myOrders")]

        ]),
        "active_orders": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⇤", callback_data="back_left_mo"),
             InlineKeyboardButton(text="⇥", callback_data="next_right_mo")],
            [InlineKeyboardButton(text="Назад", callback_data="back_myOrders")]

        ]),
        "canceled_orders": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⇤", callback_data="back_left_mo"),
             InlineKeyboardButton(text="⇥", callback_data="next_right_mo")],
            [InlineKeyboardButton(text="Назад", callback_data="back_myOrders")]

        ]),
        "completed_orders": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⇤", callback_data="back_left_mo"),
             InlineKeyboardButton(text="⇥", callback_data="next_right_mo")],
            [InlineKeyboardButton(text="Назад", callback_data="back_myOrders")]

        ]),
        "overprice": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Не оформлять 🆇", callback_data="cancel_order"),
             InlineKeyboardButton(text="Хорошо", callback_data="accept_notification")]
        ]),
        "rerecord": InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Перезаписать ゞ", callback_data="ai_order")],

        ]),
    }

    if message:
        if message.text == "/start":
            return kb["next_kb"]
        else:
            return kb[message.text]
    if message and message.text in kb:
        return kb[message.text]

    if callback_data:
        pass

    if text:
        if text in kb:
            return kb[text]

    # return kb["ok_kb"]


async def get_my_orders_kb(pending_count: int, active_count: int,
                           canceled_count: int, completed_count: int) -> InlineKeyboardMarkup:
    my_orders_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Ожидают {pending_count}", callback_data="pending_orders"),
         InlineKeyboardButton(text=f"Активные {active_count}", callback_data="active_orders")],
        [InlineKeyboardButton(text=f"Отмененные {canceled_count}", callback_data="canceled_orders"),
         InlineKeyboardButton(text=f"Доставленные {completed_count}", callback_data="completed_orders")],
        [InlineKeyboardButton(text="Статистика", callback_data="my_statistic")]

    ])

    return my_orders_kb
