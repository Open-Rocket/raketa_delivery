import os
import json
from fuzzywuzzy import process
from src.config import log


class Cities:
    _cities = []
    _millions_cities = []
    _small_cities = []
    _cache_path = "src/parser/json/russian-cities-list.json"
    _millions_cache_path = "src/parser/json/millions-cities.json"
    _small_cache_path = "src/parser/json/small-cities.json"
    _json_path = "src/parser/json/russian-cities.json"

    @classmethod
    async def _load_cities_from_json(cls):
        """Загружает города из JSON и сохраняет в список и кэш."""

        if not os.path.exists(cls._json_path):
            log.error(f"Файл {cls._json_path} не найден")
            raise FileNotFoundError(f"Файл {cls._json_path} не найден")

        with open(cls._json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        cls._cities = [city["name"] for city in data]

        with open(cls._cache_path, "w", encoding="utf-8") as f:
            json.dump(cls._cities, f, ensure_ascii=False, indent=4)

        log.info("Города загружены из JSON и сохранены в кэш")

    @classmethod
    async def _load_millions_cities_from_json(cls):
        """Загружает города-миллионники из JSON и сохраняет в кэш."""

        if not os.path.exists(cls._json_path):
            log.error(f"Файл {cls._json_path} не найден")
            raise FileNotFoundError(f"Файл {cls._json_path} не найден")

        with open(cls._json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        cls._millions_cities = [
            obj["name"] for obj in data if obj.get("population", 0) >= 1_000_000
        ]

        with open(cls._millions_cache_path, "w", encoding="utf-8") as f:
            json.dump(cls._millions_cities, f, ensure_ascii=False, indent=4)

        log.info("Города-миллионники загружены из JSON и сохранены в кэш")

    @classmethod
    async def _load_small_cities_from_json(cls):
        """Загружает города с населением < 300 000 из JSON и сохраняет в кэш."""

        if not os.path.exists(cls._json_path):
            log.error(f"Файл {cls._json_path} не найден")
            raise FileNotFoundError(f"Файл {cls._json_path} не найден")

        with open(cls._json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        cls._small_cities = [
            obj["name"] for obj in data if obj.get("population", 0) < 300_000
        ]

        with open(cls._small_cache_path, "w", encoding="utf-8") as f:
            json.dump(cls._small_cities, f, ensure_ascii=False, indent=4)

        log.info("Малые города загружены из JSON и сохранены в кэш")

    @classmethod
    async def get_cities(cls):
        """Возвращает список городов, загружая из кеша или JSON при необходимости."""

        if not cls._cities:
            if os.path.exists(cls._cache_path):
                try:
                    with open(cls._cache_path, "r", encoding="utf-8") as f:
                        cls._cities = json.load(f)
                    log.info("Города загружены из кэша")
                except Exception as e:
                    log.error(f"Ошибка при загрузке из кэша: {e}")
                    await cls._load_cities_from_json()
            else:
                await cls._load_cities_from_json()
        return cls._cities

    @classmethod
    async def get_millions_cities(cls):
        """Возвращает список городов-миллионников, загружая из кэша или JSON при необходимости."""

        if not cls._millions_cities:
            if os.path.exists(cls._millions_cache_path):
                try:
                    with open(cls._millions_cache_path, "r", encoding="utf-8") as f:
                        cls._millions_cities = json.load(f)
                    log.info("Города-миллионники загружены из кэша")
                except Exception as e:
                    log.error(f"Ошибка при загрузке из кэша: {e}")
                    await cls._load_millions_cities_from_json()
            else:
                await cls._load_millions_cities_from_json()

        return cls._millions_cities

    @classmethod
    async def get_small_cities(cls):
        """Возвращает список городов с населением менее 300 000, загружая из кэша или JSON при необходимости."""

        if not cls._small_cities:
            if os.path.exists(cls._small_cache_path):
                try:
                    with open(cls._small_cache_path, "r", encoding="utf-8") as f:
                        cls._small_cities = json.load(f)
                    log.info("Малые города загружены из кэша")
                except Exception as e:
                    log.error(f"Ошибка при загрузке из кэша: {e}")
                    await cls._load_small_cities_from_json()
            else:
                await cls._load_small_cities_from_json()

        return cls._small_cities


async def find_closest_city(city_name: str, cities: list):
    """Поиск наилучшего совпадения с учётом опечаток."""

    if not city_name or not city_name.strip():
        log.warning("Пустой текст для поиска города")
        return None, 0

    city_name = city_name.lower()
    if city_name == "питер":
        city_name = "Санкт-Петербург"
    elif city_name == "екб":
        city_name = "Екатеринбург"
    elif city_name == "мск":
        city_name = "Москва"

    result = process.extractOne(city_name, cities, score_cutoff=73)

    if result:
        matched_city, score = result
        log.info(f"Найден город: {matched_city}, score={score}")
        return matched_city, score
    else:
        log.warning(f"Город не найден для текста: {city_name}")
        return None, 0


cities = Cities()
cities_2 = Cities()


__all__ = ["cities", "cities", "find_closest_city"]
