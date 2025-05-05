# src/notifications/notifications.py

import asyncio
from collections import defaultdict
from src.config import Time, courier_bot, customer_bot, log
from src.services.db_requests import courier_data, customer_data, order_data, admin_data
from src.confredis import rediska


async def delete_message_after_delay(
    bot, chat_id: int, message_id: int, delay: int = 600
):
    try:
        await asyncio.sleep(delay)
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
        log.info(f"Удалено сообщение {message_id} у пользователя {chat_id}")
    except Exception as e:
        log.warning(f"Не удалось удалить сообщение {message_id} у {chat_id}: {e}")


async def notify_couriers_about_orders():
    couriers = await courier_data.get_all_couriers_tg_ids_notify_status_true()
    city_couriers = defaultdict(list)

    for tg_id in couriers:
        city = await courier_data.get_courier_city(tg_id)
        if city:
            city_couriers[city].append(tg_id)

    for city, tg_ids in city_couriers.items():
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
                        chat_id=tg_id, text=text, parse_mode="HTML"
                    )
                    asyncio.create_task(
                        delete_message_after_delay(
                            courier_bot, tg_id, msg.message_id, delay=14400
                        )
                    )
                except Exception as e:
                    log.error(f"Ошибка при отправке уведомления курьеру {tg_id}: {e}")


async def notify_customers_about_couriers():
    customers = await customer_data.get_all_customers_tg_ids_notify_status_true()
    city_customers = defaultdict(list)

    for tg_id in customers:
        city = await customer_data.get_customer_city(tg_id)
        if city:
            city_customers[city].append(tg_id)

    for city, tg_ids in city_customers.items():
        couriers_count = len(await courier_data.get_couriers_in_city(city))

        if couriers_count > 0:
            text = (
                f"Курьеров в городе {city} сейчас: <b>{couriers_count}</b>\n"
                f"Можете сделать заказ /order\n\n"
                f"<i>Отключить уведомления</i> /notify"
            )
            for tg_id in tg_ids:
                try:
                    msg = await customer_bot.send_message(
                        chat_id=tg_id, text=text, parse_mode="HTML"
                    )
                    asyncio.create_task(
                        delete_message_after_delay(
                            customer_bot, tg_id, msg.message_id, delay=14400
                        )
                    )
                except Exception as e:
                    log.error(f"Ошибка при отправке уведомления клиенту {tg_id}: {e}")


async def notify_couriers_about_XP_rewards():
    now = await Time.get_moscow_time()
    today = now.date()

    last_speed_award = await rediska.get_last_speed_bonus_award_date()
    last_distance_award = await rediska.get_last_distance_bonus_award_date()

    # Награда за скорость
    if last_speed_award != today:
        data = await order_data.get_fastest_order_by_date(today)
        if data:
            (_, courier_tg_id, _, _, _, _, speed, _, _) = data

            if courier_tg_id:
                try:
                    speed_XP_value = await admin_data.get_speed_XP()
                    awarded_XP = round(speed * speed_XP_value, 2)

                    await courier_data.update_courier_XP(courier_tg_id, awarded_XP)

                    text = (
                        f"🎉 Вы вчера поставили рекорд по скорости!\n"
                        f"Скорость: <b>{speed} км/ч</b>\n"
                        f"Вы получаете <b>{awarded_XP}</b> очков XP!\n\n"
                        f"Спасибо за вашу работу 🚀"
                    )
                    await courier_bot.send_message(
                        chat_id=courier_tg_id, text=text, parse_mode="HTML"
                    )
                    await rediska.set_last_speed_bonus_award_date(today)
                except Exception as e:
                    log.error(f"Ошибка начисления награды за скорость: {e}")

    # Награда за дистанцию
    if last_distance_award != today:
        courier_id, distance = (
            await admin_data.get_courier_info_by_max_date_distance_covered(today)
        )
        if courier_id:
            courier_tg_id = await courier_data.get_courier_tg_id(courier_id)
            if courier_tg_id:
                try:
                    distance_XP_value = await admin_data.get_distance_XP()
                    awarded_XP = round(distance * distance_XP_value, 2)

                    await courier_data.update_courier_XP(courier_tg_id, awarded_XP)

                    text = (
                        f"🎉 Вы вчера прошли самую большую дистанцию!\n"
                        f"Дистанция: <b>{distance} км</b>\n"
                        f"Вы получаете <b>{awarded_XP}</b> очков XP!\n\n"
                        f"Спасибо за вашу работу 🚀"
                    )
                    await courier_bot.send_message(
                        chat_id=courier_tg_id, text=text, parse_mode="HTML"
                    )
                    await rediska.set_last_distance_bonus_award_date(today)
                except Exception as e:
                    log.error(f"Ошибка начисления награды за дистанцию: {e}")
