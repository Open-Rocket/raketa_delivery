import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiogram.exceptions import TelegramBadRequest

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
    SUBDOMAIN_CUSTOMER,
    SUBDOMAIN_COURIER,
    SUBDOMAIN_ADMIN,
    SUBDOMAIN_PARTNER,
)

app = web.Application()


async def handle_webhook(request: web.Request):
    bot_name = request.match_info.get("bot_name")
    body = await request.json()
    update = Update.model_validate(body)

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

    return web.Response(status=200)


async def setup_bot(
    dp: Dispatcher,
    bot: Bot,
    route: str,
    middleware_cls,
    routers: list,
    domain: str,
):
    dp.update()
    dp["redis"] = rediska

    dp.message.middleware(middleware_cls(rediska))
    dp.callback_query.middleware(middleware_cls(rediska))
    dp.include_routers(*routers)

    webhook_url = f"{domain}/{route}"
    try:
        await bot.set_webhook(webhook_url)
        log.info(f"Установлен webhook: {webhook_url}")
    except TelegramBadRequest as e:
        log.error(f"Ошибка установки вебхука: {e}")
        raise

    app.router.add_post(
        f"/{route}",
        handle_webhook,
        name=f"{route}",
    )


async def main():
    try:
        await asyncio.gather(
            setup_bot(
                customer_dp,
                customer_bot,
                "customer",
                CustomerOuterMiddleware,
                [customer_r, customer_fallback],
                domain=f"https://customer.raketago.ru",
            ),
            setup_bot(
                courier_dp,
                courier_bot,
                "courier",
                CourierOuterMiddleware,
                [courier_r, payment_r, courier_fallback],
                domain=f"https://courier.raketago.ru",
            ),
            setup_bot(
                admin_dp,
                admin_bot,
                "admin",
                AdminOuterMiddleware,
                [admin_r, admin_fallback],
                domain=f"https://admin.raketago.ru",
            ),
            setup_bot(
                partner_dp,
                partner_bot,
                "partner",
                AgentOuterMiddleware,
                [partner_r, partner_fallback],
                domain=f"https://partner.raketago.ru",
            ),
            main_worker(),
        )
    except Exception as e:
        log.error(f"🔥 Глобальная ошибка: {e}")
    finally:
        await rediska.redis.aclose()


if __name__ == "__main__":
    try:
        asyncio.run(main())
        web.run_app(app, host="0.0.0.0", port=80)
    except KeyboardInterrupt:
        log.warning("⛔ KeyboardInterrupt: остановка вручную.")
