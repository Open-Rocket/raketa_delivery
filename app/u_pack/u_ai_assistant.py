import os
import re
import httpx
import json

from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv("./info/.env")
proxy = os.getenv("PROXY")
apy_key = os.getenv("OPENAI_API")
assistant_id = os.getenv("AI_ASSISTANT_ID")
# user_threads = {}

client = AsyncOpenAI(
    api_key=apy_key,
    http_client=httpx.AsyncClient(
        proxies=proxy, transport=httpx.AsyncHTTPTransport(local_address="0.0.0.0")
    ),
)


# Протестировать на ожидание ответа
async def get_gpt_text(req, model="gpt-4o-mini"):
    completion = await client.chat.completions.create(
        messages=[{"role": "user", "content": req}], model=model
    )
    return completion.choices[0].message.content


async def assistant_censure(req: str) -> str:
    censore_data = [
        "clear",
        "overprice",
        "inaudible",
        "no_item",
        "censure",
        "not_order",
        "intercity",
    ]
    instructions = {
        "censure": (
            f"Ты — ИИ ассистент в сервисе пешей доставки. Твоя задача — проверять заказы на цензуру и корректность. "
            f"Следуй данной иерархии:\n\n"
            f"1. **Статус заказа**:\n"
            f"- Если текст не является реалистичным заказом доставки, верни '{censore_data[5]}'.\n"
            f"- Если в тексте отсутствует предмет доставки, верни '{censore_data[3]}'.\n"
            f"- Если это межгородская доставка '{censore_data[6]}'.\n"
            f"2. **Содержание заказа**:\n"
            f"- Если текст содержит запрещённые товары (наркотики, оружие, и т. д.), верни '{censore_data[4]}'.\n"
            # f"- Если требуется перевозка животных верни '{censore_data[4]}'.\n"
            # f"- Если текст содержит табачные изделия, электронные сигареты или алкоголь, верни '{censore_data[1]}'.\n\n"
            f"3. **Корректность текста**:\n"
            f"- Если текст неразборчивый или бессмысленный, верни '{censore_data[2]}'.\n"
            f"- Если заказ корректен и не содержит запрещённых товаров, верни '{censore_data[0]}'.\n\n"
            f"Помни, возвращай только одно значение без комментариев. Заказ: {req}"
        )
    }

    try:
        thread = await client.beta.threads.create()
        run = await client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant_id,
            instructions=instructions["censure"],
        )

        if run.status == "completed":
            messages_page = await client.beta.threads.messages.list(thread_id=thread.id)
            async for message in messages_page:
                if message.content and isinstance(message.content, list):
                    for content_block in message.content:
                        if hasattr(content_block, "text") and hasattr(
                            content_block.text, "value"
                        ):
                            return content_block.text.value
            return "Нет ответа от ассистента."
        return f"Ошибка: статус {run.status}"
    except Exception as e:
        print(f"Ошибка при работе с ассистентом: {e}")
        return "Ошибка при взаимодействии с ассистентом."


async def parse_response(response: str) -> dict:
    try:
        # Поиск начала и конца JSON-строки в ответе
        json_start = response.find("{")
        json_end = response.rfind("}") + 1
        clean_response = response[json_start:json_end]

        # Пытаемся преобразовать строку ответа в JSON-объект
        structured_data = json.loads(clean_response)
    except json.JSONDecodeError as e:
        # Обработка ошибки разбора JSON
        structured_data = {}
        print(f"Ошибка при разборе JSON ответа от модели: {e}")

    return structured_data


async def process_order_text(order_text: str) -> dict | str | None:
    # Проверяем текст заказа на цензуру
    response_assist = await assistant_censure(order_text)

    # Если заказ не прошел проверку, возвращаем None
    if response_assist in ("censure", "zero"):
        return response_assist

    # Если заказ прошел проверку, формируем JSON с извлеченными данными
    prompt = (
        f"Пожалуйста, извлеките и структурируйте следующую информацию "
        f"о заказе в формате JSON без дополнительных комментариев и текстов, "
        f"если о чем то нет информации то обязательно ничего не заполняй,\n"
        f"если нужно возвращаться из определенной точки в одну из предыдущих, "
        f"то узазывай точку возврата, полным его адресом (как в тексте), как следующую. "
        f"Обрати внимание на тот факт если пользователь просит вернуться обратно, то есть ABA - маршрут, "
        f"но ты заполняй как ABC\n"
        f"Заказ: \n{order_text}\n\n"
        f"Строго в формате JSON:\n"
        f"{{\n"
        f'  "City": ,\n'
        f'  "Starting point A": "Первый пункт доставки",\n'
        f'  "Destination point B": "Второй пункт доставки",\n'
        f'  "Destination point C": "Третий пункт доставки",\n'
        f'  "Destination point D": "Четвертый пункт доставки",\n'
        f'  "Destination point E": "Пятый пункт доставки",\n'
        f'  "Delivery object": "Объект доставки",\n'
        f'  "Description": "Опиши грамотно и полностью заказ"\n'
        f"}}"
    )

    response = await get_gpt_text(prompt)
    # print(f"JSON={response}")
    structured_data = await parse_response(response)
    # print(f"structured_data={response}")

    return structured_data


async def get_parsed_addresses(order_text, city=None):
    if not city:
        prompt = (
            f"Пожалуйста, извлеки из этого текста все адреса в следующем формате:\n"
            f"Город (обязательно),Тип объекта: улица, поселок, деревня, село, аэропорт, вокзал, станция, станция метро и т.д., "
            f"Название объекта, номер улицы или дома, город или населенный пункт).\n"
            f"addresses: [(Передай в этот список кортеж из адресов по указанному формату)]\n"
            f"text: {order_text} - извлеки отсюда только адреса."
            f"Если не указывается второй город то значит оба адреса из одного города!"
        )
    else:
        prompt = (
            f"Пожалуйста, извлеки из этого текста все адреса в следующем формате:\n"
            f"Город (обязательно),Тип объекта: улица, поселок, деревня, село, аэропорт, вокзал, станция, станция метро и т.д., "
            f"Название объекта, номер улицы или дома, город или населенный пункт).\n"
            f"addresses: [(Передай в этот список кортеж из адресов по указанному формату)]\n"
            f"text: {city}\n{order_text} - извлеки отсюда только адреса."
            f"Если не указывается второй город то значит оба адреса из одного города!"
        )

    response = await get_gpt_text(prompt)
    # print(response)

    # Регулярное выражение для поиска адресов по указанному формату
    address_pattern = re.compile(r"\((.*?)\)")
    # print(address_pattern)
    matches = address_pattern.findall(response)
    # print(matches)

    addresses = []
    for match in matches:
        if "," in match:
            addresses.append(match.strip())

    # print(addresses)
    return addresses
