import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiogram.exceptions import TelegramBadRequest

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

for bot, secret in WEBHOOK_SECRET.items():
    if not secret or len(secret) < 16:
        raise ValueError(
            f"Секрет для бота {bot} пустой или слишком короткий (мин. 16 символов)"
        )
    log.debug(f"Секрет для {bot}: {secret[:4]}**** (длина: {len(secret)})")


@web.middleware
async def log_requests_middleware(request, handler):
    log.debug(f"Входящий запрос: {request.method} {request.path} {request.headers}")
    try:
        body = await request.text()
        log.debug(f"Тело запроса: {body}")
        response = await handler(request)
        log.debug(f"Ответ: {response.status} {response.text}")
        return response
    except Exception as e:
        log.error(f"Ошибка обработки запроса {request.path}: {e}")
        raise


async def handle_webhook(request: web.Request):
    bot_name = request.path.lstrip("/")
    log.debug(f"Обработка вебхука для: {bot_name}")

    expected_secret = WEBHOOK_SECRET.get(bot_name)
    received_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")

    if not expected_secret:
        return web.Response(status=500, text="Server configuration error")
    if not received_secret:
        return web.Response(status=403, text="Missing webhook secret")
    if received_secret != expected_secret:
        return web.Response(status=403, text="Invalid webhook secret")

    try:
        body = await request.json()
        update = Update.model_validate(body)
    except Exception as e:
        log.error(f"Ошибка разбора JSON/валидации: {e}")
        return web.Response(status=400, text="Invalid update")

    try:
        if bot_name == "customer":
            await customer_dp.feed_update(customer_bot, update)
        elif bot_name == "courier":
            await courier_dp.feed_update(courier_bot, update)
        elif bot_name == "admin":
            await admin_dp.feed_update(admin_bot, update)
        elif bot_name == "partner":
            await partner_dp.feed_update(partner_bot, update)
        else:
            return web.Response(status=404, text="Bot not found")
    except Exception as e:
        log.error(f"Ошибка обработки обновления для {bot_name}: {e}")
        return web.Response(status=500, text="Internal server error")

    return web.Response(status=200, text="OK")


async def setup_dispatcher(dp: Dispatcher, bot: Bot, middleware_cls, routers: list):
    dp.update()
    dp["redis"] = rediska
    dp["bot"] = bot

    dp.message.middleware(middleware_cls(rediska))
    dp.callback_query.middleware(middleware_cls(rediska))
    dp.include_routers(*routers)

    dp.resolve_used_update_types()
    log.debug(f"Диспетчер {dp.name} настроен")


async def set_webhooks():
    try:
        tasks = [
            customer_bot.set_webhook(
                "https://customer.raketago.ru/customer",
                secret_token=WEBHOOK_SECRET["customer"],
                drop_pending_updates=True,
            ),
            courier_bot.set_webhook(
                "https://courier.raketago.ru/courier",
                secret_token=WEBHOOK_SECRET["courier"],
                drop_pending_updates=True,
            ),
            admin_bot.set_webhook(
                "https://admin.raketago.ru/admin",
                secret_token=WEBHOOK_SECRET["admin"],
                drop_pending_updates=True,
            ),
            partner_bot.set_webhook(
                "https://partner.raketago.ru/partner",
                secret_token=WEBHOOK_SECRET["partner"],
                drop_pending_updates=True,
            ),
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for bot_name, result in zip(
            ["customer", "courier", "admin", "partner"], results
        ):
            if isinstance(result, Exception):
                log.error(f"❌ Ошибка установки webhook для {bot_name}: {result}")
            else:
                log.info(
                    f"✅ Webhook установлен: https://{bot_name}.raketago.ru/{bot_name}"
                )
    except TelegramBadRequest as e:
        log.error(f"Критическая ошибка установки webhook: {e}")
        raise


async def start_web_server():
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 80)
    await site.start()
    log.info("🚀 Веб-сервер запущен на http://0.0.0.0:80")


async def main():
    await setup_dispatcher(
        customer_dp,
        customer_bot,
        CustomerOuterMiddleware,
        [customer_r, customer_fallback],
    )
    await setup_dispatcher(
        courier_dp,
        courier_bot,
        CourierOuterMiddleware,
        [courier_r, payment_r, courier_fallback],
    )
    await setup_dispatcher(
        admin_dp, admin_bot, AdminOuterMiddleware, [admin_r, admin_fallback]
    )
    await setup_dispatcher(
        partner_dp, partner_bot, AgentOuterMiddleware, [partner_r, partner_fallback]
    )

    app.middlewares.append(log_requests_middleware)

    app.router.add_post("/customer", handle_webhook)
    app.router.add_post("/courier", handle_webhook)
    app.router.add_post("/admin", handle_webhook)
    app.router.add_post("/partner", handle_webhook)

    await set_webhooks()
    await start_web_server()

    try:
        await asyncio.gather(
            customer_dp.startup(customer_bot),
            courier_dp.startup(courier_bot),
            admin_dp.startup(admin_bot),
            partner_dp.startup(partner_bot),
            main_worker(),
        )
    except Exception as e:
        log.error(f"Ошибка при запуске диспетчеров: {e}")
    finally:
        await customer_bot.session.close()
        await courier_bot.session.close()
        await admin_bot.session.close()
        await partner_bot.session.close()

    while True:
        await asyncio.sleep(3600)


async def on_shutdown():
    try:
        tasks = [
            customer_bot.delete_webhook(drop_pending_updates=True),
            courier_bot.delete_webhook(drop_pending_updates=True),
            admin_bot.delete_webhook(drop_pending_updates=True),
            partner_bot.delete_webhook(drop_pending_updates=True),
        ]
        await asyncio.gather(*tasks, return_exceptions=True)

        sessions = [
            customer_bot.session.close(),
            courier_bot.session.close(),
            admin_bot.session.close(),
            partner_bot.session.close(),
        ]
        await asyncio.gather(*sessions, return_exceptions=True)

        await rediska.redis.aclose()
        log.warning("❌ Приложение остановлено корректно")
    except Exception as e:
        log.error(f"Ошибка при остановке: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        asyncio.run(on_shutdown())
        log.info("Боты корректно завершены.")
