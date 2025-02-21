import io
import speech_recognition as sr
from pydub import AudioSegment
from aiogram.types import Message
from aiogram.enums import ContentType
from src.config import log, moscow_time
from .routing import route


class OrderFormatter:
    @staticmethod
    async def _prepare_data(
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
            coords = await route.get_coordinates(address)
            if coords:
                coordinates.append(coords)
                maps_url = f"https://maps.yandex.ru/?text={address.replace(' ', '+')}"
                address_links.append(maps_url)
                formatted_addresses.append(f"<a href='{maps_url}'>{address}</a>")
                order_addresses_data.append([coords, address])

        if len(coordinates) < 2:
            return {}

        yandex_maps_url = await route.get_rout(coordinates[0], coordinates[1:])
        distance = round(await route.calculate_total_distance(coordinates), 2)
        price = await route.get_price(distance, time)
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
            "addresses_text": addresses_text,
            "delivery_object": delivery_object,
            "description": description,
            "yandex_maps_url": yandex_maps_url,
            "distance": distance,
            "price": price,
        }

    @staticmethod
    async def format_order_form(data: dict) -> str:
        """Форматирует и возвращает текст заказа на основе подготовленных данных."""
        (
            city,
            customer_name,
            customer_phone,
            addresses_text,
            delivery_object,
            description,
            yandex_maps_url,
            distance,
            price,
        ) = [data[key] for key in data.keys()]

        order_forma = (
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
            f"⦿⌁⦿ <a href='{yandex_maps_url}'>Маршрут доставки</a>\n\n"
        )

        return order_forma


class MessageRecognizer:

    async def get_recognition_text(self, message: Message) -> str:
        """Обрабатывает голосовое сообщение или текст и возвращает распознанный текст."""

        if message.content_type == ContentType.VOICE:
            voice = message.voice
            file_info = await message.bot.get_file(voice.file_id)
            file = await message.bot.download_file(file_info.file_path)
            audio_data = io.BytesIO(file.read())  # Приведение к io.BytesIO
            return await self._process_audio_data(audio_data)  # Вызов через cls
        return message.text

    async def _process_audio_data(self, audio_data: bytes) -> str:
        """Распознаёт речь из аудиофайла."""

        r = sr.Recognizer()

        # Конвертация ogg -> wav
        audio_segment = AudioSegment.from_file(audio_data, format="ogg")
        audio_wav = io.BytesIO()
        audio_segment.export(audio_wav, format="wav")
        audio_wav.seek(0)

        with sr.AudioFile(audio_wav) as source:
            audio = r.record(source)
            try:
                return r.recognize_google(audio, language="ru-RU")
            except (
                sr.UnknownValueError,
                sr.RequestError,
            ) as e:
                log.error(f"ERROR: {e}")
                return f"Не удалось распознать речь"


formatter = OrderFormatter()
recognizer = MessageRecognizer()


__all__ = ["formatter", "recognizer"]
