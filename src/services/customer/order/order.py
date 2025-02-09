from route import route_master


class OrderFormatter:
    @staticmethod
    async def prepare_data(
        time: str,
        city: str,
        customer_name: str,
        customer_phone: str,
        addresses: list[str],
        delivery_object: str,
        description: str,
    ) -> dict:
        """Готовит все необходимые данные для формирования заказа и возвращает их."""

        if not addresses:
            return {}

        coordinates = []
        address_links = []
        formatted_addresses = []
        order_addresses_data = []

        for address in addresses:
            coords = await route_master.get_coordinates(address)
            if coords:
                coordinates.append(coords)
                maps_url = f"https://maps.yandex.ru/?text={address.replace(' ', '+')}"
                address_links.append(maps_url)
                formatted_addresses.append(f"<a href='{maps_url}'>{address}</a>")
                order_addresses_data.append([coords, address])

        if len(coordinates) < 2:
            return {}

        yandex_maps_url = await route_master.get_rout(coordinates[0], coordinates[1:])
        distance = round(await route_master.calculate_total_distance(coordinates), 2)
        price = await route_master.get_price(distance, time)
        addresses_text = "\n".join(
            [
                f"⦿ <b>Адрес {i+1}:</b> {formatted_addresses[i]}"
                for i in range(len(formatted_addresses))
            ]
        )

        return {
            "city": city,
            "customer_name": customer_name,
            "customer_phone": customer_phone,
            "formatted_addresses": formatted_addresses,
            "addresses_text": addresses_text,
            "delivery_object": delivery_object,
            "description": description,
            "yandex_maps_url": yandex_maps_url,
            "distance": distance,
            "price": price,
        }

    @staticmethod
    async def format_order_form(
        city: str,
        customer_name: str,
        customer_phone: str,
        addresses_text: str,
        delivery_object: str,
        distance: int,
        price: int,
        description: int,
    ) -> str:
        """Форматирует и возвращает текст заказа на основе подготовленных данных."""

        return (
            f"<b>Ваш заказ</b> ✍︎\n"
            f"---------------------------------------------\n\n"
            f"<b>Город:</b> {city}\n\n"
            f"<b>Заказчик:</b> {customer_name}\n"
            f"<b>Телефон:</b> {customer_phone}\n\n"
            f"{addresses_text}\n\n"
            f"<b>Доставляем:</b> {delivery_object}\n"
            f"<b>Расстояние:</b> {distance} км\n"
            f"<b>Стоимость доставки:</b> {price}₽\n\n"
            f"<b>Описание:</b> {description}\n\n"
            f"---------------------------------------------\n"
            f"• Проверьте ваш заказ и если все верно, то разместите.\n"
            f"• Курьер может связаться с вами для уточнения деталей!\n"
            f"• Оплачивайте курьеру наличными или переводом.\n\n"
            f"⦿⌁⦿ <a href='{data['yandex_maps_url']}'>Маршрут доставки</a>\n\n"
        )


class OrderMessage

order_formatter = OrderFormatter()


__all__ = ["order_formatter"]
