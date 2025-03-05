import asyncio
from src.confredis import rediska
from src.app.customer import customer_r, customer_fallback
from src.app.courier import courier_r, courier_fallback, payment_r
from src.config import (
    customer_bot,
    courier_bot,
    customer_dp,
    courier_dp,
    log,
)


async def main():

    customer_dp["redis"] = rediska
    courier_dp["redis"] = rediska

    customer_dp.include_routers(customer_r, customer_fallback)
    courier_dp.include_routers(courier_r, payment_r, courier_fallback)

    try:
        await asyncio.gather(
            customer_dp.start_polling(customer_bot, skip_updates=True),
            courier_dp.start_polling(courier_bot, skip_updates=True),
        )
    finally:
        await rediska.redis.aclose()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.error("Exit")
