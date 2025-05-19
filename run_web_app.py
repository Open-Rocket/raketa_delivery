import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import Update

from src.confredis import rediska
from src.app.customer import customer_r, customer_fallback
from src.app.courier import courier_r, courier_fallback, payment_r
from src.app.admin import admin_r, admin_fallback
from src.app.partner import partner_r, partner_fallback
from src.tasks.worker import main_worker
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
    customer_bot_secret,
    courier_bot_secret,
    admin_bot_secret,
    partner_bot_secret,
)

app = web.Application()


def setup_dispatchers():
    """Инициализация диспетчеров (синхронная часть)"""
    # Customer
    customer_dp["bot"] = customer_bot
    customer_dp["redis"] = rediska
    customer_dp.message.middleware(CustomerOuterMiddleware(rediska))
    customer_dp.callback_query.middleware(CustomerOuterMiddleware(rediska))
    customer_dp.include_routers(customer_r, customer_fallback)

    # Courier
    courier_dp["bot"] = courier_bot
    courier_dp["redis"] = rediska
    courier_dp.message.middleware(CourierOuterMiddleware(rediska))
    courier_dp.callback_query.middleware(CourierOuterMiddleware(rediska))
    courier_dp.include_routers(courier_r, payment_r, courier_fallback)

    # Admin
    admin_dp["bot"] = admin_bot
    admin_dp["redis"] = rediska
    admin_dp.message.middleware(AdminOuterMiddleware(rediska))
    admin_dp.callback_query.middleware(AdminOuterMiddleware(rediska))
    admin_dp.include_routers(admin_r, admin_fallback)

    # Partner
    partner_dp["bot"] = partner_bot
    partner_dp["redis"] = rediska
    partner_dp.message.middleware(AgentOuterMiddleware(rediska))
    partner_dp.callback_query.middleware(AgentOuterMiddleware(rediska))
    partner_dp.include_routers(partner_r)


async def handle_webhook(request: web.Request):
    bot_name = request.path.strip("/")
    try:
        update = Update.model_validate(await request.json())
        log.debug(f"Update for {bot_name}: {update}")

        if bot_name == "customer":
            await customer_dp.feed_update(
                customer_bot,
                update,
            )
        elif bot_name == "courier":
            await courier_dp.feed_update(
                courier_bot,
                update,
            )
        elif bot_name == "admin":
            await admin_dp.feed_update(
                admin_bot,
                update,
            )
        elif bot_name == "partner":
            await partner_dp.feed_update(
                partner_bot,
                update,
            )
        else:
            return web.Response(status=404)

        return web.Response(status=200)
    except Exception as e:
        log.error(f"Error handling update: {e}")
        return web.Response(status=500)


async def set_webhooks():
    """Установка вебхуков для всех ботов"""
    webhooks = [
        (
            customer_bot,
            "customer",
            customer_bot_secret,
        ),
        (
            courier_bot,
            "courier",
            courier_bot_secret,
        ),
        (
            admin_bot,
            "admin",
            admin_bot_secret,
        ),
        (
            partner_bot,
            "partner",
            partner_bot_secret,
        ),
    ]

    for bot, name, secret in webhooks:
        await bot.set_webhook(
            f"https://{name}.raketago.ru/{name}",
            secret_token=secret,
            drop_pending_updates=True,
        )
        log.info(f"Webhook set for {name}")


async def start_server():
    """Запуск веб-сервера"""
    app.router.add_post("/customer", handle_webhook)
    app.router.add_post("/courier", handle_webhook)
    app.router.add_post("/admin", handle_webhook)
    app.router.add_post("/partner", handle_webhook)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 80)
    await site.start()
    log.info("Server started at http://0.0.0.0:80")
    return runner


async def main():
    # Инициализация
    setup_dispatchers()  # Синхронная настройка диспетчеров
    await set_webhooks()

    # Запуск сервера
    runner = await start_server()

    # Запуск воркера в фоне
    worker_task = asyncio.create_task(main_worker())

    try:
        # Основной цикл
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        log.info("Shutting down...")
    finally:
        # Корректное завершение
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass

        await runner.cleanup()
        await rediska.redis.aclose()
        log.info("All resources released")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        log.critical(f"Fatal error: {e}")
