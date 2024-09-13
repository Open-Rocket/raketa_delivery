import math
import os

import requests
from dotenv import load_dotenv

load_dotenv()

YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")


async def get_coordinates(address):
    base_url = "https://geocode-maps.yandex.ru/1.x/"
    params = {
        "apikey": YANDEX_API_KEY,
        "geocode": address,
        "format": "json"
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        json_data = response.json()
        pos = json_data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
        longitude, latitude = pos.split()
        return latitude, longitude
    else:
        return None, None


async def calculate_osrm_route(pickup_latitude, pickup_longitude, delivery_latitude, delivery_longitude):
    url = f"https://router.project-osrm.org/route/v1/driving/{pickup_longitude},{pickup_latitude};{delivery_longitude},{delivery_latitude}?overview=false"

    response = requests.get(url)
    data = response.json()
    time_coefficient = 1.6

    if response.status_code == 200:
        if data['routes']:
            distance = data['routes'][0]['distance'] / 1000  # расстояние в километрах
            duration = data['routes'][0]['duration'] / 60  # время в минутах
            return math.ceil(distance), math.ceil(duration * time_coefficient)
        else:
            print("Маршрут не найден")
            return None, None
    else:
        print(f"Ошибка: {response.status_code}, Ответ: {response.text}")
        return None, None


async def get_price(distance, order_time, city=None):
    city = city
    base_price_per_km = 38  # Базовая цена за километр

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

    return total_price
