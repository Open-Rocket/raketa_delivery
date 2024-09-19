import os
import re
import httpx
import json

from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()
proxy = os.getenv("PROXY")
apy_key = os.getenv("OPENAI_API")
assistant_id = os.getenv("AI_ASSISTANT_ID")
user_threads = {}

client = AsyncOpenAI(api_key=apy_key,
                     http_client=httpx.AsyncClient(proxies=proxy,
                                                   transport=httpx.AsyncHTTPTransport(local_address="0.0.0.0")))


async def get_gpt_text(req, model="gpt-4o-mini"):
    completion = await client.chat.completions.create(
        messages=[{"role": "user", "content": req}],
        model=model
    )
    return completion.choices[0].message.content


async def assistant_censure(req: str) -> str:
    try:
        # Создаем новый поток
        thread = await client.beta.threads.create()

        # Запускаем задание в потоке
        run = await client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant_id,
            instructions=(
                f"Ты — ИИ ассистент в сервисе пешей доставки.\n"
                f"Твоя задача — фильтровать заказы на наличие неприемлемых или противозаконных товаров, "
                f"проверять корректность данных и возвращать один из следующих ответов:\n"
                f"1. 'clear' — если заказ соответствует всем требованиям и нет нарушений.\n"
                f"2. 'censure' — если в заказе есть противозаконные или неприемлемые товары.\n"
                f"3. 'zero' — если текст заказа непонятен, содержит бессмысленные символы или не может быть обработан.\n\n"
                f"**Важно**: есть категории товаров, которые **не подлежат цензуре**, и их **можно** доставлять:\n"
                f"— Лекарства\n"
                f"— Медикаменты\n\n"
                f"Лекарства и медикаменты **должны быть одобрены для доставки**. Их нельзя цензурировать или блокировать.\n"
                f"Если ты видишь, что заказ содержит такие товары, **не нужно** применять фильтрацию.\n"
                f"Если заказ законен и не содержит запрещенных товаров, верни 'clear'.\n"
                f"Если заказ непонятен или незаконен, верни 'censure'.\n\n"
                f"Важно избегать излишней строгости при оценке разрешенных товаров, таких как лекарства и медикаменты. "
                f"Убедись, что они пропущены.\n\n"
                f"Заказ для проверки:\n"
                f"{req}"
            )
        )

        # Проверяем статус задания
        if run.status == 'completed':
            # Получаем сообщения из потока
            messages_page = await client.beta.threads.messages.list(thread_id=thread.id)

            # Собираем сообщения
            messages = []
            async for message in messages_page:
                messages.append(message)

            # Проверяем, есть ли сообщения и извлекаем текст
            if messages:
                message = messages[0]
                # print(f"Message structure: {message}")  # Для отладки структуры
                if message.content and isinstance(message.content, list) and len(message.content) > 0:
                    text_block = message.content[0]
                    if hasattr(text_block, 'text') and hasattr(text_block.text, 'value'):
                        return text_block.text.value
                return "Не удалось извлечь текст сообщения."
            else:
                return "Нет ответа от ассистента."
        else:
            return f"Ошибка при получении ответа от ассистента. Статус: {run.status}"
    except Exception as e:
        print(f"Ошибка при взаимодействии с ассистентом: {e}")


async def parse_response(response: str) -> dict:
    try:
        # Пытаемся преобразовать строку ответа в JSON-объект
        structured_data = json.loads(response)
    except json.JSONDecodeError:
        # Если ошибка, возвращаем пустой словарь или обработку ошибки
        structured_data = {}
        print("Ошибка при разборе JSON ответа от модели.")

    return structured_data


async def process_order_text(order_text: str) -> dict | str | None:
    # Формируем запрос для модели ассистента
    prompt = (
        f"Пожалуйста, извлеките и структурируйте следующую информацию о заказе в формате "
        f"JSON (без текста самого заказа):\n\n"
        f"Заказ: {order_text}\n"
        f"{{\n"
        f'  "City": "Город",\n'
        f'  "Starting point A": "Первый пункт доставки",\n'
        f'  "Destination point B": "Второй пункт доставки",\n'
        f'  "Delivery object": "Объект доставки",\n'
        f'  "Receiver name": "Имя получателя (если указывается)",\n'
        f'  "Receiver phone": "Номер получателя (если указывается)",\n'
        f'  "Comments": "Комментарии"\n'
        f"}}"
    )

    response_assist = await assistant_censure(order_text)
    # Отправляем запрос в ассистент
    if response_assist in ('censure', 'zero'):
        return None
    elif response_assist == "clear":
        response = await get_gpt_text(prompt)
        # Предполагается, что модель вернет JSON
        structured_data = await parse_response(response)
        return structured_data



async def get_parsed_addresses(order_text):
    prompt = (f"Пожалуйста, извлеки из этого текста все адреса в следующем формате:\n"
              f"Город (обязательно),Тип объекта: улица, поселок, деревня, село, аэропорт, вокзал, станция, станция метро и т.д., "
              f"Название объекта, номер улицы или дома, город или населенный пункт).\n"
              f"addresses: [(Передай в этот список кортеж из адресов по указанному формату)]\n"
              f"text: {order_text} - извлеки отсюда только адреса."
              f"Если не указывается второй город то значит оба адреса из одного города!")

    response = await get_gpt_text(prompt)

    # Регулярное выражение для поиска адресов по указанному формату
    address_pattern = re.compile(r'\((.*?)\)')
    matches = address_pattern.findall(response)

    addresses = []
    for match in matches:
        if ',' in match:
            addresses.append(match.strip())

    return addresses
