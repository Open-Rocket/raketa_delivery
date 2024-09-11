import os
import re
import httpx
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()
proxy = os.getenv("PROXY")
apy_key = os.getenv("OPENAI_API")

client = AsyncOpenAI(api_key=apy_key,
                     http_client=httpx.AsyncClient(proxies=proxy,
                                                   transport=httpx.AsyncHTTPTransport(local_address="0.0.0.0")))


async def get_gpt_text(req, model="gpt-3.5-turbo"):
    completion = await client.chat.completions.create(
        messages=[{"role": "user", "content": req}],
        model=model
    )
    return completion.choices[0].message.content


async def process_order_text(order_text=None, distance=None, duration=None, price=None):
    prompt = (
        f"Пожалуйста, извлеките и структурируйте следующую информацию о заказе :{order_text}\n"
        f"(cам Текст в заказ не отправлять), (не дописывай от себя пункты, структура заказа строгая):\n"
        f"Пункт A: г.[Cyty],[Starting point]\n"
        f"Пункт B: г.[Cyty],[Destination point]\n"
        f"Пункт C: г.[Cyty],[Destination point] - Отображать если есть\n\n"
        f"Дополнительные сведения о заказе: [Order details]\n\n"
        f"Оплатит получатель: [Да/Нет/Нет информации]\n"
        f"Предмет доставки: [Delivery object]\n\n"
        f"Имя отправителя: [Sender name]\n"
        f"Номер отправителя: [Sender phone]\n"
        f"Имя получателя: [Receiver name]\n"
        f"Номер получателя: [Receiver phone]\n\n"
        f"Комментарий курьеру: [Comments]\n\n"
        f"Расстояние: [{distance} км]\n"
        f"Время: [{duration}]\n\n"
        f"Оплата: [{int(price)}₽]\n")
    response = await get_gpt_text(prompt)
    return response


async def get_parsed_addresses(order_text):
    prompt = (f"Пожалуйста, извлеки из этого текста все возможные адреса в следующем формате:\n"
              f"(Тип объекта: улица, поселок, деревня, село, аэропорт, вокзал, станция и т.д., "
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


async def get_city(order_text):
    prompt = (f"Пожалуйста извлеки из этого текста только город заказа:\n"
              f"text: {order_text} - верни только название города например 'Москва'")
    response = await get_gpt_text(prompt)

    if response:
        # Попробуем извлечь название города
        city = response.strip()  # Убираем лишние пробелы и символы переноса строк
        return city.lower()
    else:
        return None
