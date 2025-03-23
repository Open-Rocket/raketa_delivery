from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CopyTextButton,
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
            "/become_partner": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Cтать партнером",
                            url="https://t.me/raketadelivery_agents_bot",
                        )
                    ]
                ]
            ),
            "/channel": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Перейти в канал",
                            url="https://t.me/raketadeliverychannel",
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
                one_time_keyboard=True,
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
            ),
            "run_first": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="🚀 Начать работу",
                            callback_data="lets_go_first",
                        )
                    ]
                ]
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
            "/become_partner": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Cтать партнером",
                            url="https://t.me/raketadelivery_agents_bot",
                        )
                    ]
                ]
            ),
            "/chat": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Перейти в чат",
                            url="https://t.me/+3umqnjKcHMlmNjQy",
                        )
                    ]
                ]
            ),
            "/channel": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Перейти в канал",
                            url="https://t.me/raketadeliverychannel",
                        )
                    ]
                ]
            ),
            "/orders_bot": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Получать заказы",
                            url="https://t.me/raketadelivery_orders_bot",
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
                one_time_keyboard=True,
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
                    [
                        InlineKeyboardButton(
                            text="Назад",
                            callback_data="back_location",
                        ),
                    ],
                ]
            ),
            # ---
            "one_order": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Принять заказ",
                            callback_data="accept_order",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="Назад",
                            callback_data="back_location",
                        ),
                    ],
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
                            text=f"Перейти к заказам!",
                            callback_data="lets_go",
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
                    [
                        InlineKeyboardButton(
                            text="Активировать 🌟", callback_data="super_go"
                        )
                    ]
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
    async def get_courier_orders_full_kb(
        city_orders_len: int,
        available_orders_len: int,
    ) -> InlineKeyboardMarkup:
        """Возвращает клавиатуру для заказов рядом"""

        near_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"Заказы в городе {city_orders_len}",
                        callback_data="show_city_orders",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=f"Заказы рядом {available_orders_len}",
                        callback_data="show_nearby_orders",
                    ),
                ],
            ]
        )

        return near_kb

    @staticmethod
    async def get_admin_kb(key: str) -> InlineKeyboardMarkup:
        """Возвращает клавиатуру для админа"""

        kb = {
            "/users": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="👫 Клиенты",
                            callback_data="choose_user",
                        ),
                        InlineKeyboardButton(
                            text="🥷 Курьеры",
                            callback_data="choose_courier",
                        ),
                        InlineKeyboardButton(
                            text="🤝 Партнеры",
                            callback_data="choose_partner",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="🔄 Обновить данные",
                            callback_data="refresh_users",
                        )
                    ],
                ]
            ),
            "/orders": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="📦 Выбрать заказ",
                            callback_data="choose_order",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="🔄 Обновить данные",
                            callback_data="refresh_orders",
                        )
                    ],
                ]
            ),
            "/admins": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="➕ Зарегистрировать админа",
                            callback_data="set_admin",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="❌ Удалить админа",
                            callback_data="del_admin",
                        )
                    ],
                ]
            ),
            "/global": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="⚙️ Сервис и Данные",
                            callback_data="service_data",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="💰 Цены и Тарифы",
                            callback_data="prices",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="🎉 Акции и Скидки %",
                            callback_data="discounts",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="📢 Сообщения и Рассылки",
                            callback_data="send_message",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="🔄 Обновить данные",
                            callback_data="refresh_global_data",
                        )
                    ],
                ]
            ),
        }

        return kb[key]

    @staticmethod
    async def get_partner_kb(key: str) -> InlineKeyboardMarkup:
        """Возвращает клавиатуру для админа"""

        kb = {
            "/start": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Регистрация",
                            callback_data="reg_partner",
                        )
                    ],
                ]
            ),
            "phone_number": ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="Поделиться номером", request_contact=True)],
                ],
                resize_keyboard=True,
                one_time_keyboard=True,
                input_field_placeholder="✳︎✳︎✳︎✳︎✳︎✳︎✳︎✳︎✳︎✳︎",
            ),
            "generate_seed": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="🔑 Сгенерировать",
                            callback_data="generate_seed_key",
                        )
                    ]
                ]
            ),
            "try_save_again": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Повторить попытку",
                            callback_data="try_save_again",
                        )
                    ]
                ]
            ),
            "earn_request": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Запросить выплату",
                            callback_data="get_partner_earn",
                        )
                    ]
                ]
            ),
        }

        return kb[key]


kb: Keyboard = Keyboard()


__all__ = ["kb"]


keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Продлить", callback_data="pay_sub")]
    ]
)
