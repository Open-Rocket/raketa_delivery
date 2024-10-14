import asyncio
from app.u_pack.u_ai_assistant import process_order_text

templates_orders = {
    "order_1": ("Забрать заказ нужно в Москве, на проспекте Вернадского, дом 76, корпус 2. "
                "Отправить на улицу Академика Анохина, дом 20. В коробке находится одежда. "
                "Получателем будет Иван, его номер — 89991234567. "
                "Очень важно, чтобы курьер доставил заказ до 18:00  Спасибо!"),
    "order_2": "pass"
}


async def get_ai_json(text: str):
    ai_json = await process_order_text(text)
    print(ai_json)
    return ai_json


asyncio.run(get_ai_json(templates_orders["order_1"]))
