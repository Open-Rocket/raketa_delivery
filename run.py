import os
import asyncio
import logging
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from app.u_pack.u_rout import users_router
from app.c_pack.c_rout import couriers_router
from app.admin_pack.admin_rout import admin_router
from app.u_pack.u_fallback_rout import fallback_router
from app.c_pack.c_test_payment import test_payment_router
from app.database.models import async_main


async def main():
    load_dotenv()

    users_bot = Bot(token=os.getenv('U_TOKEN'))
    couriers_bot = Bot(token=os.getenv('C_TOKEN'))

    u_dp = Dispatcher()
    c_dp = Dispatcher()

    u_dp.include_routers(users_router, fallback_router)
    c_dp.include_routers(couriers_router, test_payment_router)

    u_dp.startup.register(on_startup)
    # await u_dp.start_polling(users_bot, skip_updates=True)

    await asyncio.gather(
        u_dp.start_polling(users_bot, skip_updates=True),
        c_dp.start_polling(couriers_bot, skip_updates=True)
    )


async def on_startup(dispatcher):
    await async_main()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
