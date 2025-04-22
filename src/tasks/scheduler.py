# scheduler.py
import asyncio
import aio_pika
from datetime import datetime, timedelta
from src.config import log
from src.services import admin_data

RABBIT_URL = "amqp://guest:guest@localhost/"

NOTIFICATIONS = [
    "notify_new_orders",
    "notify_city_couriers",
]


async def send_notification(command: str):
    connection = await aio_pika.connect_robust(RABBIT_URL)
    channel = await connection.channel()
    await channel.default_exchange.publish(
        aio_pika.Message(body=command.encode()), routing_key="notifications"
    )
    log.info(f"[{datetime.now().strftime('%H:%M:%S')}] Отправлена команда: {command}")
    await connection.close()


async def repeatable_notifications():
    while True:
        task_status = await admin_data.get_task_status()
        log.info(f"task-status: {task_status}")
        interval = await admin_data.get_new_orders_notification_interval()
        if task_status:
            for command in NOTIFICATIONS:
                await send_notification(command)
            log.info("✅ Уведомления отправлены. Ждём интервал...")
            log.info(f"interval: {interval}")
        else:
            log.info("⛔ Уведомления отключены администратором.")
        await asyncio.sleep(interval)


async def wait_until_target_time(hour: int, minute: int):
    now = datetime.now()
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if now >= target:
        target += timedelta(days=1)
    await asyncio.sleep((target - now).total_seconds())


async def daily_XP_notification():
    while True:
        await wait_until_target_time(0, 32)
        await send_notification("notify_XP")
        await asyncio.sleep(60)


async def main_scheduler():
    await asyncio.gather(repeatable_notifications(), daily_XP_notification())


if __name__ == "__main__":
    try:
        asyncio.run(main_scheduler())
    except KeyboardInterrupt:
        log.info("Планировщик RabbitMQ остановлен вручную.")
