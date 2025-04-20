from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CopyTextButton,
)
from typing import Optional
from src.services import admin_data


class Keyboard:

    @staticmethod
    async def get_customer_kb(
        key: str,
    ) -> InlineKeyboardMarkup:
        """Возвращает клавиатуру для клиента"""

        support_link = await admin_data.get_support_link()

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
            "/support": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Перейти в чат",
                            url=support_link,
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
            # ---
            "promo": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Ввести PROMOKOD",
                            callback_data="PROMOKOD",
                        ),
                    ],
                ]
            ),
            "make_order": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Сделать заказ",
                            callback_data="make_order",
                        )
                    ]
                ]
            ),
            "try_seed_again": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Ввести PROMOKOD еще раз",
                            callback_data="PROMOKOD",
                        )
                    ]
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
            # ---
            "promo": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Ввести PROMOKOD",
                            callback_data="PROMOKOD",
                        ),
                    ],
                ]
            ),
            "key": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="В другой раз 🕒",
                            callback_data="not_now",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="Ввести PROMOKOD",
                            callback_data="PROMOKOD",
                        ),
                    ],
                ]
            ),
            "try_seed_again": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Ввести PROMOKOD еще раз",
                            callback_data="PROMOKOD",
                        )
                    ]
                ]
            ),
        }

        return kb[key]

    @staticmethod
    async def courier_XP_kb(
        key: str,
        rub: float,
        current_xp: float,
        new_price: float,
    ) -> InlineKeyboardMarkup:
        """Возвращает клавиатуру для курьера"""

        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"Оплатить за {rub} ₽",
                        callback_data="use_rub",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=f"Списать {current_xp} XP = {new_price} ₽",
                        callback_data="use_XP",
                    )
                ],
            ]
        )

        return kb

    @staticmethod
    async def get_courier_orders_kb(
        active_count: int, completed_count: int
    ) -> InlineKeyboardMarkup:
        """Возвращает клавиатуру для заказов курьера"""

        my_orders_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Статистика", callback_data="my_statistic")],
                [
                    InlineKeyboardButton(
                        text=f"Завершеные {completed_count}",
                        callback_data="completed_orders",
                    ),
                    InlineKeyboardButton(
                        text=f"Активные {active_count}", callback_data="active_orders"
                    ),
                ],
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
                        text=f"🔄 Обновить данные",
                        callback_data="refresh_orders",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=f"Город {city_orders_len}",
                        callback_data="show_city_orders",
                    ),
                    InlineKeyboardButton(
                        text=f"Рядом {available_orders_len}",
                        callback_data="show_nearby_orders",
                    ),
                ],
            ]
        )

        return near_kb

    @staticmethod
    async def get_admin_kb(
        key: str,
    ) -> InlineKeyboardMarkup:
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
                            text="🔄 Обновить",
                            callback_data="refresh_orders",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="📦 Выбрать заказ",
                            callback_data="choose_order",
                        )
                    ],
                ]
            ),
            "/global": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="🔄 Обновить",
                            callback_data="refresh_global_data",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="⚙️ Сервис",
                            callback_data="service_data",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="🤑 Финансы",
                            callback_data="finance",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="🏆 Рекорды",
                            callback_data="records",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="💰 Тарифы",
                            callback_data="prices_and_tariffs",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="🎉 Акции",
                            callback_data="discounts_and_promotions",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="👨‍💼 Админы",
                            callback_data="admins",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="💬 Сообщения",
                            callback_data="messages",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="🔔 Уведомления",
                            callback_data="notifications",
                        )
                    ],
                ]
            ),
            # ---
            "admins": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="+ Зарегистрировать админа",
                            callback_data="set_admin",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="❌ Удалить админа",
                            callback_data="del_admin",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="↩️ Назад",
                            callback_data="back_global_data",
                        ),
                    ],
                ]
            ),
            "prices_and_tariffs": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Стоимость подписки",
                            callback_data="subscription_price",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Стандартная цена за 1 км",
                            callback_data="standard_order_price",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Максимальная цена заказа",
                            callback_data="max_order_price",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Коэффициент 0-5 км",
                            callback_data="distance_coefficient_less_5",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Коэффициент 5-10 км",
                            callback_data="distance_coefficient_5_10",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Коэффициент 10-20 км",
                            callback_data="distance_coefficient_10_20",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Коэффициент 20+ км",
                            callback_data="distance_coefficient_more_20",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Коэффициент 00-06",
                            callback_data="time_coefficient_00_06",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Коэффициент 06-12",
                            callback_data="time_coefficient_06_12",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Коэффициент 12-18",
                            callback_data="time_coefficient_12_18",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Коэффициент 18-21",
                            callback_data="time_coefficient_18_21",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Коэффициент 21-00",
                            callback_data="time_coefficient_21_00",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Коэффициент по большим городам",
                            callback_data="big_cities_coefficient",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Коэффициент по остальным городам",
                            callback_data="small_cities_coefficient",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Минимальная сумма выплаты",
                            callback_data="change_min_refund_amount",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Максимальная сумма выплаты",
                            callback_data="change_max_refund_amount",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Базовый XP за заказ",
                            callback_data="change_base_order_XP",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="XP за расстояние",
                            callback_data="change_distance_XP",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="XP за скорость",
                            callback_data="change_speed_XP",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Радиус поиска",
                            callback_data="change_radius_km",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Макс выполняемых заказов",
                            callback_data="change_max_orders_count",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="↩️ Назад",
                            callback_data="back_global_data",
                        ),
                    ],
                ]
            ),
            "discounts_and_promotions": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Скидка на первый заказ",
                            callback_data="change_first_order_discount",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Бесплатный период",
                            callback_data="change_free_period",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Партнерский процент",
                            callback_data="change_refund_percent",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="↩️ Назад",
                            callback_data="back_global_data",
                        ),
                    ],
                ]
            ),
            # ---
            "records": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Скорость",
                            callback_data="speed_records",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Дистанция",
                            callback_data="distance_records",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Заказов",
                            callback_data="orders_records",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Заработал",
                            callback_data="earn_courier_record",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="↩️ Назад",
                            callback_data="back_global_data",
                        ),
                    ],
                ]
            ),
            "speed_records": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Y-M-D",
                            callback_data="full_speed_report_by_date",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Y-M-D : Y-M-D",
                            callback_data="full_speed_report_by_period",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="↩️ Рекорды",
                            callback_data="back_records",
                        ),
                    ],
                ]
            ),
            "distance_records": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Y-M-D",
                            callback_data="full_distance_report_by_date",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Y-M-D : Y-M-D",
                            callback_data="full_distance_report_by_period",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="↩️ Рекорды",
                            callback_data="back_records",
                        ),
                    ],
                ]
            ),
            "orders_records": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Y-M-D",
                            callback_data="full_orders_report_by_date",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Y-M-D : Y-M-D",
                            callback_data="full_orders_report_by_period",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="↩️ Рекорды",
                            callback_data="back_records",
                        ),
                    ],
                ]
            ),
            "earn_courier_record": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Y-M-D",
                            callback_data="full_earned_report_by_date",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Y-M-D : Y-M-D",
                            callback_data="full_earned_report_by_period",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="↩️ Рекорды",
                            callback_data="back_records",
                        ),
                    ],
                ]
            ),
            # ---
            "finance": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Y-M-D",
                            callback_data="full_finance_report_by_date",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Y-M-D : Y-M-D",
                            callback_data="full_finance_report_by_period",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="↩️ Назад",
                            callback_data="back_global_data",
                        ),
                    ],
                ]
            ),
            "messages": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Обработать запрос №",
                            callback_data="process_request",
                        )
                    ],
                ]
            ),
            "notifications": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Изменить интервал",
                            callback_data="change_interval",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Изменить ссылку поддержки",
                            callback_data="change_support_link",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="↩️ Назад",
                            callback_data="back_global_data",
                        ),
                    ],
                ]
            ),
            "send_message": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Отправить сообщение",
                            callback_data="send_message_to_users",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Отправить рассылку",
                            callback_data="send_broadcast_message",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="↩️ Назад",
                            callback_data="back_global_data",
                        ),
                    ],
                ]
            ),
            "process_request": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="✅ Обработан",
                            callback_data="confirm_request",
                        )
                    ]
                ]
            ),
            "phone_kb": ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="Поделиться номером", request_contact=True)],
                ],
                resize_keyboard=True,
                one_time_keyboard=True,
                input_field_placeholder="✳︎✳︎✳︎✳︎✳︎✳︎✳︎✳︎✳︎✳︎",
            ),
            # ---
            "choose_user": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Выбрать по ID",
                            callback_data="choose_user_by_ID",
                        ),
                        InlineKeyboardButton(
                            text="Рассылка",
                            callback_data="mailing_users",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="↩️ Назад",
                            callback_data="back_to_users",
                        ),
                    ],
                ]
            ),
            "choose_courier": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Выбрать по ID",
                            callback_data="choose_courier_by_ID",
                        ),
                        InlineKeyboardButton(
                            text="Рассылка",
                            callback_data="mailing_couriers",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="↩️ Назад",
                            callback_data="back_to_users",
                        ),
                    ],
                ]
            ),
            "choose_partner": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Выбрать по SEED",
                            callback_data="choose_partner_by_SEED",
                        ),
                        InlineKeyboardButton(
                            text="Рассылка",
                            callback_data="mailing_partners",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="↩️ Назад",
                            callback_data="back_to_users",
                        ),
                    ],
                ]
            ),
        }

        return kb[key]

    @staticmethod
    async def get_turn_status_kb(
        key: str,
        status_service: bool = False,
        status_partner: bool = True,
        status_notify: bool = True,
    ) -> InlineKeyboardMarkup:
        """Возвращает клавиатуру для админа"""

        kb = {
            "service_and_data": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=f"{'Включить сервис ✅' if status_service else 'Выключить сервис ❌'}",
                            callback_data=f"{'turn_on_service' if status_service else 'turn_off_service'}",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=f"{'Включить партнерку ✅' if status_partner else 'Выключить партнерку ❌'}",
                            callback_data=f"{'turn_on_partner' if status_partner else 'turn_off_partner'}",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="↩️ Назад",
                            callback_data="back_global_data",
                        ),
                    ],
                ]
            ),
            "notify": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=f"{'Включить уведомления 🔔' if status_notify else  'Выключить уведомления 🔕'}",
                            callback_data=f"{'turn_on_notify' if status_notify else   'turn_off_notify'}",
                        ),
                    ],
                ]
            ),
        }

        return kb[key]

    @staticmethod
    async def get_partner_kb(
        key: str,
    ) -> InlineKeyboardMarkup:
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
            "try_again_seed": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Попробовать еще раз",
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
                            text="🔄 Обновить данные",
                            callback_data="refresh_balance",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Запросить выплату",
                            callback_data="get_partner_earn",
                        )
                    ],
                ]
            ),
            "adv_request": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Визитка для курьера",
                            callback_data="business_card_courier",
                        ),
                        InlineKeyboardButton(
                            text="Визитка для клиента",
                            callback_data="business_card_customer",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="Буклет для курьера",
                            callback_data="buklet_courier",
                        ),
                        InlineKeyboardButton(
                            text="Буклет для клиента",
                            callback_data="buklet_customer",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="QR-код бота курьера",
                            callback_data="QR_courier",
                        ),
                        InlineKeyboardButton(
                            text="QR-код бота клиента",
                            callback_data="QR_customer",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="Логотип",
                            callback_data="logo",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="SEED ключ",
                            callback_data="seed_key",
                        ),
                    ],
                ]
            ),
            "refresh_refs": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="🔄 Обновить данные",
                            callback_data="refresh_refs",
                        )
                    ]
                ]
            ),
        }

        return kb[key]

    @staticmethod
    async def get_task_kb(
        key: str,
    ) -> InlineKeyboardMarkup:
        """Возвращает клавиатуру для курьера"""

        kb = {
            "go_work": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=f"Перейти к заказам!",
                            callback_data="lets_go",
                        )
                    ]
                ]
            ),
        }

        return kb[key]

    @staticmethod
    async def get_user_manipulate_kb(
        type_of_user: str,
        is_blocked: bool = False,
    ) -> InlineKeyboardMarkup:
        """Возвращает клавиатуру для взаимодействия с пользователем"""

        kb = {
            "customer": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=f"{'Разблокировать 🔓' if is_blocked else 'Заблокировать 🔒'}",
                            callback_data=f"{'unblock_customer' if is_blocked else 'block_customer'}",
                        ),
                    ],
                ]
            ),
            "courier": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=f"{'Разблокировать 🔓' if is_blocked else 'Заблокировать 🔒'}",
                            callback_data=f"{'unblock_courier' if is_blocked else 'block_courier'}",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="Начислить XP ❇️",
                            callback_data="add_XP",
                        ),
                    ],
                ]
            ),
            "partner": InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=f"{'Разблокировать 🔓' if is_blocked else 'Заблокировать 🔒'}",
                            callback_data=f"{'unblock_partner' if is_blocked else 'block_partner'}",
                        ),
                    ],
                ]
            ),
        }

        return kb[type_of_user]


kb: Keyboard = Keyboard()


__all__ = ["kb"]


keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Продлить", callback_data="pay_sub")]
    ]
)
