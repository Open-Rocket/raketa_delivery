from src.config import moscow_time, log
from src.services import assistant
from src.services import formatter

import time
import asyncio


messages = [
    "Забрать заказ нужно в Москве, на проспекте Вернадского, дом 76, корпус 2. Отправить на улицу Академика Анохина, дом 20. В коробке находится одежда. Получателем будет Иван, его номер — 89991234567. Очень важно, чтобы курьер доставил заказ до 18:00  Спасибо!",
    "Привет! Заказ в Москве, забирать нужно с улицы Мосфильмовская, дом 53. Доставить на улицу Петровка, дом 19. Там лекарства, это важно, потому что их ждут. Забрать можно с 14:00. Получатель — Ольга, номер 89978987865, свяжитесь с ней, если возникнут вопросы. Спасибо!",
    "Забрать заказ нужно в Москве, на улице Тверская, дом 15. Затем заехать на Ленинградский проспект, дом 44 для забора дополнительного груза. После этого отправить всё на Кутузовский проспект, дом 12. В сумке находятся документы. Получатель — Сергей, его номер — 89161112233. Пожалуйста, доставьте до 17:30. Спасибо!",
    "Привет! Заберите заказ с улицы Кутузовский проспект, дом 12 доставить нужно книжки. После этого, пожалуйста, заедьте на улицу Строителей, дом 8, там находятся игрушки. Затем на улицу Льва Толстого, дом 14, где находятся документы. Далее, заедьте на улицу Мира, дом 22, в которой нужно забрать одежду. В завершение, пожалуйста, доставьте на улицу Петра Романова 11. Спасибо большое!",
    "Забрать заказ нужно на Невском проспекте, дом 28, корпус 1. Отправить на улицу Ленина, дом 15. В коробке находится техника. Получателем будет Сергей, его номер — 89261234567. Очень важно, чтобы курьер доставил заказ до 20:00. Спасибо!",
    "Нужно доставить шаурму на улицу Гаппо Баева 1 с проспекта Коста, дом 72, корпус 2. Получателем будет Юрий, его номер — 89261234567. Город Владикавказ",
]


async def get_assistant_response():

    user_name = "Ruslan"
    user_phone = "89993501515"

    start_time = time.perf_counter()

    try:
        city, addresses, delivery_object, description = await assistant.process_order(
            messages[1], city="Москва"
        )

        log.info("request was successfully done")
    except Exception as e:
        log.error(f"exception: {e}")

    prepare_dict = await formatter._prepare_data(
        moscow_time,
        city,
        user_name,
        user_phone,
        addresses,
        delivery_object,
        description,
    )

    form = await formatter.format_order_form(prepare_dict)

    end_time = time.perf_counter()
    execution_time = end_time - start_time

    log.info(f"Order form:\n\n{form}\n")
    log.info(f"Time taken: {execution_time:.4f} seconds\n")


asyncio.run(get_assistant_response())

# source .venv/bin/activate
# python -m src_test.testing_assistant
