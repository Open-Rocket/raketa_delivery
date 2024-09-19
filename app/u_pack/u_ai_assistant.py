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
    censore_data = ["clear", "tobacco_alcohol", "inaudible", "censure"]
    instructions = {
        "censure": (
            f"Ты — ИИ ассистент в сервисе пешей доставки.\n"
            f"Твоя задача — проверять заказы на предмет цензуры и подозрительных действий.\n"
            f"Четко следуй инструкциям, чтобы определить правильный статус заказа.\n\n"

            f"Пропускай заказы, содержащие следующие товары, но с пометкой о необходимости дополнительного анализа:\n"
            f"- Табачные изделия\n"
            f"- Электронные сигареты\n"
            f"- Алкоголь\n"
            f"Эти товары разрешены к заказу, однако они требуют более тщательной проверки для "
            f"выявления возможных нарушений или подозрительных действий.\n\n"

            f"Запрещённые товары включают:\n"
            f"- Наркотические вещества\n"
            f"- Оружие и боеприпасы\n"
            f"- Взрывчатые вещества\n"
            f"- Токсичные или опасные химические вещества\n"
            f"- Предметы, связанные с незаконной деятельностью\n"
            f"- Украденные товары\n"
            f"- Животные (если не оговорено иначе)\n"
            f"- Любые другие товары, запрещённые законом.\n\n"

            f"Анализируй текст заказа на подозрительность. Обрати внимание на следующее:\n"
            f"- Неправдоподобные или слишком нечеткие описания заказа\n"
            f"- Чрезмерно завуалированные или двусмысленные формулировки\n"
            f"- Упоминание действий, связанных с уклонением от закона\n"
            f"- Намёки на незаконные операции или скрытые действия.\n\n"

            f"Возвращай без лишних комментариев строго одно из следующих значений на основе анализа:\n"
            f"{censore_data[0]} — если заказ полностью чист и не содержит запрещенных товаров и подозрительности.\n"
            f"{censore_data[1]} — если заказ содержит табачные изделия, электронные сигареты, алкоголь."
            f"{censore_data[2]} — если текст заказа неразборчивый, неполный или не может быть обработан.\n\n"
            f"{censore_data[3]} — если заказ содержит запрещенные товары (наркотики, оружие и прочие), "
            f"или подозрительный текст, указывающий на незаконную деятельность.\n"
            f"Заказ: {req}"
        )
    }

    try:
        thread = await client.beta.threads.create()
        run = await client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant_id,
            instructions=instructions["censure"]
        )

        if run.status == 'completed':
            messages_page = await client.beta.threads.messages.list(thread_id=thread.id)
            async for message in messages_page:
                if message.content and isinstance(message.content, list):
                    for content_block in message.content:
                        if hasattr(content_block, 'text') and hasattr(content_block.text, 'value'):
                            return content_block.text.value
            return "Нет ответа от ассистента."
        return f"Ошибка: статус {run.status}"
    except Exception as e:
        print(f"Ошибка при работе с ассистентом: {e}")
        return "Ошибка при взаимодействии с ассистентом."


async def parse_response(response: str) -> dict:
    try:
        # Поиск начала и конца JSON-строки в ответе
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
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
    if response_assist in ('censure', 'zero'):
        return response_assist

    # Если заказ прошел проверку, формируем JSON с извлеченными данными
    prompt = (
        f"Пожалуйста, извлеките и структурируйте следующую информацию о заказе в формате JSON без дополнительных комментариев и текстов:\n"
        f"Заказ: {order_text}\n"
        f"Строго в формате JSON:\n"
        f"{{\n"
        f'  "City": "Город",\n'
        f'  "Starting point A": "Первый пункт доставки",\n'
        f'  "Destination point B": "Второй пункт доставки",\n'
        f'  "Delivery object": "Объект доставки",\n'
        f'  "Receiver name": "Имя получателя (если указывается)",\n'
        f'  "Receiver phone": "Номер получателя (если указывается)",\n'
        f'  "Comments": "Комментарии (если указываются)"\n'
        f"}}"
    )

    response = await get_gpt_text(prompt)
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
