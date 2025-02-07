import asyncio
import logging
from app.u_pack.u_ai_assistant import AssistantAi
import time
from datetime import datetime
import pytz
from app.common.coords_and_price import (
    get_coordinates,
    get_price,
    calculate_total_distance,
    get_rout,
)

from app.database.requests import user_data, order_data


assistant = AssistantAi()

logging.basicConfig(
    level=logging.INFO,  # Уровень логирования, можно использовать DEBUG, INFO, WARNING, ERROR, CRITICAL
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Формат сообщения
)
logger = logging.getLogger(__name__)  # Создаем логгер для текущего модуля


messages = [
    "Забрать заказ нужно в Москве, на проспекте Вернадского, дом 76, корпус 2. Отправить на улицу Академика Анохина, дом 20. В коробке находится одежда. Получателем будет Иван, его номер — 89991234567. Очень важно, чтобы курьер доставил заказ до 18:00  Спасибо!",
    "Привет! Заказ в Москве, забирать нужно с улицы Мосфильмовская, дом 53. Доставить на улицу Петровка, дом 19. Там лекарства, это важно, потому что их ждут. Забрать можно с 14:00. Получатель — Ольга, номер 89978987865, свяжитесь с ней, если возникнут вопросы. Спасибо!",
    "Забрать заказ нужно в Москве, на улице Тверская, дом 15. Затем заехать на Ленинградский проспект, дом 44 для забора дополнительного груза. После этого отправить всё на Кутузовский проспект, дом 12. В сумке находятся документы. Получатель — Сергей, его номер — 89161112233. Пожалуйста, доставьте до 17:30. Спасибо!",
    "Привет! Заберите заказ с улицы Кутузовский проспект, дом 12 доставить нужно книжки. После этого, пожалуйста, заедьте на улицу Строителей, дом 8, там находятся игрушки. Затем на улицу Льва Толстого, дом 14, где находятся документы. Далее, заедьте на улицу Мира, дом 22, в которой нужно забрать одежду. В завершение, пожалуйста, доставьте на улицу Петра Романова 11. Спасибо большое!",
    "Забрать заказ нужно на Невском проспекте, дом 28, корпус 1. Отправить на улицу Ленина, дом 15. В коробке находится техника. Получателем будет Сергей, его номер — 89261234567. Очень важно, чтобы курьер доставил заказ до 20:00. Спасибо!",
    "Нужно доставить шаурму на улицу Гаппо Баева 1 с проспекта Коста, дом 72, корпус 2. Получателем будет Юрий, его номер — 89261234567. Город Владикавказ",
]


async def get_order_form(city, addresses, description):

    customer_name = "Ruslan"
    customer_phone = 89993501515
    moscow_time = datetime.now(pytz.timezone("Europe/Moscow")).replace(
        tzinfo=None, microsecond=0
    )

    if addresses:
        coordinates = []
        address_links = []
        formatted_addresses = []
        order_addresses_data = []

        for address in addresses:
            coords = await get_coordinates(address)
            if coords:
                coordinates.append(coords)
                maps_url = f"https://maps.yandex.ru/?text={address.replace(' ', '+')}"
                address_links.append(maps_url)
                formatted_addresses.append(f"<a href='{maps_url}'>{address}</a>")

                order_addresses_data.append([coords, address])

        logger.info(f"Order address data: {order_addresses_data}")

        if len(coordinates) >= 2:
            yandex_maps_url = await get_rout(coordinates[0], coordinates[1:])
            distance = await calculate_total_distance(coordinates)
            distance = round(distance, 2)
            price = await get_price(distance, moscow_time)

            addresses_text = "\n".join(
                [
                    f"⦿ <b>Адрес {i+1}:</b> {formatted_addresses[i]}"
                    for i in range(len(formatted_addresses))
                ]
            )

            # Сохранение данных в состоянии
            # await state.update_data(
            #     city=city,
            #     starting_point_a=starting_point_a,
            #     a_latitude=float(pickup_coords[0]),
            #     a_longitude=float(pickup_coords[1]),
            #     a_coordinates=pickup_coords,
            #     a_url=pickup_point,
            #     destination_point_b=destination_point_b,
            #     b_latitude=float(delivery_coords[0]),
            #     b_longitude=float(delivery_coords[1]),
            #     b_coordinates=delivery_coords,
            #     b_url=delivery_point,
            #     delivery_object=delivery_object,
            #     customer_name=customer_name,
            #     customer_phone=customer_phone,
            #     description=description,
            #     distance_km=distance,
            #     duration_min=duration,
            #     price_rub=price,
            #     order_text=recognized_text,
            #     order_time=moscow_time,
            #     yandex_maps_url=yandex_maps_url,
            #     pickup_point=pickup_point,
            #     delivery_point=delivery_point,
            # )

            order_forma = (
                f"<b>Ваш заказ</b> ✍︎\n"
                f"---------------------------------------------\n\n"
                f"<b>Город:</b> {city}\n\n"
                f"<b>Заказчик:</b> {customer_name}\n"
                f"<b>Телефон:</b> {customer_phone}\n\n"
                f"{addresses_text}\n\n"
                f"<b>Расстояние:</b> {distance} км\n"
                f"<b>Стоимость доставки:</b> {price}₽\n\n"
                f"<b>Описание:</b> {description}\n\n"
                f"---------------------------------------------\n"
                f"• Проверьте ваш заказ и если все верно, то разместите.\n"
                f"• Курьер может связаться с вами для уточнения деталей!\n"
                f"• Оплачивайте курьеру наличными или переводом.\n\n"
                f"⦿⌁⦿ <a href='{yandex_maps_url}'>Маршрут доставки</a>\n\n"
            )

            return order_forma

        return "-"


async def get_assistant_response():
    start_time = time.perf_counter()
    city, addresses, description = await assistant.process_order(
        messages[0], city="Москва"
    )
    end_time = time.perf_counter()
    execution_time = end_time - start_time

    form = await get_order_form(city, addresses, description)

    # logger.info(f"Response: {assistant_response}")
    logger.info(f"\n-----\nTime taken: {execution_time:.4f} seconds\n-----")
    logger.info(f"\n-----\nOrder form: \n{form}\n-----")


asyncio.run(get_assistant_response())

# source .venv/bin/activate
# python -m app.u_pack.testing_assistant
