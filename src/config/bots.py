import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

fsm_customer_storage = MemoryStorage()
fsm_courier_storage = MemoryStorage()
fsm_admin_storage = MemoryStorage()
fsm_partner_storage = MemoryStorage()

load_dotenv()

SUPER_ADMIN_TG_ID = int(os.getenv("SUPER_ADMIN_TG_ID"))

customer_bot = Bot(token=os.getenv("CUSTOMER_BOT"))
courier_bot = Bot(token=os.getenv("COURIER_BOT"))
admin_bot = Bot(token=os.getenv("ADMIN_BOT"))
partner_bot = Bot(token=os.getenv("AGENT_BOT"))


customer_bot_id = customer_bot.id
courier_bot_id = courier_bot.id
admin_bot_id = admin_bot.id
partner_bot_id = partner_bot.id


customer_dp = Dispatcher(storage=fsm_customer_storage)
courier_dp = Dispatcher(storage=fsm_courier_storage)
admin_dp = Dispatcher(storage=fsm_admin_storage)
partner_dp = Dispatcher(storage=fsm_partner_storage)


__all__ = [
    "SUPER_ADMIN_TG_ID",
    "customer_bot",
    "customer_bot_id",
    "customer_dp",
    "fsm_customer_storage",
    "courier_bot",
    "courier_bot_id",
    "courier_dp",
    "fsm_courier_storage",
    "admin_bot",
    "admin_bot_id",
    "admin_dp",
    "fsm_admin_storage",
    "partner_bot",
    "partner_bot_id",
    "partner_dp",
    "fsm_partner_storage",
]
