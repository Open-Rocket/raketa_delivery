import asyncio
import inspect
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import Update, Message
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest

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

# Устанавливаем DEBUG-логирование
log.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)

app = web.Application()

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
    path = request.path.lstrip("/")
    bot_name = path
    log.debug(f"Начало обработки вебхука для bot_name: {bot_name}")

    # Проверка секрета
    expected_secret = WEBHOOK_SECRET.get(bot_name)
    received_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")

    if not expected_secret:
        log.error(f"Секрет для {bot_name} не найден")
        return web.Response(status=500, text="Server configuration error")

    if not received_secret:
        log.error(
            f"Заголовок X-Telegram-Bot-Api-Secret-Token отсутствует для {bot_name}"
        )
        return web.Response(status=403, text="Missing webhook secret")

    if received_secret != expected_secret:
        log.error(
            f"Неверный секрет для {bot_name}: ожидался {expected_secret[:4]}****, получен {received_secret[:4]}****"
        )
        return web.Response(status=403, text="Invalid webhook secret")

    log.debug(f"Секрет для {bot_name} успешно проверен")

    try:
        body = await request.json()
        log.debug(f"Получен JSON: {body}")
    except Exception as e:
        log.error(f"Неверный JSON в запросе {request.path}: {e}")
        return web.Response(status=400, text="Invalid JSON")

    try:
        update = Update.model_validate(body)
        log.debug(f"Валидированное обновление: {update}")
    except Exception as e:
        log.error(f"Ошибка валидации обновления для {bot_name}: {e}")
        return web.Response(status=400, text="Invalid update")

    try:
        if bot_name == "customer":
            log.debug(f"Подача обновления в customer_dp")
            await customer_dp.feed_update(customer_bot, update)
        elif bot_name == "courier":
            log.debug(f"Подача обновления в courier_dp")
            await courier_dp.feed_update(courier_bot, update)
        elif bot_name == "admin":
            log.debug(f"Подача обновления в admin_dp")
            await admin_dp.feed_update(admin_bot, update)
        elif bot_name == "partner":
            log.debug(f"Подача обновления в partner_dp")
            await partner_dp.feed_update(partner_bot, update)
        else:
            log.error(f"Неизвестный bot_name: {bot_name}")
            return web.Response(status=404, text="Bot not found")
        log.debug(f"Обновление успешно обработано для {bot_name}")
    except Exception as e:
        log.error(f"Ошибка обработки обновления для {bot_name}: {e}")
        return web.Response(status=500, text="Internal server error")

    return web.Response(status=200, text="OK")


def setup_dispatcher(dp: Dispatcher, bot: Bot, middleware_cls, routers: list):
    log.debug(f"Настройка диспетчера {dp.name}")
    dp.update()
    dp["redis"] = rediska
    dp["bot"] = bot

    dp.message.middleware(middleware_cls(rediska))
    dp.callback_query.middleware(middleware_cls(rediska))
    dp.include_routers(*routers)

    # Тестовый хендлер для проверки
    @dp.message(Command("test"))
    async def test_handler(message: Message):
        log.debug(f"Тестовый хендлер сработал для {dp.name}: {message.text}")
        await message.answer(f"Бот {dp.name} работает! Тест пройден.")

    async def log_update(update: Update, *args, **kwargs):
        log.debug(f"Получено обновление для бота {dp.name}: {update}")

    dp.update.outer_middleware()(log_update)
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
        for bot_name, secret in WEBHOOK_SECRET.items():
            log.debug(f"Установка webhook для {bot_name} с секретом: {secret[:4]}****")
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
        log.error(f"❌ Критическая ошибка установки webhook: {e}")
        raise


async def start_web_server():
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 80)
    await site.start()
    log.info("🚀 Веб-сервер запущен на http://0.0.0.0:80")


async def main():
    # Настройка диспетчеров как в polling
    setup_dispatcher(
        customer_dp,
        customer_bot,
        CustomerOuterMiddleware,
        [customer_r, customer_fallback],
    )
    setup_dispatcher(
        courier_dp,
        courier_bot,
        CourierOuterMiddleware,
        [courier_r, payment_r, courier_fallback],
    )
    setup_dispatcher(
        admin_dp,
        admin_bot,
        AdminOuterMiddleware,
        [admin_r, admin_fallback],
    )
    setup_dispatcher(
        partner_dp,
        partner_bot,
        AgentOuterMiddleware,
        [partner_r, partner_fallback],
    )

    # Запуск диспетчеров
    async def run_startup(dp, name):
        try:
            if inspect.iscoroutinefunction(dp.startup):
                await dp.startup()
                log.info(f"✅ Диспетчер {name} запущен (async startup)")
            else:
                await asyncio.to_thread(dp.startup)
                log.info(f"✅ Диспетчер {name} запущен (sync startup)")
        except Exception as e:
            log.error(f"❌ Ошибка запуска диспетчера {name}: {e}")
            raise

    await asyncio.gather(
        run_startup(customer_dp, "customer"),
        run_startup(courier_dp, "courier"),
        run_startup(admin_dp, "admin"),
        run_startup(partner_dp, "partner"),
    )

    app.middlewares.append(log_requests_middleware)

    app.router.add_post("/customer", handle_webhook)
    app.router.add_post("/courier", handle_webhook)
    app.router.add_post("/admin", handle_webhook)
    app.router.add_post("/partner", handle_webhook)

    await set_webhooks()
    await start_web_server()

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
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for bot_name, result in zip(
            ["customer", "courier", "admin", "partner"], results
        ):
            if isinstance(result, Exception):
                log.error(f"Ошибка удаления вебхука для {bot_name}: {result}")
            else:
                log.info(f"🗑 Вебхук удалён для {bot_name}")

        sessions = [
            customer_bot.session.close(),
            courier_bot.session.close(),
            admin_bot.session.close(),
            partner_bot.session.close(),
        ]
        results = await asyncio.gather(*sessions, return_exceptions=True)
        for bot_name, result in zip(
            ["customer", "courier", "admin", "partner"], results
        ):
            if isinstance(result, Exception):
                log.error(f"Ошибка закрытия сессии для {bot_name}: {result}")
            else:
                log.info(f"🔌 Сессия закрыта для {bot_name}")

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
