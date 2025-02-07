import asyncio

import aiohttp
import os
import requests
import math
import urllib3
from math import cos, radians, sin, sqrt, atan2
from dotenv import load_dotenv

load_dotenv()

YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


async def calculate_total_distance(coordinates, adjustment_factor=1.34):
    """
    Рассчитывает общее расстояние между набором координат с учётом погрешности.
    coords - список кортежей вида (широта, долгота)
    adjustment_factor - коэффициент увеличения (по умолчанию 1.1 для 10% погрешности)
    """
    R = 6371  # радиус Земли в километрах
    total_distance = 0

    # Проходим по списку координат и считаем расстояние между каждой парой
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

    # Применяем коэффициент погрешности
    total_distance *= adjustment_factor

    return total_distance


async def get_price(distance, order_time, city=None, over_price=0) -> int:
    city = city

    # Базовая цена за километр
    if 0 < distance <= 2:
        base_price_per_km = 101
    else:
        base_price_per_km = 38

    # Устанавливаем универсальный коэффициент для всех городов
    city_coefficient = 1.0

    # Коэффициент на основе времени заказа
    if 0 <= order_time.hour < 6:
        time_coefficient = 1.15  # Ночью наибольший
    elif 6 <= order_time.hour < 12:
        time_coefficient = 1  # Утро стандартное
    elif 12 <= order_time.hour < 18:
        time_coefficient = 1.1  # Днем повышенный
    else:
        time_coefficient = 1.07  # Вечером выше среднего

    # Коэффициент на основе дистанции
    if distance <= 5:
        distance_coefficient = 1
    elif 5 < distance <= 10:
        distance_coefficient = 0.9
    elif 10 < distance <= 20:
        distance_coefficient = 0.8
    else:
        distance_coefficient = 0.7

    # Общий коэффициент
    total_coefficient = city_coefficient * time_coefficient * distance_coefficient

    # Итоговая цена
    total_price = base_price_per_km * distance * total_coefficient

    return int(total_price + over_price)


async def get_coordinates(address):
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
    else:
        return None, None


async def get_rout(pickup_coords: tuple, delivery_coords: list) -> tuple:

    route_points = [f"{pickup_coords[0]},{pickup_coords[1]}"] + [
        f"{coord[0]},{coord[1]}" for coord in delivery_coords
    ]
    yandex_maps_url = f"https://yandex.ru/maps/?rtext={'~'.join(route_points)}&rtt=auto"

    return yandex_maps_url
