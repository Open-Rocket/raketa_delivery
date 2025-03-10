import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

fsm_customer_storage = MemoryStorage()
fsm_courier_storage = MemoryStorage()

load_dotenv()

customer_bot = Bot(token=os.getenv("CUSTOMER_BOT"))
courier_bot = Bot(token=os.getenv("COURIER_BOT"))

customer_bot_id = customer_bot.id
courier_bot_id = courier_bot.id

customer_dp = Dispatcher(storage=fsm_customer_storage)
courier_dp = Dispatcher(storage=fsm_courier_storage)


__all__ = [
    "customer_bot",
    "courier_bot",
    "customer_dp",
    "courier_dp",
    "fsm_customer_storage",
    "fsm_courier_storage",
    "customer_bot_id",
    "courier_bot_id",
]
