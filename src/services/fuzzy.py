import os
import sys
import asyncio
import json
from fuzzywuzzy import process, fuzz

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from config import log


class CityList:
    _cities = []
    _cache_path = "parser/json/russian-cities-list.json"
    _json_path = "parser/json/russian-cities.json"

    @classmethod
    async def _load_cities_from_json(cls):
        """Загружает города из JSON и сохраняет в список и кэш."""
        if not os.path.exists(cls._json_path):
            raise FileNotFoundError(f"Файл {cls._json_path} не найден")

        with open(cls._json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        cls._cities = [city["name"] for city in data]

        with open(cls._cache_path, "w", encoding="utf-8") as f:
            json.dump(cls._cities, f, ensure_ascii=False, indent=4)

        log.info("Города загружены из JSON и сохранены в кеш")

    @classmethod
    async def get_cities(cls):
        """Возвращает список городов. Загружает из кеша, если данные уже есть."""
        if not cls._cities:  # Если города не загружены в память
            if os.path.exists(cls._cache_path):
                with open(cls._cache_path, "r", encoding="utf-8") as f:
                    cls._cities = json.load(f)
            else:
                cls.load_cities_from_json()

        return cls._cities


async def find_closest_city(city_name: str, russian_cities: list):
    """Поиск наилучшего совпадения с учётом опечаток"""
    result = process.extractOne(city_name, russian_cities, score_cutoff=73)
    return result


async def main():

    # await CityList._load_cities_from_json()
    russian_cities = await CityList.get_cities()

    user_input = "Яркутск"
    if user_input.lower() == "питер":
        user_input = "Санкт-Петербург"
    elif user_input.lower() == "екб":
        user_input = "Екатеринбург"
    closest_city = await find_closest_city(user_input, russian_cities)
    # closest_city = await find_most_compatible_response(user_input, russian_cities)

    if closest_city:
        match, score = closest_city
        log.info(f"Самое близкое совпадение: {match}, коэффициент: {score}")
    else:
        log.info("Город не найден.")


asyncio.run(main())


# python -m src.services.fuzzy
