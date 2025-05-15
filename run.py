import asyncio
import logging
from aiohttp import web
from aiogram.types import Update
from aiogram import Bot, Dispatcher

from src.tasks.worker import main_worker
from src.confredis import rediska
from src.app.customer import customer_r, customer_fallback
from src.app.courier import courier_r, courier_fallback, payment_r
from src.app.admin import admin_r, admin_fallback
from src.app.partner import partner_r, partner_fallback
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

WEBHOOK_SECRET = {
    "customer": customer_bot_secret,
    "courier": courier_bot_secret,
    "admin": admin_bot_secret,
    "partner": partner_bot_secret,
}


@web.middleware
async def log_requests_middleware(request, handler):
    log.debug(f"Входящий запрос: {request.method} {request.path}")
    try:
        response = await handler(request)
        return response
    except Exception as e:
        log.error(f"Ошибка обработки запроса: {e}")
        raise


app.middlewares.append(log_requests_middleware)


async def handle_webhook(request: web.Request):
    bot_name = request.path.strip("/")
    try:
        body = await request.json()
        update = Update.model_validate(body)
    except Exception as e:
        log.error(f"Ошибка разбора update: {e}")
        return web.Response(status=400)

    bot: Bot = None
    dp: Dispatcher = None

    if bot_name == "customer":
        bot, dp = customer_bot, customer_dp
    elif bot_name == "courier":
        bot, dp = courier_bot, courier_dp
    elif bot_name == "admin":
        bot, dp = admin_bot, admin_dp
    elif bot_name == "partner":
        bot, dp = partner_bot, partner_dp
    else:
        return web.Response(status=404)

    try:
        await dp.feed_update(bot, update)
    except Exception as e:
        log.error(f"Ошибка feed_update: {e}")
        return web.Response(status=500)

    return web.Response(status=200)


app.router.add_post("/customer", handle_webhook)
app.router.add_post("/courier", handle_webhook)
app.router.add_post("/admin", handle_webhook)
app.router.add_post("/partner", handle_webhook)


async def setup_dispatchers():
    # Сохраняем redis и bot в Dispatcher
    customer_dp["redis"] = rediska
    courier_dp["redis"] = rediska
    admin_dp["redis"] = rediska
    partner_dp["redis"] = rediska

    customer_dp["bot"] = customer_bot
    courier_dp["bot"] = courier_bot
    admin_dp["bot"] = admin_bot
    partner_dp["bot"] = partner_bot

    # Middleware
    customer_dp.message.middleware(CustomerOuterMiddleware(rediska))
    customer_dp.callback_query.middleware(CustomerOuterMiddleware(rediska))

    courier_dp.message.middleware(CourierOuterMiddleware(rediska))
    courier_dp.callback_query.middleware(CourierOuterMiddleware(rediska))

    admin_dp.message.middleware(AdminOuterMiddleware(rediska))
    admin_dp.callback_query.middleware(AdminOuterMiddleware(rediska))

    partner_dp.message.middleware(AgentOuterMiddleware(rediska))
    partner_dp.callback_query.middleware(AgentOuterMiddleware(rediska))

    # Routers
    customer_dp.include_routers(customer_r, customer_fallback)
    courier_dp.include_routers(courier_r, payment_r, courier_fallback)
    admin_dp.include_routers(admin_r, admin_fallback)
    partner_dp.include_routers(partner_r, partner_fallback)

    log.info("✅ Диспетчеры настроены")


async def set_webhooks():
    await asyncio.gather(
        customer_bot.set_webhook(
            "https://customer.raketago.ru/customer",
            secret_token=customer_bot_secret,
            drop_pending_updates=True,
        ),
        courier_bot.set_webhook(
            "https://courier.raketago.ru/courier",
            secret_token=courier_bot_secret,
            drop_pending_updates=True,
        ),
        admin_bot.set_webhook(
            "https://admin.raketago.ru/admin",
            secret_token=admin_bot_secret,
            drop_pending_updates=True,
        ),
        partner_bot.set_webhook(
            "https://partner.raketago.ru/partner",
            secret_token=partner_bot_secret,
            drop_pending_updates=True,
        ),
    )

    log.info("✅ Вебхуки установлены")


async def main():
    await setup_dispatchers()
    await set_webhooks()

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=80)
    await site.start()
    log.info("🚀 Веб-сервер запущен: http://0.0.0.0:80")

    await asyncio.gather(
        customer_dp.startup(),
        courier_dp.startup(),
        admin_dp.startup(),
        partner_dp.startup(),
        # main_worker(),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log.warning("🛑 Завершение работы...")
