from datetime import timedelta
from collections import defaultdict
from src.config import courier_bot, customer_bot, log, Time
from src.services.db_requests import courier_data, admin_data, order_data, customer_data
from src.confredis import rediska
import asyncio


async def delete_message_after_delay(
    bot,
    chat_id: int,
    message_id: int,
    delay: int = 600,
):
    try:
        log.info(f"delete_message_id: {message_id}")
        await asyncio.sleep(delay)
        if message_id:
            await bot.delete_message(chat_id=chat_id, message_id=message_id)
            log.info(f"Удалено сообщение {message_id} у {chat_id}")
    except Exception as e:
        log.warning(f"Не удалось удалить сообщение {message_id} у {chat_id}: {e}")


async def new_orders_notification():
    all_couriers_tg_ids = (
        await courier_data.get_all_couriers_tg_ids_notify_status_true()
    )
    city_couriers_map = defaultdict(list)

    for tg_id in all_couriers_tg_ids:
        city = await courier_data.get_courier_city(tg_id=tg_id)
        if city:
            city_couriers_map[city].append(tg_id)

    for city, tg_ids in city_couriers_map.items():
        count_orders, total_price_rub = (
            await order_data.get_count_and_sum_orders_in_city(city)
        )
        if count_orders > 0:
            text = (
                f"В городе {city} сейчас заказов: <b>{count_orders}</b>\n"
                f"Сумма заказов: <b>{total_price_rub}₽</b>\n"
                f"Начать работу /run\n\n"
                f"<i>Отключить уведомления</i> /notify"
            )
            for tg_id in tg_ids:
                try:
                    msg = await courier_bot.send_message(
                        chat_id=tg_id,
                        text=text,
                        parse_mode="HTML",
                    )
                    asyncio.create_task(
                        delete_message_after_delay(
                            courier_bot,
                            tg_id,
                            msg.message_id,
                            delay=14400,
                        )
                    )
                except Exception as e:
                    log.error(f"Ошибка при отправке уведомления курьеру {tg_id}: {e}")


async def city_couriers_notification():
    all_customers_tg_ids = (
        await customer_data.get_all_customers_tg_ids_notify_status_true()
    )
    city_customers_map = defaultdict(list)

    for tg_id in all_customers_tg_ids:
        customer_city = await customer_data.get_customer_city(tg_id=tg_id)
        if customer_city:
            city_customers_map[customer_city].append(tg_id)

    for city, tg_ids in city_customers_map.items():
        couriers_city_len = len(await courier_data.get_couriers_in_city(city=city))
        if couriers_city_len > 0:
            text = (
                f"Курьеров в городе {city} сейчас: <b>{couriers_city_len}</b>\n"
                f"Можете сделать заказ /order\n\n"
                f"<i>Отключить уведомления</i> /notify"
            )

            for tg_id in tg_ids:
                try:
                    msg = await customer_bot.send_message(
                        chat_id=tg_id,
                        text=text,
                        parse_mode="HTML",
                    )

                    asyncio.create_task(
                        delete_message_after_delay(
                            customer_bot,
                            tg_id,
                            msg.message_id,
                            delay=14400,
                        )
                    )
                except Exception as e:
                    log.error(f"Ошибка при отправке уведомления клиенту {tg_id}: {e}")


async def XP_points_notification():
    now = await Time.get_moscow_time()
    today = now.date()

    last_speed_bonus_award_date = await rediska.get_last_speed_bonus_award_date()
    last_distance_bonus_award_date = await rediska.get_last_distance_bonus_award_date()

    if last_speed_bonus_award_date != today:
        data = await order_data.get_fastest_order_by_date(today)
        if data:
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
            ) = data

            if courier_tg_id:
                try:
                    speed_XP = await admin_data.get_speed_XP()
                    calculate_speed_XP = round((speed * speed_XP), 2)
                    await courier_data.update_courier_XP(
                        tg_id=courier_tg_id, new_XP=calculate_speed_XP
                    )

                    text = (
                        f"🎉 Вы вчера поставили рекорд по скорости!\n"
                        f"Скорость: <b>{speed} км/ч</b>\nВы получаете бонус <b>{calculate_speed_XP}</b> очков опыта XP!\n\n"
                        f"Спасибо за вашу работу 🚀"
                    )
                    await courier_bot.send_message(
                        chat_id=courier_tg_id, text=text, parse_mode="HTML"
                    )

                    await rediska.set_last_speed_bonus_award_date(award_date=today)
                except Exception as e:
                    log.error(f"Exception speed bonus day {e}")

    # Обработка награды за дистанцию
    if last_distance_bonus_award_date != today:
        courier_id, distance = (
            await admin_data.get_courier_info_by_max_date_distance_covered(date=today)
        )
        if courier_id:
            courier_tg_id = await courier_data.get_courier_tg_id(id=courier_id)
            if courier_tg_id:
                try:
                    distance_XP = await admin_data.get_distance_XP()
                    calculate_distance_XP = round((distance * distance_XP), 2)
                    await courier_data.update_courier_XP(
                        tg_id=courier_tg_id, new_XP=calculate_distance_XP
                    )
                    text = (
                        f"🎉 Вы вчера прошли самую большую дистанцию!\n"
                        f"Дистанция: <b>{distance} км</b>\nВы получаете бонус <b>{calculate_distance_XP}</b> очков опыта XP!\n\n"
                        f"Спасибо за вашу работу 🚀"
                    )
                    await courier_bot.send_message(
                        chat_id=courier_tg_id, text=text, parse_mode="HTML"
                    )
                    await rediska.set_last_distance_bonus_award_date(award_date=today)
                except Exception as e:
                    log.error(f"Exception distance bonus day {e}")
