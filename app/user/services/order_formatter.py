from app.common import get_coordinates, get_price, calculate_total_distance, get_rout


class OrderFormatter:
    def __init__(
        self,
        time: str,
        city: str,
        user_name: str,
        user_phone: str,
        addresses: list[str],
        delivery_object: str,
        description: str,
    ):
        self.time = time
        self.city = city
        self.addresses = addresses
        self.delivery_object = delivery_object
        self.description = description
        self.user_name = user_name
        self.user_phone = user_phone
        self.coordinates = []
        self.address_links = []
        self.formatted_addresses = []
        self.order_addresses_data = []

    async def generate_first_order_form(self) -> str:
        """Генерирует и возвращает формат заказа."""

        if not await self._process_addresses():
            return "-"

        yandex_maps_url = await get_rout(self.coordinates[0], self.coordinates[1:])
        distance = round(await calculate_total_distance(self.coordinates), 2)
        price = await get_price(distance, self.time)

        addresses_text = "\n".join(
            [
                f"⦿ <b>Адрес {i+1}:</b> {self.formatted_addresses[i]}"
                for i in range(len(self.formatted_addresses))
            ]
        )

        return self._format_order_text(yandex_maps_url, distance, price, addresses_text)

    async def _process_addresses(self) -> bool:
        """Обрабатывает адреса: получает координаты и формирует ссылки."""

        if not self.addresses:
            return False

        for address in self.addresses:
            coords = await get_coordinates(address)
            if coords:
                self.coordinates.append(coords)
                maps_url = f"https://maps.yandex.ru/?text={address.replace(' ', '+')}"
                self.address_links.append(maps_url)
                self.formatted_addresses.append(f"<a href='{maps_url}'>{address}</a>")
                self.order_addresses_data.append([coords, address])

        return len(self.coordinates) >= 2

    def _format_order_text(
        self, yandex_maps_url, distance, price, addresses_text
    ) -> str:
        """Форматирует текст заказа."""
        return (
            f"<b>Ваш заказ</b> ✍︎\n"
            f"---------------------------------------------\n\n"
            f"<b>Город:</b> {self.city}\n\n"
            f"<b>Заказчик:</b> {self.user_name}\n"
            f"<b>Телефон:</b> {self.user_phone}\n\n"
            f"{addresses_text}\n\n"
            f"<b>Доставляем:</b> {self.delivery_object}\n"
            f"<b>Расстояние:</b> {distance} км\n"
            f"<b>Стоимость доставки:</b> {price}₽\n\n"
            f"<b>Описание:</b> {self.description}\n\n"
            f"---------------------------------------------\n"
            f"• Проверьте ваш заказ и если все верно, то разместите.\n"
            f"• Курьер может связаться с вами для уточнения деталей!\n"
            f"• Оплачивайте курьеру наличными или переводом.\n\n"
            f"⦿⌁⦿ <a href='{yandex_maps_url}'>Маршрут доставки</a>\n\n"
        )
