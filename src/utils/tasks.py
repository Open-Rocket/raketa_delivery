import asyncio
from datetime import timedelta
from src.config import courier_bot, log, Time
from src.services.db_requests import courier_data, admin_data, order_data
from src.utils import kb
from src.confredis import rediska


async def new_orders_notification():
    all_couriers_tg_ids = await courier_data.get_all_couriers_tg_ids()
    reply_kb = await kb.get_task_kb("go_work")

    for courier_tg_id in all_couriers_tg_ids:
        count_orders, total_price_rub = (
            await courier_data.get_count_and_sum_orders_in_my_city(tg_id=courier_tg_id)
        )
        notify_status = await courier_data.get_courier_notify_status(
            tg_id=courier_tg_id
        )

        if count_orders > 0 and notify_status:
            text = (
                f"В вашем городе сейчас {count_orders} заказов на {total_price_rub}₽."
            )
            await courier_bot.send_message(
                chat_id=courier_tg_id,
                text=text,
                reply_markup=reply_kb,
                parse_mode="HTML",
            )


async def XP_points_notification():

    now = await Time.get_moscow_time()
    today = now.date()
    yesterday = today - timedelta(days=1)

    last_speed_bonus_award_date = await rediska.get_last_speed_bonus_award_date()
    last_distance_bonus_award_date = await rediska.get_last_distance_bonus_award_date()

    if now.hour == 6 and 9 < now.minute < 15 and last_speed_bonus_award_date != today:

        (
            order_id,
            courier_tg_id,
            courier_name,
            courier_username,
            courier_phone,
            city,
            speed,
            distance,
            execution_time_seconds,
        ) = await order_data.get_fastest_order_by_date(today)

        if courier_tg_id:
            try:
                speed_XP = await admin_data.get_speed_XP()
                calculate_speed_XP = round((speed * speed_XP), 2)
                _ = await courier_data.update_courier_XP(
                    tg_id=courier_tg_id,
                    new_XP=calculate_speed_XP,
                )
                text = (
                    f"🎉 Вы вчера поставили рекорд по скорости!\n"
                    f"Скорость: {speed} км/ч\nВы получаете бонус <b>{calculate_speed_XP}</b> очков опыта XP!\n\n"
                    f"Спасибо за вашу работу 🚀"
                )
                await courier_bot.send_message(
                    chat_id=courier_tg_id,
                    text=text,
                    parse_mode="HTML",
                )

                await rediska.set_last_speed_bonus_award_date(award_date=today)

            except Exception as e:
                log.error(f"Exception speed bonus day {e}")
            last_speed_bonus_award_date = today

    if (
        now.hour == 6
        and 9 < now.minute < 15
        and last_distance_bonus_award_date != today
    ):
        courier_id, distance = (
            await admin_data.get_courier_info_by_max_date_distance_covered(date=today)
        )
        if courier_id:
            courier_tg_id = await courier_data.get_courier_tg_id(id=courier_id)
            if courier_tg_id:
                distance_XP = await admin_data.get_distance_XP()
                calculate_distance_XP = round((distance * distance_XP), 2)
                try:
                    _ = await courier_data.update_courier_XP(
                        tg_id=courier_tg_id,
                        new_XP=calculate_distance_XP,
                    )
                    text = (
                        f"🎉 Вы вчера прошли самую большую дистанцию!\n"
                        f"Дистанция: {distance} км\nВы получаете бонус <b>{calculate_distance_XP}</b> очков опыта XP!\n\n"
                        f"Спасибо за вашу работу 🚀"
                    )
                    await courier_bot.send_message(
                        chat_id=courier_tg_id,
                        text=text,
                        parse_mode="HTML",
                    )
                    await rediska.set_last_distance_bonus_award_date(award_date=today)
                except Exception as e:
                    log.error(f"Exception distance bonus day {e}")
                last_distance_bonus_award_date = today


# 🔁 Запуск двух независимых циклов


async def notification_loop():
    while True:
        try:
            interval = await admin_data.get_new_orders_notification_interval()
            await new_orders_notification()
            await asyncio.sleep(interval)
        except Exception as e:
            log.error(f"[notification_loop] Ошибка: {e}")
            await asyncio.sleep(30)


async def bonus_loop():
    while True:
        try:
            await XP_points_notification()
            await asyncio.sleep(60)  # Проверка каждую минуту
        except Exception as e:
            log.error(f"[bonus_loop] Ошибка: {e}")
            await asyncio.sleep(30)


async def send_notification_to_couriers():
    await asyncio.gather(
        notification_loop(),
        bonus_loop(),
    )


__all__ = ["send_notification_to_couriers"]
