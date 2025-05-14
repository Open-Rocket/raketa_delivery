import asyncio
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

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
    SUBDOMAIN_CUSTOMER,
    SUBDOMAIN_COURIER,
    SUBDOMAIN_ADMIN,
    SUBDOMAIN_PARTNER,
    customer_bot_secret,
    courier_bot_secret,
    admin_bot_secret,
    partner_bot_secret,
)

# Секреты вебхуков
WEBHOOK_SECRET = {
    "customer": customer_bot_secret,
    "courier": courier_bot_secret,
    "admin": admin_bot_secret,
    "partner": partner_bot_secret,
}

# Проверка секретов
for bot, secret in WEBHOOK_SECRET.items():
    log.info(f"customer_bot_secret: {customer_bot_secret}")
    log.info(f"courier_bot_secret: {courier_bot_secret}")
    log.info(f"admin_bot_secret: {admin_bot_secret}")
    log.info(f"partner_bot_secret: {partner_bot_secret}")
    if not secret or len(secret) < 16:
        raise ValueError(
            f"Секрет для бота {bot} пустой или слишком короткий (мин. 16 символов)"
        )


# Middleware для логирования входящих запросов
async def log_requests_middleware(handler):
    async def middleware(request):
        log.info(f"Входящий запрос: {request.method} {request.path}")
        response = await handler(request)
        return response

    return middleware


async def setup_dispatchers():
    # Роутеры
    customer_dp.include_routers(customer_r, customer_fallback)
    courier_dp.include_routers(courier_r, payment_r, courier_fallback)
    admin_dp.include_routers(admin_r, admin_fallback)
    partner_dp.include_routers(partner_r, partner_fallback)

    # Redis
    for dp in (customer_dp, courier_dp, admin_dp, partner_dp):
        dp.update()
        dp["redis"] = rediska

    # Middleware
    customer_dp.message.middleware(CustomerOuterMiddleware(rediska))
    customer_dp.callback_query.middleware(CustomerOuterMiddleware(rediska))
    courier_dp.message.middleware(CourierOuterMiddleware(rediska))
    courier_dp.callback_query.middleware(CourierOuterMiddleware(rediska))
    admin_dp.message.middleware(AdminOuterMiddleware(rediska))
    admin_dp.callback_query.middleware(AdminOuterMiddleware(rediska))
    partner_dp.message.middleware(AgentOuterMiddleware(rediska))
    partner_dp.callback_query.middleware(AgentOuterMiddleware(rediska))


async def on_startup(_: web.Application):  # Добавлен параметр app
    IP_TG = "149.154.160.0/20"
    try:
        # Установка вебхуков с секретами и ограничением IP Telegram
        await customer_bot.set_webhook(
            f"{SUBDOMAIN_CUSTOMER}/webhook/customer",
            secret_token=WEBHOOK_SECRET["customer"],
            allowed_updates=["message", "callback_query"],
            ip_address=IP_TG,
        )
        await courier_bot.set_webhook(
            f"{SUBDOMAIN_COURIER}/webhook/courier",
            secret_token=WEBHOOK_SECRET["courier"],
            allowed_updates=["message", "callback_query"],
            ip_address=IP_TG,
        )
        await admin_bot.set_webhook(
            f"{SUBDOMAIN_ADMIN}/webhook/admin",
            secret_token=WEBHOOK_SECRET["admin"],
            allowed_updates=["message", "callback_query"],
            ip_address=IP_TG,
        )
        await partner_bot.set_webhook(
            f"{SUBDOMAIN_PARTNER}/webhook/partner",
            secret_token=WEBHOOK_SECRET["partner"],
            allowed_updates=["message", "callback_query"],
            ip_address=IP_TG,
        )
        log.info("🔗 Вебхуки установлены")
    except Exception as e:
        log.error(f"Ошибка установки вебхуков: {e}")
        raise


async def on_shutdown(_: web.Application):  # Добавлен параметр app
    try:
        await customer_bot.delete_webhook()
        await courier_bot.delete_webhook()
        await admin_bot.delete_webhook()
        await partner_bot.delete_webhook()
        await rediska.redis.aclose()
        log.warning("❌ Остановлено корректно")
    except Exception as e:
        log.error(f"Ошибка при остановке: {e}")


async def main():
    await setup_dispatchers()
    app = web.Application()
    app.middlewares.append(log_requests_middleware)
    # Привязываем каждый диспетчер к своему пути с секретами
    SimpleRequestHandler(
        dispatcher=customer_dp,
        bot=customer_bot,
        secret_token=WEBHOOK_SECRET["customer"],
    ).register(app, path="/webhook/customer")
    SimpleRequestHandler(
        dispatcher=courier_dp,
        bot=courier_bot,
        secret_token=WEBHOOK_SECRET["courier"],
    ).register(app, path="/webhook/courier")
    SimpleRequestHandler(
        dispatcher=admin_dp,
        bot=admin_bot,
        secret_token=WEBHOOK_SECRET["admin"],
    ).register(app, path="/webhook/admin")
    SimpleRequestHandler(
        dispatcher=partner_dp,
        bot=partner_bot,
        secret_token=WEBHOOK_SECRET["partner"],
    ).register(app, path="/webhook/partner")
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    # Aiogram внутренняя настройка
    setup_application(app, customer_dp, bot=customer_bot)
    setup_application(app, courier_dp, bot=courier_bot)
    setup_application(app, admin_dp, bot=admin_bot)
    setup_application(app, partner_dp, bot=partner_bot)
    # Запускаем параллельно воркеры и aiohttp
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 80)
    await site.start()
    await main_worker()  # Ваш таск-планировщик


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.warning("⛔ KeyboardInterrupt: остановка вручную.")
