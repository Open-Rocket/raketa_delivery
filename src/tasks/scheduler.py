# src/notifications/scheduler.py

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.tasks.notifications import (
    notify_couriers_about_orders,
    notify_customers_about_couriers,
    notify_couriers_about_XP_rewards,
)

scheduler = AsyncIOScheduler(timezone="Europe/Moscow")


async def start_scheduler():
    scheduler.add_job(notify_couriers_about_orders, "cron", hour=12, minute=5)
    scheduler.add_job(notify_couriers_about_orders, "cron", hour=20, minute=30)
    scheduler.add_job(notify_customers_about_couriers, "cron", hour=12, minute=5)
    scheduler.add_job(notify_customers_about_couriers, "cron", hour=20, minute=30)
    scheduler.add_job(notify_customers_about_couriers, "cron", hour=16, minute=5)
    scheduler.add_job(notify_couriers_about_XP_rewards, "cron", hour=00, minute=1)
    scheduler.start()
