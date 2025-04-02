import io
import asyncio
import time
import zlib
import json
from random import randint
from aiogram import Router, filters, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.enums import ContentType
from datetime import datetime, timedelta
from aiogram.types import LabeledPrice, InputMediaDocument
from src.middlewares import CustomerOuterMiddleware, CourierOuterMiddleware
from aiogram.types import ReplyKeyboardRemove
from math import ceil


from src.services import (
    customer_data,
    courier_data,
    order_data,
    admin_data,
    partner_data,
    assistant,
    formatter,
    route,
    recognizer,
    seed_maker,
)
from src.models import OrderStatus
from src.confredis import rediska
from src.config import (
    SUPER_ADMIN_TG_ID,
    Time,
    customer_bot,
    courier_bot,
    customer_bot_id,
    courier_bot_id,
    admin_bot,
    admin_bot_id,
    partner_bot,
    partner_bot_id,
    customer_r,
    courier_r,
    payment_r,
    customer_fallback,
    courier_fallback,
    admin_r,
    admin_fallback,
    partner_r,
    partner_fallback,
    orders_bot,
    orders_bot_id,
    orders_dp,
    orders_r,
    orders_fallback,
    payment_provider,
    log,
)
from aiogram.types import Message, CallbackQuery, PreCheckoutQuery, BufferedInputFile
from src.utils import (
    CustomerState,
    CourierState,
    AdminState,
    PartnerState,
    OrdersState,
    handler,
    kb,
    title,
)
from src.services import cities, find_closest_city


__all__ = [
    "ceil",
    "StateFilter",
    "randint",
    "io",
    "zlib",
    "json",
    "time",
    "asyncio",
    "CommandStart",
    "FSMContext",
    "ContentType",
    "AdminState",
    "filters",
    "F",
    "datetime",
    "CustomerOuterMiddleware",
    "CourierOuterMiddleware",
    "customer_data",
    "courier_data",
    "order_data",
    "assistant",
    "route",
    "recognizer",
    "OrderStatus",
    "rediska",
    "timedelta",
    "customer_r",
    "courier_r",
    "customer_fallback",
    "courier_fallback",
    "log",
    "Message",
    "CallbackQuery",
    "handler",
    "CustomerState",
    "CourierState",
    "kb",
    "title",
    "Router",
    "payment_r",
    "PreCheckoutQuery",
    "formatter",
    "cities",
    "find_closest_city",
    "LabeledPrice",
    "payment_provider",
    "customer_bot",
    "courier_bot",
    "customer_bot_id",
    "courier_bot_id",
    "Time",
    "ReplyKeyboardRemove",
    "admin_r",
    "admin_fallback",
    "admin_bot_id",
    "admin_bot",
    "admin_data",
    "SUPER_ADMIN_TG_ID",
    "partner_bot",
    "partner_bot_id",
    "partner_r",
    "partner_fallback",
    "partner_data",
    "orders_bot",
    "orders_bot_id",
    "orders_dp",
    "orders_r",
    "orders_fallback",
    "PartnerState",
    "OrdersState",
    "seed_maker",
    "BufferedInputFile",
    "InputMediaDocument",
]
