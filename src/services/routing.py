import urllib3
import requests
from datetime import datetime
from math import cos, radians, sin, sqrt, atan2
from src.config import YANDEX_API_KEY
from src.services.fuzzy import cities
from geopy.distance import geodesic
from src.config import log
from src.confredis import rediska


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class RouteMaster:

    YANDEX_API_KEYS = [
        YANDEX_API_KEY,
        "your_yandex_api_key_2",
        "your_yandex_api_key_3",
    ]

    @staticmethod
    async def get_coordinates(address: str) -> tuple:
        """Попытка получить координаты через Яндекс с несколькими ключами"""

        counter = await rediska.get_yandex_api_counter()

        while counter < len(RouteMaster.YANDEX_API_KEYS):
            coordinates = await RouteMaster._get_coordinates_from_yandex(
                address,
                counter,
            )
            if coordinates != (None, None):
                return coordinates
            counter += 1
            await rediska.set_yandex_api_counter(counter)

        return None, None

    @staticmethod
    async def _get_coordinates_from_yandex(
        address: str,
        counter: int,
    ) -> tuple:
        """Попытка получить координаты через Яндекс API с конкретным ключом"""

        api_key = RouteMaster.YANDEX_API_KEYS[counter]
        base_url = "https://geocode-maps.yandex.ru/1.x/"
        params = {"apikey": api_key, "geocode": address, "format": "json"}

        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()  # Поднимет исключение, если статус не 2xx
        except requests.RequestException as e:
            log.error(
                f"Error while getting coordinates from Yandex with key {api_key}: {e}"
            )
            return (None, None)

        if response.status_code == 200:
            json_data = response.json()
            pos = json_data["response"]["GeoObjectCollection"]["featureMember"][0][
                "GeoObject"
            ]["Point"]["pos"]
            longitude, latitude = pos.split()
            return latitude, longitude

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

        route_points = [f"{pickup_coords[0]},{pickup_coords[1]}"] + [
            f"{coord[0]},{coord[1]}" for coord in delivery_coords
        ]
        return f"https://yandex.ru/maps/?rtext={'~'.join(route_points)}&rtt=auto"

    @staticmethod
    async def get_price(
        distance: int,
        order_time: datetime,
        city=None,
        over_price=0,
    ) -> int:
        """
        Рассчитывает стоимость доставки.
        :param distance: расстояние в км
        :param order_time: время заказа (datetime)
        :param city: город (опционально)
        :param over_price: надбавка к стоимости
        :return: стоимость доставки
        """

        millions_cities = await cities.get_millions_cities()
        small_cities = await cities.get_small_cities()

        base_price_per_km = 100 if 0 < distance <= 2 else 38
        city_coefficient = 1.0

        if city in millions_cities:
            city_coefficient = 1.045

        if city in small_cities:
            city_coefficient = 0.9

        if 0 <= order_time.hour < 6:
            time_coefficient = 1.15
        elif 6 <= order_time.hour < 12:
            time_coefficient = 1.0
        elif 12 <= order_time.hour < 18:
            time_coefficient = 1.1
        else:
            time_coefficient = 1.07

        if distance <= 5:
            distance_coefficient = 0.9
        elif 5 < distance <= 10:
            distance_coefficient = 1.0
        elif 10 < distance <= 20:
            distance_coefficient = 0.8
        else:
            distance_coefficient = 0.7

        total_coefficient = city_coefficient * time_coefficient * distance_coefficient
        total_price = base_price_per_km * distance * total_coefficient

        return int(total_price + over_price)

    @staticmethod
    async def is_within_radius(
        courier_coords: tuple,
        order_coords: tuple,
        radius_km: int,
    ) -> bool:
        """Проверяет, находится ли заказ в радиусе курьера"""
        return geodesic(courier_coords, order_coords).km <= radius_km


route = RouteMaster()


__all__ = ["route"]
