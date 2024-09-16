import os
import re
import httpx
import json

from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()
proxy = os.getenv("PROXY")
apy_key = os.getenv("OPENAI_API")

client = AsyncOpenAI(api_key=apy_key,
                     http_client=httpx.AsyncClient(proxies=proxy,
                                                   transport=httpx.AsyncHTTPTransport(local_address="0.0.0.0")))


async def parse_response(response: str) -> dict:
    try:
        # Пытаемся преобразовать строку ответа в JSON-объект
        structured_data = json.loads(response)
    except json.JSONDecodeError:
        # Если ошибка, возвращаем пустой словарь или обработку ошибки
        structured_data = {}
        print("Ошибка при разборе JSON ответа от модели.")

    return structured_data


async def get_gpt_text(req, model="gpt-3.5-turbo"):
    completion = await client.chat.completions.create(
        messages=[{"role": "user", "content": req}],
        model=model
    )
    return completion.choices[0].message.content


# async def process_order_text(order_text=None, distance=None, duration=None, price=None, sender_info=None):
#     sender_name, sender_phone = sender_info
#     prompt = (
#         f"Пожалуйста, извлеките и структурируйте следующую информацию о заказе :{order_text}\n"
#         f"(cам Текст в заказ не отправлять), (не дописывай от себя пункты, структура заказа строгая):\n"
#         f"Пункт A: г.[Cyty],[Starting point]\n"
#         f"Пункт B: г.[Cyty],[Destination point]\n"
#         f"Пункт C: г.[Cyty],[Destination point] - Отображать если есть\n\n"
#         f"Пункт D: г.[Cyty],[Destination point] - Отображать если есть\n\n"
#         f"Оплатит: [отправитель/получатель/Нет информации]\n"
#         f"Предмет доставки: [Delivery object]\n\n"
#         f"Имя отправителя: [{sender_name}]\n"
#         f"Номер отправителя: [{sender_phone}]\n"
#         f"Имя получателя: [Receiver name]\n"
#         f"Номер получателя: [Receiver phone]\n\n"
#         f"Дополнительные сведения о заказе: [Order details]\n\n"
#         f"Комментарий курьеру: [Comments]\n\n"
#         f"Расстояние: [{distance} км]\n"
#         f"Время: [{duration}]\n\n"
#         f"Оплата: [{int(price)}₽]\n")
#     response = await get_gpt_text(prompt)
#     return response

async def process_order_text(order_text: str) -> dict:
    # Формируем запрос для модели ассистента
    prompt = (
        f"Пожалуйста, извлеките и структурируйте (только формате JSON!!!) следующую информацию о заказе "
        f"(Текст самого заказа не отправлять):\n\n"
        f"Заказ{order_text}"
        f"{{\n"
        f"  'City': 'Город',\n"
        f"  'Starting point A': Первый пункт доставки,\n"
        f"  'Destination point B': Второй пункт доставки,\n"
        f"  'Delivery object': 'Объект доставки',\n"
        f"  'Receiver name': 'Имя получателя (если указывается)',\n"
        f"  'Receiver phone': 'Номер получателя (если указывается)',\n"
        f"  'Comments': 'Комментарии',\n"
        f"}}"
    )

    # Отправляем запрос в ассистенту
    response = await get_gpt_text(prompt)

    # Предполагается, что модель вернет JSON
    structured_data = await parse_response(response)
    return structured_data


async def get_parsed_addresses(order_text):
    prompt = (f"Пожалуйста, извлеки из этого текста все адреса в следующем формате:\n"
              f"Город,Тип объекта: улица, поселок, деревня, село, аэропорт, вокзал, станция, станция метро и т.д., "
              f"Название объекта, номер улицы или дома, город или населенный пункт).\n"
              f"addresses: [(Передай в этот список кортеж из адресов по указанному формату)]\n"
              f"text: {order_text} - извлеки отсюда только адреса")

    response = await get_gpt_text(prompt)

    # Регулярное выражение для поиска адресов по указанному формату
    address_pattern = re.compile(r'\((.*?)\)')
    matches = address_pattern.findall(response)

    addresses = []
    for match in matches:
        if ',' in match:
            addresses.append(match.strip())

    return addresses

# async def get_city(order_text):
#     prompt = (f"Пожалуйста извлеки из этого текста только город заказа:\n"
#               f"text: {order_text} - верни только название города например 'Москва'")
#     response = await get_gpt_text(prompt)
#
#     if response:
#         # Попробуем извлечь название города
#         city = response.strip()  # Убираем лишние пробелы и символы переноса строк
#         return city.lower()
#     else:
#         return None
