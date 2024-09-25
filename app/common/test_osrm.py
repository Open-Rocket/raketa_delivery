from app.common.coords_and_price import calculate_osrm_route
import asyncio


async def osrm():
    distance, duration = await calculate_osrm_route((55.693597, 37.532448),
                                                    (55.780233, 37.63376),
                                                    (55.755831, 37.617673))
    print(f"Общая дистанция: {distance} км, Общее время: {duration} минут")


asyncio.run(osrm())
