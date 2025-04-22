# worker.py
import asyncio
import aio_pika
from src.config import log
from src.tasks.notifications import (
    new_orders_notification,
    city_couriers_notification,
    XP_points_notification,
)

RABBIT_URL = "amqp://guest:guest@localhost/"


async def handle_message(message: aio_pika.IncomingMessage):
    async with message.process():
        try:
            payload = message.body.decode()
            log.info(f"Получено сообщение из RabbitMQ: {payload}")

            if payload == "notify_new_orders":
                await new_orders_notification()
            elif payload == "notify_city_couriers":
                await city_couriers_notification()
            elif payload == "notify_XP":
                await XP_points_notification()
            else:
                log.warning(f"Неизвестная команда: {payload}")

        except Exception as e:
            log.error(f"Ошибка при обработке сообщения: {e}")


async def main_worker():
    connection = await aio_pika.connect_robust(RABBIT_URL)
    channel = await connection.channel()
    queue = await channel.declare_queue("notifications", durable=True)
    await queue.consume(handle_message)
    log.info("⏳ Ожидаю сообщения в очереди 'notifications'...")
    await asyncio.Future()  # Бесконечное ожидание


if __name__ == "__main__":
    try:
        asyncio.run(main_worker())
    except KeyboardInterrupt:
        log.info("RabbitMQ воркер остановлен вручную.")
