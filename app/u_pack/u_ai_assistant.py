import os
import re
import httpx
import json
import logging


from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class AssistantAi:

    def __init__(self):
        self.proxy = os.getenv("PROXY")
        self.apy_key = os.getenv("OPENAI_API")
        self.assistant_id = os.getenv("AI_ASSISTANT_ID")

        self.client = AsyncOpenAI(
            api_key=self.apy_key,
            http_client=httpx.AsyncClient(
                proxies=self.proxy,
                transport=httpx.AsyncHTTPTransport(local_address="0.0.0.0"),
            ),
        )


    async def _get_gpt_text(self,  request: str, model="gpt-4o-mini"):
        completion = await self.client.chat.completions.create(
            messages=[{"role": "system", "content": "Ты — ассистент по обработке заказов."},
                       {"role": "user", "content": request}], 
                       model=model
        )
        return completion.choices[0].message.content
    

    async def _get_parsed_addresses(self, form: dict, city: str) -> list:

        city_form = form.get("city")
        city = city_form if city_form else city

        prompt = (
            "Пожалуйста, извлеки из этой формы все адреса в следующем формате:\n"
            "Город (обязательно), Тип объекта: улица, поселок, деревня, село, аэропорт, вокзал, станция, станция метро и т.д., "
            "Название объекта, номер улицы или дома, город или населенный пункт).\n"
            "addresses: [(Передай в этот список кортеж из адресов по указанному формату)]\n"
            f"text: {city + ' ' if city else ''}{form} - извлеки отсюда только адреса.\n"
        )

        response = await self._get_gpt_text(prompt)

        address_pattern = re.compile(r"\((.*?)\)")
        matches = address_pattern.findall(response)

        addresses = []
        for match in matches:
            if "," in match:
                addresses.append(match.strip())

        return addresses


    async def _parse_response(self, request: str) -> dict:
        try:
            json_start = request.find("{")
            json_end = request.rfind("}") + 1
            clean_response = request[json_start:json_end]
            json_response = json.loads(clean_response)

            return json_response
        except json.JSONDecodeError as error:
            logger.info(f"Ошибка при разборе JSON ответа от модели: {error}")
            return {}

    
    async def process_order(self, order_text: str, city: str) -> tuple[dict, list] | None:


        prompt = (
            f"Пожалуйста, извлеките и структурируйте следующую информацию "
            f"о заказе в формате JSON без дополнительных комментариев и текстов, "
            f"если о чем то нет информации то обязательно ничего не заполняй,\n"
            f"если нужно возвращаться из определенной точки в одну из предыдущих, "
            f"то указывай точку возврата, полным его адресом (как в тексте), как следующую. "
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

        response = await self._get_gpt_text(prompt)
        form = await self._parse_response(response)
        addresses = await self._get_parsed_addresses(form, city)

        return form, addresses





