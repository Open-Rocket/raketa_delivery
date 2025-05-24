import asyncio
from src.confredis import rediska
from src.app.customer import customer_r, customer_fallback


from src.middlewares import (
    CustomerOuterMiddleware,
)
from src.config import (
    customer_bot_dev,
    customer_dp,
    log,
)


async def main():

    customer_dp.update()

    customer_dp["redis"] = rediska

    customer_dp.message.middleware(CustomerOuterMiddleware(rediska))
    customer_dp.callback_query.middleware(CustomerOuterMiddleware(rediska))

    customer_dp.include_routers(customer_r, customer_fallback)

    try:

        await customer_dp.start_polling(customer_bot_dev, skip_updates=True)

    except Exception as e:
        log.error(f"Глобальная ошибка: {e}")
    finally:
        await rediska.redis.aclose()


if __name__ == "__main__":
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        log.warning("⛔ KeyboardInterrupt: остановка вручную.")
