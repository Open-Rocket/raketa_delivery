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
        time_coefficient = 1.1  # Ночью наибольший
    elif 6 <= order_time.hour < 12:
        time_coefficient = 1  # Утро стандартное
    elif 12 <= order_time.hour < 18:
        time_coefficient = 1  # Днем стандартное
    else:
        time_coefficient = 1.05  # Вечером выше

    # Коэффициент на основе дистанции
    if distance <= 5:
        distance_coefficient = 1
    elif 5 < distance <= 10:
        distance_coefficient = 0.8
    elif 10 < distance <= 20:
        distance_coefficient = 0.7
    else:
        distance_coefficient = 0.6

    # Общий коэффициент
    total_coefficient = city_coefficient * time_coefficient * distance_coefficient

    # Итоговая цена
    total_price = base_price_per_km * distance * total_coefficient

    return int(total_price + over_price)


# OSRM
async def calculate_osrm_route(*coordinates):
    """
    Вычисление маршрута с использованием OSRM для любого количества точек.
    :param coordinates: пары (latitude, longitude) для каждой точки.
    :return: общая дистанция в км и общее время в минутах для всего маршрута.
    """
    if len(coordinates) < 2:
        print("Необходимо как минимум две точки для расчета маршрута.")
        return None, None

    # Создаем URL для запроса, соединяя все координаты через точку с запятой
    coord_str = ";".join([f"{lon},{lat}" for lat, lon in coordinates])
    url = f"http://localhost:5001/route/v1/driving/{coord_str}?overview=false"  # Изменен порт на 5001

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    print(f"Ошибка: {response.status}, Ответ: {await response.text()}")
                    return None, None

                # Проверяем, что ответ не пустой и данные в формате JSON
                try:
                    data = await response.json()
                except ValueError:
                    print("Ошибка: Невозможно декодировать JSON ответ")
                    return None, None

                time_coefficient = 1.6  # коэффициент для более точного времени доставки

                if data.get("routes"):
                    total_distance = (
                        data["routes"][0].get("distance", 0) / 1000
                    )  # расстояние в километрах
                    total_duration = data["routes"][0].get(
                        "duration"
                    )  # время в секундах

                    # Проверяем, что total_duration не является None
                    if total_duration is not None:
                        total_duration /= 60  # переводим в минуты
                        return int(math.ceil(total_distance)), int(
                            math.ceil(total_duration * time_coefficient)
                        )
                    else:
                        print("Ошибка: Продолжительность маршрута не найдена")
                        return None, None
                else:
                    print("Маршрут не найден")
                    return None, None
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return None, None


# async def calculate_osrm_route(*coordinates):
#     """
#     Вычисление маршрута с использованием OSRM для любого количества точек.
#     :param coordinates: пары (latitude, longitude) для каждой точки.
#     :return: общая дистанция в км и общее время в минутах для всего маршрута.
#     """
#     if len(coordinates) < 2:
#         print("Необходимо как минимум две точки для расчета маршрута.")
#         return None, None
#
#     # Создаем URL для запроса, соединяя все координаты через точку с запятой
#     coord_str = ";".join([f"{lon},{lat}" for lat, lon in coordinates])
#     url = f"http://localhost:5000/route/v1/driving/{coord_str}?overview=false"  # Укажите адрес вашего сервера OSRM
#
#     try:
#         response = requests.get(url)  # Запрос к вашему серверу OSRM
#         if response.status_code != 200:
#             print(f"Ошибка: {response.status_code}, Ответ: {response.text}")
#             return None, None
#
#         # Проверяем, что ответ не пустой и данные в формате JSON
#         try:
#             data = response.json()
#         except ValueError:
#             print("Ошибка: Невозможно декодировать JSON ответ")
#             return None, None
#
#         time_coefficient = 1.6  # коэфициент для более точного времени доставки
#
#         if data.get('routes'):
#             total_distance = data['routes'][0].get('distance', 0) / 1000  # расстояние в километрах
#             total_duration = data['routes'][0].get('duration')  # время в секундах
#
#             # Проверяем, что total_duration не является None
#             if total_duration is not None:
#                 total_duration /= 60  # переводим в минуты
#                 return int(math.ceil(total_distance)), int(math.ceil(total_duration * time_coefficient))
#             else:
#                 print("Ошибка: Продолжительность маршрута не найдена")
#                 return None, None
#         else:
#             print("Маршрут не найден")
#             return None, None
#     except Exception as e:
#         print(f"Произошла ошибка: {e}")
#         return None, None


# async def calculate_osrm_route(*coordinates):
#     """
#     Вычисление маршрута с использованием OSRM для любого количества точек.
#     :param coordinates: пары (latitude, longitude) для каждой точки.
#     :return: общая дистанция в км и общее время в минутах для всего маршрута.
#     """
#     if len(coordinates) < 2:
#         print("Необходимо как минимум две точки для расчета маршрута.")
#         return None, None
#
#     # Создаем URL для запроса, соединяя все координаты через точку с запятой
#     coord_str = ";".join([f"{lon},{lat}" for lat, lon in coordinates])
#     url = f"https://router.project-osrm.org/route/v1/driving/{coord_str}?overview=false"
#
#     response = requests.get(url)
#     data = response.json()
#     time_coefficient = 1.6  # коэфициент для более точного времени доставки
#
#     if response.status_code == 200:
#         if data['routes']:
#             total_distance = data['routes'][0]['distance'] / 1000  # расстояние в километрах
#             total_duration = data['routes'][0]['duration'] / 60  # время в минутах
#             return int(math.ceil(total_distance)), int(math.ceil(total_duration * time_coefficient))
#         else:
#             print("Маршрут не найден")
#             return None, None
#     else:
#         print(f"Ошибка: {response.status_code}, Ответ: {response.text}")
#         return None, None


# async def calculate_osrm_route(pickup_latitude, pickup_longitude, delivery_latitude, delivery_longitude):
#     url = (f"https://router.project-osrm.org/route/v1/driving/{pickup_longitude},{pickup_latitude};"
#            f"{delivery_longitude},{delivery_latitude}?overview=false")
#
#     response = requests.get(url)
#     data = response.json()
#     time_coefficient = 1.6
#
#     if response.status_code == 200:
#         if data['routes']:
#             distance = data['routes'][0]['distance'] / 1000  # расстояние в километрах
#             duration = data['routes'][0]['duration'] / 60  # время в минутах
#             return int(math.ceil(distance)), int(math.ceil(duration * time_coefficient))
#         else:
#             print("Маршрут не найден")
#             return None, None
#     else:
#         print(f"Ошибка: {response.status_code}, Ответ: {response.text}")
#         return None, None
