from dependencies._dependencies import (
    requests,
    datetime,
    urllib3,
    sqrt,
    sin,
    cos,
    atan2,
    radians,
)
from config import YANDEX_API_KEY


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class RouteMaster:
    """
    Класс для расчета расстояний, стоимости доставки и получения маршрутов.
    """

    @staticmethod
    async def get_coordinates(address: str) -> tuple[str, str] | tuple[None, None]:
        """
        Получает координаты по адресу через API Яндекса.
        :param address: строка с адресом
        :return: кортеж (широта, долгота) или (None, None) при ошибке
        """

        base_url = "https://geocode-maps.yandex.ru/1.x/"
        params = {"apikey": YANDEX_API_KEY, "geocode": address, "format": "json"}
        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            json_data = response.json()
            pos = json_data["response"]["GeoObjectCollection"]["featureMember"][0][
                "GeoObject"
            ]["Point"]["pos"]
            longitude, latitude = pos.split()
            return latitude, longitude
        return None, None

    @staticmethod
    async def calculate_total_distance(
        coordinates, adjustment_factor: int = 1.34
    ) -> int:
        """
        Рассчитывает общее расстояние между набором координат с учётом погрешности.
        :param coordinates: список кортежей вида (широта, долгота)
        :param adjustment_factor: коэффициент увеличения (по умолчанию 1.34)
        :return: общее расстояние
        """
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
    async def get_rout(pickup_coords: tuple, delivery_coords: list) -> str:
        """
        Генерирует URL маршрута на Яндекс.Картах.
        :param pickup_coords: координаты точки отправки (широта, долгота)
        :param delivery_coords: список координат точек доставки [(широта, долгота), ...]
        :return: URL маршрута
        """
        route_points = [f"{pickup_coords[0]},{pickup_coords[1]}"] + [
            f"{coord[0]},{coord[1]}" for coord in delivery_coords
        ]
        return f"https://yandex.ru/maps/?rtext={'~'.join(route_points)}&rtt=auto"

    @staticmethod
    async def get_price(
        distance: int, order_time: datetime, city=None, over_price=0
    ) -> int:
        """
        Рассчитывает стоимость доставки.
        :param distance: расстояние в км
        :param order_time: время заказа (datetime)
        :param city: город (опционально)
        :param over_price: надбавка к стоимости
        :return: стоимость доставки
        """
        base_price_per_km = 101 if 0 < distance <= 2 else 38
        city_coefficient = 1.0

        if 0 <= order_time.hour < 6:
            time_coefficient = 1.15
        elif 6 <= order_time.hour < 12:
            time_coefficient = 1.0
        elif 12 <= order_time.hour < 18:
            time_coefficient = 1.1
        else:
            time_coefficient = 1.07

        if distance <= 5:
            distance_coefficient = 1.0
        elif 5 < distance <= 10:
            distance_coefficient = 0.9
        elif 10 < distance <= 20:
            distance_coefficient = 0.8
        else:
            distance_coefficient = 0.7

        total_coefficient = city_coefficient * time_coefficient * distance_coefficient
        total_price = base_price_per_km * distance * total_coefficient

        return int(total_price + over_price)


route = RouteMaster()


__all__ = ["route"]
