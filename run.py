import asyncio
from src.confredis import rediska
from src.app.customer import customer_r, customer_fallback
from src.app.courier import courier_r, courier_fallback, payment_r
from src.app.admin import admin_r, admin_fallback
from src.app.partner import partner_r, partner_fallback
from src.utils.tasks import send_notification_to_couriers
from aiogram.exceptions import TelegramBadRequest
from src.tasks.worker import main_worker
from src.tasks.scheduler import main_scheduler


from src.middlewares import (
    CustomerOuterMiddleware,
    CourierOuterMiddleware,
    AdminOuterMiddleware,
    AgentOuterMiddleware,
)
from src.config import (
    customer_bot,
    courier_bot,
    admin_bot,
    partner_bot,
    customer_dp,
    courier_dp,
    admin_dp,
    partner_dp,
    log,
)


async def main():

    customer_dp.update()
    courier_dp.update()
    admin_dp.update()
    partner_dp.update()

    customer_dp["redis"] = rediska
    courier_dp["redis"] = rediska
    admin_dp["redis"] = rediska
    partner_dp["redis"] = rediska

    customer_dp.message.middleware(CustomerOuterMiddleware(rediska))
    customer_dp.callback_query.middleware(CustomerOuterMiddleware(rediska))

    courier_dp.message.middleware(CourierOuterMiddleware(rediska))
    courier_dp.callback_query.middleware(CourierOuterMiddleware(rediska))

    admin_dp.message.middleware(AdminOuterMiddleware(rediska))
    admin_dp.callback_query.middleware(AdminOuterMiddleware(rediska))

    partner_dp.message.middleware(AgentOuterMiddleware(rediska))
    partner_dp.callback_query.middleware(AgentOuterMiddleware(rediska))

    customer_dp.include_routers(customer_r, customer_fallback)
    courier_dp.include_routers(courier_r, payment_r, courier_fallback)
    admin_dp.include_routers(admin_r, admin_fallback)
    partner_dp.include_routers(partner_r, partner_fallback)

    try:

        await asyncio.gather(
            customer_dp.start_polling(customer_bot, skip_updates=True),
            courier_dp.start_polling(courier_bot, skip_updates=True),
            admin_dp.start_polling(admin_bot, skip_updates=True),
            partner_dp.start_polling(partner_bot, skip_updates=True),
            main_worker(),
            main_scheduler(),
        )

    finally:
        await rediska.redis.aclose()


if __name__ == "__main__":
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        log.warning("⛔ KeyboardInterrupt: остановка вручную.")
