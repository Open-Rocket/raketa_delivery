import asyncio
import logging
from src.models import drop_create_db
from src.confredis import rediska
from src.app.customer import customer_r, customer_fallback
from src.config import (
    customer_bot,
    couriers_bot,
    customer_dp,
    courier_dp,
    # customer_r,
    courier_r,
    # customer_fallback,
    courier_fallback,
    payment_r,
    log,
)

# import os
# from aiogram import Bot, Dispatcher, Router
# from dotenv import load_dotenv


async def main():

    # customer_dp["redis"] = rediska
    # courier_dp["redis"] = rediska

    customer_dp.include_routers(customer_r, customer_fallback)
    courier_dp.include_routers(courier_r, payment_r, courier_fallback)

    customer_dp.startup.register(on_startup)

    try:
        await asyncio.gather(
            customer_dp.start_polling(customer_bot, skip_updates=True),
            courier_dp.start_polling(couriers_bot, skip_updates=True),
        )
    finally:
        await rediska.redis.aclose()


async def on_startup(dispatcher):
    await drop_create_db()


if __name__ == "__main__":
    # logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.error("Exit")
