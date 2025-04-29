# src/notifications/worker.py

import asyncio
from src.tasks.scheduler import start_scheduler
from src.config import log


async def main_worker():
    log.info("Запуск планировщика уведомлений...")
    start_scheduler()

    # Бесконечная работа
    while True:
        await asyncio.sleep(3600)
