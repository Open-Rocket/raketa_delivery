import asyncio
from app.common.coords_and_price import get_coordinates

address_1 = "Москва проспект Вернадского 76/2"
address_2 = "Москва улица Академика Анохина 20/3"
address_3 = "Москва улица Юных Ленинцев 25"
address_x1 = "Москва", "улица", "проспект Вернадского", "76, корпус 2", "Москва"
address_x2 = "Москва", "улица", "Академика Анохина", "20", "Москва"


async def show_coords(add_1, add_2):
    coord_1 = await get_coordinates(add_1)
    print(coord_1)
    coord_2 = await get_coordinates(add_2)
    print(coord_2)

    yandex_maps_url = (
        f"https://yandex.ru/maps/?rtext={coord_1[0]},{coord_1[1]}"
        f"~{coord_2[0]},{coord_2[1]}&rtt=auto"
    )
    print(yandex_maps_url)
    pickup_point = (
        f"https://yandex.ru/maps/?ll={coord_1[1]},{coord_1[0]}"
        f"&pt={coord_1[1]},{coord_1[0]}&z=14"
    )
    print(pickup_point)
    pickup_point_2 = (
        f"https://yandex.ru/maps/?ll={coord_2[1]},{coord_2[0]}"
        f"&pt={coord_2[1]},{coord_2[0]}&z=14"
    )
    print(pickup_point_2)


asyncio.run(show_coords(address_1, address_3))
