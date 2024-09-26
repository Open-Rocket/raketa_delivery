from app.common.coords_and_price import calculate_osrm_route
import asyncio


async def osrm():

    # Москва
    distance, duration = await calculate_osrm_route((55.693597, 37.532448),
                                                    (55.780233, 37.63376),
                                                    (55.755831, 37.617673))

    # Владикавказ
    distance1, duration1 = await calculate_osrm_route((43.0220, 44.6750),
                                                      (43.0215, 44.6980))

    print(f"Общая дистанция: {distance1} км, Общее время: {duration1} минут")


asyncio.run(osrm())
