import urllib3
import requests
from datetime import datetime
from math import cos, radians, sin, sqrt, atan2
from src.config import YANDEX_API_KEY_Gogich, YANDEX_API_KEY_Olia, YANDEX_API_KEY_Erel
from src.services.fuzzy import cities
from src.config import log
from src.confredis import rediska
from src.services.db_requests import admin_data


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class RouteMaster:

    YANDEX_API_KEYS = [
        YANDEX_API_KEY_Gogich,
        YANDEX_API_KEY_Olia,
        YANDEX_API_KEY_Erel,
    ]

    @staticmethod
    async def get_coordinates(address: str) -> tuple:
        """Попытка получить координаты через Яндекс с несколькими ключами"""

        counter = await rediska.get_yandex_api_counter()

        while True:

            if not address.strip():
                log.warning(f"Пустой адрес передан в геокодирование: {address}")
                return (None, None)

            coordinates = await RouteMaster._get_coordinates_from_yandex(
                address, counter
            )

            if coordinates != (None, None):
                return coordinates

            counter += 1

            if counter >= len(RouteMaster.YANDEX_API_KEYS):
                counter = 0

            await rediska.set_yandex_api_counter(counter)

    @staticmethod
    async def _get_coordinates_from_yandex(
        address: str,
        counter: int,
    ) -> tuple:
        """Попытка получить координаты через Яндекс API с конкретным ключом"""

        api_key = RouteMaster.YANDEX_API_KEYS[counter]
        base_url = "https://geocode-maps.yandex.ru/1.x/"
        params = {"apikey": api_key, "geocode": address, "format": "json"}

        log.info(f"yandex_api_counter: {counter}")

        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()

            json_data = response.json()
            feature_members = json_data["response"]["GeoObjectCollection"][
                "featureMember"
            ]

            if not feature_members:
                log.warning(f"Нет результатов геокодирования для адреса: {address}")
                return (None, None)

            pos = feature_members[0]["GeoObject"]["Point"]["pos"]
            longitude, latitude = pos.split()
            return latitude, longitude

        except requests.RequestException as e:
            log.error(
                f"Error while getting coordinates from Yandex with key {api_key}: {e}"
            )
            return (None, None)

    @staticmethod
    async def calculate_total_distance(
        coordinates,
        adjustment_factor: int = 1.34,
    ) -> int:
        """Рассчитывает общее расстояние между набором координат с учётом погрешности"""

        R = 6371  # радиус Земли в километрах
        total_distance = 0

        for i in range(len(coordinates) - 1):
            lat1, lon1 = coordinates[i]
            lat2, lon2 = coordinates[i + 1]

            lat1, lon1, lat2, lon2 = map(radians, map(float, [lat1, lon1, lat2, lon2]))

            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            distance = R * c
            total_distance += distance

        return total_distance * adjustment_factor

    @staticmethod
    async def get_rout(
        pickup_coords: tuple,
        delivery_coords: list,
    ) -> str:
        """Генерирует URL маршрута на Яндекс.Картах."""

        # Проверяем правильность координат
        if not all(
            isinstance(coord, tuple) and len(coord) == 2
            for coord in [pickup_coords] + delivery_coords
        ):
            return "Ошибка: некорректный формат координат"

        route_points = [f"{pickup_coords[0]},{pickup_coords[1]}"] + [
            f"{coord[0]},{coord[1]}" for coord in delivery_coords
        ]

        # Логируем координаты для отладки
        log.info(f"Pickup coordinates: {pickup_coords}")
        log.info(f"Delivery coordinates: {delivery_coords}")

        return f"https://yandex.ru/maps/?rtext={'~'.join(route_points)}&rtt=auto"

    @staticmethod
    async def get_price(
        distance: int,
        order_time: datetime,
        city=None,
        over_price=0,
    ) -> int:
        """Рассчитывает стоимость доставки."""

        millions_cities = await cities.get_millions_cities()
        small_cities = await cities.get_small_cities()

        common_price, max_price = await admin_data.get_order_prices()

        base_price_per_km = max_price if 0 < distance <= 2 else common_price

        city_coefficient = 1.0
        time_coefficient = 1.0
        distance_coefficient = 1.0

        if city in millions_cities:
            city_coefficient = await admin_data.get_big_cities_coefficient()

        if city in small_cities:
            city_coefficient = await admin_data.get_small_cities_coefficient()

        if 0 <= order_time.hour < 6:
            time_coefficient = await admin_data.get_time_coefficient_00_06()
        elif 6 <= order_time.hour < 12:
            time_coefficient = await admin_data.get_time_coefficient_06_12()
        elif 12 <= order_time.hour < 18:
            time_coefficient = await admin_data.get_time_coefficient_12_18()
        elif 18 <= order_time.hour < 21:
            time_coefficient = await admin_data.get_time_coefficient_18_21()
        else:
            time_coefficient = await admin_data.get_time_coefficient_21_00()

        if distance <= 5:
            distance_coefficient = await admin_data.get_distance_coefficient_less_5()
        elif 5 < distance <= 10:
            distance_coefficient = await admin_data.get_distance_coefficient_5_10()
        elif 10 < distance <= 20:
            distance_coefficient = await admin_data.get_distance_coefficient_10_20()
        else:
            distance_coefficient = await admin_data.get_distance_coefficient_more_20()

        total_coefficient = city_coefficient * time_coefficient * distance_coefficient
        total_price = base_price_per_km * distance * total_coefficient
        price = int(total_price + over_price)

        return price


route = RouteMaster()


__all__ = ["route"]
