import asyncio
from src.config import courier_bot
from src.services.db_requests import courier_data, admin_data
from src.utils import kb
from src.config import log


async def new_orders_notification():

    log.info("new_orders_notification")

    all_couriers_tg_ids = await courier_data.get_all_couriers_tg_ids()
    reply_kb = await kb.get_task_kb("go_work")

    for courier_tg_id in all_couriers_tg_ids:
        count_orders, total_price_rub = (
            await courier_data.get_count_and_sum_orders_in_my_city(tg_id=courier_tg_id)
        )

        notify_status = await courier_data.get_courier_notify_status(
            tg_id=courier_tg_id
        )

        text = f"В вашем городе сейчас {count_orders} заказов на {total_price_rub}₽.\n"

        if count_orders > 0 and notify_status:
            await courier_bot.send_message(
                chat_id=courier_tg_id,
                text=text,
                reply_markup=reply_kb,
                parse_mode="HTML",
            )

    interval = await admin_data.get_new_orders_notification_interval()

    log.info(f"interval: {interval}")

    await asyncio.sleep(interval)


async def send_notification_to_couriers():

    while True:
        try:
            await new_orders_notification()

        except Exception as e:
            print(f"[ERROR] Ошибка в уведомлениях: {e}")
            await asyncio.sleep(10)


__all__ = ["send_notification_to_couriers"]
