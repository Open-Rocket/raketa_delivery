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


# Middleware для логирования запросов
@web.middleware
async def log_requests_middleware(request, handler):
    log.debug(f"Входящий запрос: {request.method} {request.path} {request.headers}")
    try:
        body = await request.text()
        log.debug(f"Тело запроса: {body}")
        response = await handler(request)
        log.debug(f"Ответ: {response.status}")
        return response
    except Exception as e:
        log.error(f"Ошибка обработки запроса {request.path}: {e}")
        raise


# Общий обработчик вебхуков
async def handle_webhook(request: web.Request):
    # Извлекаем bot_name из пути
    path = request.path.lstrip("/")
    bot_name = path  # Например, "customer" из "/customer"
    log.debug(f"Обработка вебхука для bot_name: {bot_name}")

    # Проверяем секрет вебхука
    expected_secret = WEBHOOK_SECRET.get(bot_name)
    received_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if expected_secret and received_secret != expected_secret:
        log.error(
            f"Неверный секрет вебхука для {bot_name}: ожидался {expected_secret}, получен {received_secret}"
        )
        return web.Response(status=403, text="Invalid webhook secret")

    # Парсим тело запроса
    try:
        body = await request.json()
    except Exception as e:
        log.error(f"Неверный JSON в запросе {request.path}: {e}")
        return web.Response(status=400, text="Invalid JSON")

    # Валидируем обновление
    try:
        update = Update.model_validate(body)
    except Exception as e:
        log.error(f"Ошибка валидации обновления для {bot_name}: {e}")
        return web.Response(status=400, text="Invalid update")

    # Перенаправляем обновление в соответствующий диспетчер
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
            log.error(f"Неизвестный bot_name: {bot_name}")
            return web.Response(status=404, text="Bot not found")
    except Exception as e:
        log.error(f"Ошибка обработки обновления для {bot_name}: {e}")
        return web.Response(status=500, text="Internal server error")

    return web.Response(status=200, text="OK")


# Функция настройки диспетчера
async def setup_dispatcher(
    dp: Dispatcher,
    bot: Bot,
    middleware_cls,
    routers: list,
):

    dp["redis"] = rediska
    dp["bot"] = bot

    dp.message.middleware(middleware_cls(rediska))
    dp.callback_query.middleware(middleware_cls(rediska))
    dp.include_routers(*routers)

    # Логирование обновлений
    async def log_update(update: Update, *args, **kwargs):
        log.debug(f"Получено обновление для бота {dp.name}: {update}")

    dp.update.outer_middleware()(log_update)


# Установка webhook'ов
async def set_webhooks():
    try:
        tasks = [
            customer_bot.set_webhook(
                "https://customer.raketago.ru/customer",
                secret_token=WEBHOOK_SECRET["customer"],
            ),
            courier_bot.set_webhook(
                "https://courier.raketago.ru/courier",
                secret_token=WEBHOOK_SECRET["courier"],
            ),
            admin_bot.set_webhook(
                "https://admin.raketago.ru/admin",
                secret_token=WEBHOOK_SECRET["admin"],
            ),
            partner_bot.set_webhook(
                "https://partner.raketago.ru/partner",
                secret_token=WEBHOOK_SECRET["partner"],
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
        log.error(f"❌ Критическая ошибка установки webhook: {e}")
        raise


# Старт веб-сервера aiohttp
async def start_web_server():
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 80)
    await site.start()
    log.info("🚀 Веб-сервер запущен на http://0.0.0.0:80")


async def main():
    # Настраиваем диспетчеры
    await asyncio.gather(
        setup_dispatcher(
            customer_dp,
            customer_bot,
            CustomerOuterMiddleware,
            [customer_r, customer_fallback],
        ),
        setup_dispatcher(
            courier_dp,
            courier_bot,
            CourierOuterMiddleware,
            [courier_r, payment_r, courier_fallback],
        ),
        setup_dispatcher(
            admin_dp,
            admin_bot,
            AdminOuterMiddleware,
            [admin_r, admin_fallback],
        ),
        setup_dispatcher(
            partner_dp,
            partner_bot,
            AgentOuterMiddleware,
            [partner_r, partner_fallback],
        ),
    )

    # Добавляем middleware для логирования
    app.middlewares.append(log_requests_middleware)

    # Добавляем маршруты для вебхуков
    app.router.add_post("/customer", handle_webhook)
    app.router.add_post("/courier", handle_webhook)
    app.router.add_post("/admin", handle_webhook)
    app.router.add_post("/partner", handle_webhook)

    # Устанавливаем webhook у ботов
    await set_webhooks()

    # Запускаем веб-сервер
    await start_web_server()

    # Запуск вечного цикла
    while True:
        await asyncio.sleep(3600)


async def on_shutdown():
    try:
        # Удаляем вебхуки
        tasks = [
            customer_bot.delete_webhook(),
            courier_bot.delete_webhook(),
            admin_bot.delete_webhook(),
            partner_bot.delete_webhook(),
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for bot_name, result in zip(
            ["customer", "courier", "admin", "partner"], results
        ):
            if isinstance(result, Exception):
                log.error(f"Ошибка удаления вебхука для {bot_name}: {result}")
            else:
                log.info(f"🗑 Вебхук удалён для {bot_name}")

        # Закрываем сессии ботов
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

        # Закрываем Redis
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
