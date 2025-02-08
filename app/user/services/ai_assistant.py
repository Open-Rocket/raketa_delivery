import os
import re
import httpx
import json
from openai import AsyncOpenAI
from app.user.services import logger
from dotenv import load_dotenv

load_dotenv()

PROXY = os.getenv("PROXY")
OPENAI_API_KEY = os.getenv("OPENAI_API")
AI_ASSISTANT_ID = os.getenv("AI_ASSISTANT_ID")


class AssistantAi:
    def __init__(self):
        self.proxy = PROXY
        self.api_key = OPENAI_API_KEY
        self.assistant_id = AI_ASSISTANT_ID

        self.client = AsyncOpenAI(
            api_key=self.api_key,
            http_client=httpx.AsyncClient(
                proxies=self.proxy,
                transport=httpx.AsyncHTTPTransport(local_address="0.0.0.0"),
            ),
        )

    async def _get_gpt_text(self, request: str, model="gpt-4o-mini"):
        try:

            # logger.info(f"Sending request to GPT: {request}")

            completion = await self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "Ты — ассистент по обработке заказов.",
                    },
                    {"role": "user", "content": request},
                ],
                model=model,
            )
            response_text = completion.choices[0].message.content
            # logger.info(f"\n-----\nGPT response: {response_text}\n-----")
            return response_text
        except Exception as e:
            logger.error(f"Error in getting response from GPT: {e}")
            return None

    async def _get_parsed_addresses(self, response) -> list:
        address_pattern = re.compile(r"\((.*?)\)")
        matches = address_pattern.findall(response)

        addresses = []
        for match in matches:
            if "," in match:
                addresses.append(match.strip())

        return addresses

    async def process_order(
        self, order_text: str, city: str = None
    ) -> tuple[str, list, str] | None:

        instruction = "Извлеки и структурируй следующую информацию о заказе без дополнительных комментариев и текстов."
        only_city = "Город заказа."
        if_not_city_use = f"Если город не указан в адресе то используй {city}."
        parsed_address = (
            "Извлеки все адреса в следующем формате, подходящем для передачи в геокодер: "
            "(Город, улица, дом, корпус, индекс, если доступно). Например: 'Москва, проспект Вернадского, дом 76, корпус 2, 119333'. "
            "Убедись, что все элементы адреса извлечены корректно и без ошибок."
        )
        description = "Опиши текстом, грамотно и полностью заказ."
        delivery_object = "Извлеки только предмет доставки"

        request = {
            "instruction": instruction,
            "order_text": order_text,
            "order_city": if_not_city_use,
            "returned_data": {
                "city": only_city,
                "addresses": parsed_address,
                "delivery_object": delivery_object,
                "description": description,
            },
        }

        messages_json = json.dumps(request, ensure_ascii=False)

        try:

            response_str = await self._get_gpt_text(messages_json)

            if not response_str:
                logger.error("Empty response from GPT.")
                return None

            response: dict = json.loads(response_str)

            city = response.get("city", "")
            addresses = response.get("addresses", [])
            delivery_object = response.get("delivery_object", "-")
            description = response.get("description", "")

            # logger.info(f"\n-----\ncity: {city}\n-----")
            # logger.info(f"addresses: {addresses}\n-----")
            # logger.info(f"description: {description}\n-----")

            return city, addresses, delivery_object, description

        except json.JSONDecodeError:
            logger.error("Ошибка при парсинге JSON ответа от GPT.")
            return None

        except Exception as e:
            logger.error(f"Произошла ошибка: {e}")
            return None
