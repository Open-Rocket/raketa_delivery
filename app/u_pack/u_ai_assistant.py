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
    

    async def _get_parsed_addresses(self, response) -> list:


        address_pattern = re.compile(r"\((.*?)\)")
        matches = address_pattern.findall(response)

        addresses = []
        for match in matches:
            if "," in match:
                addresses.append(match.strip())

        return addresses

    
    async def process_order(self, order_text: str, city: str = None) -> tuple[str, dict, str] | None:
        
        instruction = "Извлеки и структурируй следующую информацию о заказе без дополнительных комментариев и текстов"
        only_city = "Извлеки только город заказа."
        parsed_address = (
            "Извлеки все адреса в следующем формате:\n"
            "(Город (обязательно), Тип объекта: улица, поселок, деревня, село, аэропорт, вокзал, станция, станция метро и т.д., "
            "Название объекта, номер улицы или дома, город или населенный пункт)\n"
        )
        description = "Опиши грамотно и полностью заказ"

        request = {
            "instruction": instruction,
            "order_text": order_text,
            "returned_data": {"city": only_city, "addresses": parsed_address, "description": description}
        }

        response: dict = await self._get_gpt_text(request)
        returned_data: dict = response.get("returned_data")
        city = returned_data.get("city")
        addresses = await self._get_parsed_addresses(returned_data.get("addresses"))
        description = response.get("description")

        return city, addresses, description





