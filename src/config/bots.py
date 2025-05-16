import os
import secrets
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

fsm_customer_storage = MemoryStorage()
fsm_courier_storage = MemoryStorage()
fsm_admin_storage = MemoryStorage()
fsm_partner_storage = MemoryStorage()

load_dotenv()

SUPER_ADMIN_TG_ID = int(os.getenv("SUPER_ADMIN_TG_ID"))

DOMAIN = os.getenv("DOMAIN")
SUBDOMAIN_CUSTOMER = os.getenv("SUBDOMAIN_CUSTOMER")
SUBDOMAIN_COURIER = os.getenv("SUBDOMAIN_COURIER")
SUBDOMAIN_ADMIN = os.getenv("SUBDOMAIN_ADMIN")
SUBDOMAIN_PARTNER = os.getenv("SUBDOMAIN_PARTNER")

customer_bot_secret = os.getenv("CUSTOMER_BOT_SECRET")
courier_bot_secret = os.getenv("COURIER_BOT_SECRET")
admin_bot_secret = os.getenv("ADMIN_BOT_SECRET")
partner_bot_secret = os.getenv("PARTNER_BOT_SECRET")

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
    "DOMAIN",
    "SUBDOMAIN_CUSTOMER",
    "SUBDOMAIN_COURIER",
    "SUBDOMAIN_ADMIN",
    "SUBDOMAIN_PARTNER",
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
    "customer_bot_secret",
    "courier_bot_secret",
    "admin_bot_secret",
    "partner_bot_secret",
]
