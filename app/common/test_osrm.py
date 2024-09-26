from app.common.coords_and_price import calculate_osrm_route, calculate_total_distance
import asyncio


async def osrm():

    # Владикавказ
    coords1 = [(43.0220, 44.6750), (43.0215, 44.6980)]

    # Москва
    coords_list = [
        [(55.693597, 37.532448), (55.780233, 37.633760)],  # Южное Тушино и Тверской район
        [(55.755831, 37.617673), (55.810251, 37.510598)],  # Кремль и Кунцево
        [(55.856888, 37.617300), (55.749079, 37.537864)],  # Речной вокзал и Арбат
        [(55.738132, 37.613061), (55.799295, 37.601068)],  # Измайлово и Сокол
        [(55.769149, 37.643131), (55.850500, 37.617600)]  # Лужники и Шелепиха
    ]

    distance, duration = await calculate_osrm_route(*coords_list[4])

    distance_m, duration_m = calculate_total_distance(coords_list[4], adjustment_factor=1.33)

    print(f"test osrm - Общая дистанция: {distance:.2f} км, Общее время: {duration} минут")
    print(f"test math - Общая дистанция: {distance_m:.2f} км, Общее время: {duration_m} минут")


asyncio.run(osrm())
