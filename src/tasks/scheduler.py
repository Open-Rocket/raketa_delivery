# src/notifications/scheduler.py

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.tasks.notifications import (
    notify_couriers_about_orders,
    notify_customers_about_couriers,
    notify_couriers_about_XP_rewards,
)

scheduler = AsyncIOScheduler(timezone="Europe/Moscow")


def start_scheduler():
    scheduler.add_job(notify_couriers_about_orders, "interval", minutes=30)
    scheduler.add_job(notify_customers_about_couriers, "interval", minutes=30)
    scheduler.add_job(notify_couriers_about_XP_rewards, "cron", hour=0, minute=1)
    scheduler.start()
