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


def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # радиус Земли в километрах
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance


async def calculate_total_distance(coordinates, adjustment_factor=1.34):
    """
    Рассчитывает общее расстояние между набором координат с учётом погрешности.
    coords - список кортежей вида (широта, долгота)
    adjustment_factor - коэффициент увеличения (по умолчанию 1.1 для 10% погрешности)
    """
    R = 6371  # радиус Земли в километрах
    total_distance = 0
    avg_speed = 25.0

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
    duration = int((total_distance / avg_speed) * 60)

    return total_distance, duration


async def calculate_manhattan_distance(coordinates, adjustment_factor=1.34):
    """
    Рассчитывает манхэттенское расстояние между набором координат с учётом погрешности.
    coords - список кортежей вида (широта, долгота)
    adjustment_factor - коэффициент увеличения (по умолчанию 1.34 для учёта сетки дорог)
    """
    R = 6371  # радиус Земли в километрах
    total_distance = 0
    avg_speed = 25.0

    # Функция для перевода градусов в километры
    def deg_to_km(deg):
        return (deg * math.pi / 180) * R

    # Проходим по списку координат и считаем манхэттенское расстояние
    for i in range(len(coordinates) - 1):
        lat1, lon1 = coordinates[i]
        lat2, lon2 = coordinates[i + 1]

        # Рассчитываем абсолютные разницы по широте и долготе
        delta_lat = abs(lat2 - lat1)
        delta_lon = abs(lon2 - lon1)

        # Переводим градусы в километры и суммируем манхэттенское расстояние
        distance = deg_to_km(delta_lat) + deg_to_km(delta_lon)
        total_distance += distance

    # Применяем коэффициент погрешности для учета реальных дорог
    total_distance *= adjustment_factor
    duration = int((total_distance / avg_speed) * 60)

    return total_distance, duration


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


async def get_rout(pickup_coords: tuple, delivery_coords: list) -> tuple:
    pickup_point = (
        f"https://yandex.ru/maps/?ll={pickup_coords[1]},{pickup_coords[0]}"
        f"&pt={pickup_coords[1]},{pickup_coords[0]}&z=14"
    )

    # Формируем маршрутную ссылку
    route_points = [f"{pickup_coords[0]},{pickup_coords[1]}"] + [
        f"{coord[0]},{coord[1]}" for coord in delivery_coords
    ]
    yandex_maps_url = f"https://yandex.ru/maps/?rtext={'~'.join(route_points)}&rtt=auto"

    # Формируем ссылки на точки доставки
    delivery_points = [
        f"https://yandex.ru/maps/?ll={coord[1]},{coord[0]}"
        f"&pt={coord[1]},{coord[0]}&z=14"
        for coord in delivery_coords
    ]

    return (yandex_maps_url, pickup_point, *delivery_points)
