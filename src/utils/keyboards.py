from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from typing import Optional


class Keyboard:

    @staticmethod
    async def get_customer_kb(
        key: str,
    ) -> InlineKeyboardMarkup:
        """Возвращает клавиатуру для клиента"""

        kb = {
            "/start": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Регистрация",
                            callback_data="reg",
                        )
                    ],
                ]
            ),
            "/order": InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Начать", callback_data="ai_order")]
                ]
            ),
            "/profile": InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Имя", callback_data="set_my_name")],
                    [InlineKeyboardButton(text="Номер", callback_data="set_my_phone")],
                    [InlineKeyboardButton(text="Город", callback_data="set_my_city")],
                ]
            ),
            "/become_courier": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Go", url="https://t.me/raketadeliverywork_bot"
                        )
                    ]
                ]
            ),
            # ---
            "accept_tou": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="✅ Принять", callback_data="accept_tou"
                        )
                    ]
                ]
            ),
            "phone_number": ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="Поделиться номером", request_contact=True)],
                ],
                resize_keyboard=True,
                one_time_keyboard=False,
                input_field_placeholder="✳︎✳︎✳︎✳︎✳︎✳︎✳︎✳︎✳︎✳︎",
            ),
            # ---
            "voice_order_accept": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Отмена 🆇", callback_data="cancel_order"
                        ),
                        InlineKeyboardButton(
                            text="Перезаписать ゞ", callback_data="ai_order"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="Разместить заказ ✎", callback_data="order_sent"
                        )
                    ],
                ]
            ),
            # ---
            "one_order": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Принять заказ", callback_data="accept_order"
                        )
                    ]
                ]
            ),
            "one_my_order": InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Назад", callback_data="back_myOrders")]
                ]
            ),
            "one_my_pending": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Отменить заказ", callback_data="cancel_my_order"
                        )
                    ],
                    [InlineKeyboardButton(text="Назад", callback_data="back_myOrders")],
                ]
            ),
            # ---
            "pending_orders": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="⇤", callback_data="back_left_mo"),
                        InlineKeyboardButton(text="⇥", callback_data="next_right_mo"),
                    ],
                    [
                        InlineKeyboardButton(
                            text="Отменить заказ", callback_data="cancel_my_order"
                        )
                    ],
                    [InlineKeyboardButton(text="Назад", callback_data="back_myOrders")],
                ]
            ),
            "active_orders": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="⇤", callback_data="back_left_mo"),
                        InlineKeyboardButton(text="⇥", callback_data="next_right_mo"),
                    ],
                    [InlineKeyboardButton(text="Назад", callback_data="back_myOrders")],
                ]
            ),
            "canceled_orders": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="⇤", callback_data="back_left_mo"),
                        InlineKeyboardButton(text="⇥", callback_data="next_right_mo"),
                    ],
                    [InlineKeyboardButton(text="Назад", callback_data="back_myOrders")],
                ]
            ),
            "completed_orders": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="⇤", callback_data="back_left_mo"),
                        InlineKeyboardButton(text="⇥", callback_data="next_right_mo"),
                    ],
                    [InlineKeyboardButton(text="Назад", callback_data="back_myOrders")],
                ]
            ),
            # ---
            "rerecord": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Перезаписать ゞ", callback_data="ai_order"
                        )
                    ],
                ]
            ),
        }

        return kb[key]

    @staticmethod
    async def get_customer_orders_kb(
        pending_count: int, active_count: int, completed_count: int
    ) -> InlineKeyboardMarkup:
        """Возвращает клавиатуру для заказов клиента"""

        my_orders_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"Ожидают {pending_count}", callback_data="pending_orders"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=f"Активные {active_count}", callback_data="active_orders"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=f"Доставленные {completed_count}",
                        callback_data="completed_orders",
                    ),
                ],
            ]
        )

        return my_orders_kb

    @staticmethod
    async def get_courier_kb(
        key: str,
    ) -> InlineKeyboardMarkup:
        """Возвращает клавиатуру для курьера"""

        kb = {
            # ---
            "/run": ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(
                            text="Отправить локацию 🧭",
                            request_location=True,
                        )
                    ],
                ],
                resize_keyboard=True,
                one_time_keyboard=True,
                input_field_placeholder="LOCATION 📍",
            ),
            "/subs": InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Оплатить", callback_data="pay_sub")]
                ]
            ),
            "/start": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Регистрация",
                            callback_data="reg",
                        )
                    ],
                ]
            ),
            "/profile": InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Имя", callback_data="set_my_name")],
                    [
                        InlineKeyboardButton(
                            text="Телефон", callback_data="set_my_phone"
                        )
                    ],
                    # [InlineKeyboardButton(text="Почта", callback_data="set_my_email")],
                    [InlineKeyboardButton(text="Город", callback_data="set_my_city")],
                ]
            ),
            "/make_order": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Заказать доставку",
                            url="https://t.me/raketadelivery_bot",
                        )
                    ]
                ]
            ),
            # ---
            "phone_number": ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="Поделиться номером", request_contact=True)],
                ],
                resize_keyboard=True,
                one_time_keyboard=False,
                input_field_placeholder="✳︎✳︎✳︎✳︎✳︎✳︎✳︎✳︎✳︎✳︎",
            ),
            "accept_tou": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="✅ Принять", callback_data="accept_tou"
                        )
                    ]
                ]
            ),
            # ---
            "available_orders": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="⇤", callback_data="back_left"),
                        InlineKeyboardButton(text="⇥", callback_data="next_right"),
                    ],
                    [
                        InlineKeyboardButton(
                            text="Принять заказ", callback_data="accept_order"
                        )
                    ],
                ]
            ),
            # ---
            "one_order": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Принять заказ", callback_data="accept_order"
                        )
                    ]
                ]
            ),
            "one_my_order": InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Назад", callback_data="back_myOrders")],
                ]
            ),
            # ---
            "complete_one": InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Назад", callback_data="back_myOrders")]
                ]
            ),
            "complete_orders": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="⇤", callback_data="back_left_mo"),
                        InlineKeyboardButton(text="⇥", callback_data="next_right_mo"),
                    ],
                    [InlineKeyboardButton(text="Назад", callback_data="back_myOrders")],
                ]
            ),
            # ---
            "active_one": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Доставил ✅", callback_data="order_delivered"
                        )
                    ],
                    [InlineKeyboardButton(text="Назад", callback_data="back_myOrders")],
                ]
            ),
            "active_orders": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="⇤", callback_data="back_left_mo"),
                        InlineKeyboardButton(text="⇥", callback_data="next_right_mo"),
                    ],
                    [
                        InlineKeyboardButton(
                            text="Доставил ✅", callback_data="order_delivered"
                        )
                    ],
                    [InlineKeyboardButton(text="Назад", callback_data="back_myOrders")],
                ]
            ),
            # ---
            "go_back": InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Назад", callback_data="back_myOrders")]
                ]
            ),
            # ---
            "success_payment": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Перейти к заказам!", callback_data="lets_go"
                        )
                    ]
                ]
            ),
            # ---
            "pay_sub": InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Оплатить", callback_data="pay_sub")]
                ]
            ),
            "extend_sub": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="🔄 Продлить", callback_data="extend_sub"
                        )
                    ]
                ]
            ),
            # ---
            "super_go": InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Супер 🌟", callback_data="super_go")]
                ]
            ),
        }

        return kb[key]

    @staticmethod
    async def get_courier_orders_kb(
        active_count: int, completed_count: int
    ) -> InlineKeyboardMarkup:
        """Возвращает клавиатуру для заказов курьера"""

        my_orders_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"Завершеные {completed_count}",
                        callback_data="completed_orders",
                    ),
                    InlineKeyboardButton(
                        text=f"Активные {active_count}", callback_data="active_orders"
                    ),
                ],
                [InlineKeyboardButton(text="Статистика", callback_data="my_statistic")],
            ]
        )

        return my_orders_kb

    @staticmethod
    async def get_courier_orders_near_kb(available_orders: int) -> InlineKeyboardMarkup:
        """Возвращает клавиатуру для заказов рядом"""

        near_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"Показать заказы рядом {available_orders}",
                        callback_data="show_nearby_orders",
                    )
                ]
            ]
        )

        return near_kb


kb: Keyboard = Keyboard()


__all__ = ["kb"]


keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Продлить", callback_data="pay_sub")]
    ]
)
