from .clock import Time
from .db import db_settings

from .db_alembic import db_settings_dev
from .logger import log
from .ai import PROXY, AI_ASSISTANT_ID, OPENAI_API_KEY, GEMINI_API_KEY
from .rabbit_mq import RABBIT_URL
from .geocoder import YANDEX_API_KEY_Gogich, YANDEX_API_KEY_Olia, YANDEX_API_KEY_Erel
from .payment import payment_provider
from .routers import (
    customer_r,
    customer_fallback,
    courier_r,
    courier_fallback,
    payment_r,
    admin_r,
    admin_fallback,
    partner_r,
    partner_fallback,
)
from .bots import (
    SUPER_ADMIN_TG_ID,
    customer_bot,
    customer_bot_id,
    customer_dp,
    fsm_customer_storage,
    courier_bot,
    courier_bot_id,
    courier_dp,
    fsm_courier_storage,
    admin_bot,
    admin_bot_id,
    admin_dp,
    fsm_admin_storage,
    partner_bot,
    partner_bot_id,
    partner_dp,
    fsm_partner_storage,
)


__all__ = [
    "SUPER_ADMIN_TG_ID",
    "log",
    "db_settings",
    "Time",
    "PROXY",
    "OPENAI_API_KEY",
    "GEMINI_API_KEY",
    "AI_ASSISTANT_ID",
    "YANDEX_API_KEY_Gogich",
    "YANDEX_API_KEY_Olia",
    "YANDEX_API_KEY_Erel",
    "payment",
    "customer_r",
    "courier_r",
    "customer_fallback",
    "courier_fallback",
    "payment_provider",
    "customer_bot",
    "courier_bot",
    "admin_bot",
    "partner_bot",
    "customer_dp",
    "courier_dp",
    "admin_dp",
    "partner_dp",
    "payment_r",
    "fsm_customer_storage",
    "fsm_courier_storage",
    "fsm_admin_storage",
    "fsm_partner_storage",
    "customer_bot_id",
    "courier_bot_id",
    "admin_bot_id",
    "partner_bot_id",
    "admin_r",
    "admin_fallback",
    "partner_r",
    "partner_fallback",
    "RABBIT_URL",
    "db_settings_dev",
]
