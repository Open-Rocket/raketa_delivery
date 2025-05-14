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
    DOMAIN,
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
    if not secret or len(secret) < 16:
        raise ValueError(
            f"Секрет для бота {bot} пустой или слишком короткий (мин. 16 символов)"
        )


@web.middleware
async def log_requests_middleware(request, handler):
    log.info(f"Входящий запрос: {request.method} {request.path}")
    return await handler(request)


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


async def on_startup(app: web.Application):
    try:
        # Установка вебхуков с секретами (используем единый DOMAIN)
        await customer_bot.set_webhook(
            f"{DOMAIN}/webhook/customer",
            secret_token=WEBHOOK_SECRET["customer"],
            allowed_updates=["message", "callback_query"],
        )
        await courier_bot.set_webhook(
            f"{DOMAIN}/webhook/courier",
            secret_token=WEBHOOK_SECRET["courier"],
            allowed_updates=["message", "callback_query"],
        )
        await admin_bot.set_webhook(
            f"{DOMAIN}/webhook/admin",
            secret_token=WEBHOOK_SECRET["admin"],
            allowed_updates=["message", "callback_query"],
        )
        await partner_bot.set_webhook(
            f"{DOMAIN}/webhook/partner",
            secret_token=WEBHOOK_SECRET["partner"],
            allowed_updates=["message", "callback_query"],
        )
        log.info("🔗 Вебхуки установлены")
    except Exception as e:
        log.error(f"Ошибка установки вебхуков: {e}")
        raise


async def on_shutdown(_: web.Application):
    try:
        await customer_bot.delete_webhook()
        await courier_bot.delete_webhook()
        await admin_bot.delete_webhook()
        await partner_bot.delete_webhook()
        await rediska.redis.aclose()
        # Закрываем сессии ботов
        await customer_bot.session.close()
        await courier_bot.session.close()
        await admin_bot.session.close()
        await partner_bot.session.close()
        log.warning("❌ Остановлено корректно")
    except Exception as e:
        log.error(f"Ошибка при остановке: {e}")


async def main():
    await setup_dispatchers()
    app = web.Application(middlewares=[log_requests_middleware])
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
    await asyncio.gather(site.start(), main_worker())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.warning("⛔ KeyboardInterrupt: остановка вручную.")

# import asyncio
# from src.confredis import rediska
# from src.app.customer import customer_r, customer_fallback
# from src.app.courier import courier_r, courier_fallback, payment_r
# from src.app.admin import admin_r, admin_fallback
# from src.app.partner import partner_r, partner_fallback
# from aiogram.exceptions import TelegramBadRequest
# from src.tasks.worker import main_worker


# from src.middlewares import (
#     CustomerOuterMiddleware,
#     CourierOuterMiddleware,
#     AdminOuterMiddleware,
#     AgentOuterMiddleware,
# )
# from src.config import (
#     customer_bot,
#     courier_bot,
#     admin_bot,
#     partner_bot,
#     customer_dp,
#     courier_dp,
#     admin_dp,
#     partner_dp,
#     log,
# )


# async def main():

#     customer_dp.update()
#     courier_dp.update()
#     admin_dp.update()
#     partner_dp.update()

#     customer_dp["redis"] = rediska
#     courier_dp["redis"] = rediska
#     admin_dp["redis"] = rediska
#     partner_dp["redis"] = rediska

#     customer_dp.message.middleware(CustomerOuterMiddleware(rediska))
#     customer_dp.callback_query.middleware(CustomerOuterMiddleware(rediska))

#     courier_dp.message.middleware(CourierOuterMiddleware(rediska))
#     courier_dp.callback_query.middleware(CourierOuterMiddleware(rediska))

#     admin_dp.message.middleware(AdminOuterMiddleware(rediska))
#     admin_dp.callback_query.middleware(AdminOuterMiddleware(rediska))

#     partner_dp.message.middleware(AgentOuterMiddleware(rediska))
#     partner_dp.callback_query.middleware(AgentOuterMiddleware(rediska))

#     customer_dp.include_routers(customer_r, customer_fallback)
#     courier_dp.include_routers(courier_r, payment_r, courier_fallback)
#     admin_dp.include_routers(admin_r, admin_fallback)
#     partner_dp.include_routers(partner_r, partner_fallback)

#     try:

#         await asyncio.gather(
#             customer_dp.start_polling(customer_bot, skip_updates=True),
#             courier_dp.start_polling(courier_bot, skip_updates=True),
#             admin_dp.start_polling(admin_bot, skip_updates=True),
#             partner_dp.start_polling(partner_bot, skip_updates=True),
#             main_worker(),
#         )

#     except Exception as e:
#         log.error(f"Глобальная ошибка: {e}")
#     finally:
#         await rediska.redis.aclose()


# if __name__ == "__main__":
#     try:
#         asyncio.run(main())

#     except KeyboardInterrupt:
#         log.warning("⛔ KeyboardInterrupt: остановка вручную.")
