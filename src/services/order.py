import io
import asyncio
from datetime import datetime
import speech_recognition as sr
from pydub import AudioSegment
from aiogram.types import Message
from aiogram.enums import ContentType
from src.config import log
from .routing import route


class OrderFormatter:
    @staticmethod
    async def _prepare_data(
        time: datetime,
        customer_name: str,
        customer_phone: str,
        city: str,
        addresses: list[str],
        delivery_object: str,
        description: str,
    ) -> dict:
        """Готовит все необходимые данные для формирования заказа и возвращает их."""

        if not addresses or addresses == "no_address":
            return {
                "city": city,
                "customer_name": customer_name,
                "customer_phone": customer_phone,
                "addresses_text": "⚠️ <b>Адреса не указаны.</b>\nСвяжитесь с заказчиком для уточнения.",
                "delivery_object": delivery_object,
                "description": description,
                "yandex_maps_url": "-",
                "distance": 0,
                "price": 0,
                "starting_point": None,
            }

        coordinates = []
        address_links = []
        formatted_addresses = []
        order_addresses_data = []

        # Обрабатываем все адреса и получаем координаты
        for address in addresses:
            coords = await route.get_coordinates(address)
            if coords:
                coordinates.append(coords)

                maps_url = f"https://maps.yandex.ru/?text={address.replace(' ', '+')}"
                address_links.append(maps_url)
                formatted_addresses.append(f"<a href='{maps_url}'>{address}</a>")
                order_addresses_data.append([coords, address])

                log.info(f"Address: {address}, Coordinates: {coords}")

            else:
                return {}

        if len(coordinates) == 1:

            yandex_maps_url = (
                f"https://maps.yandex.ru/?text={addresses[0].replace(' ', '+')}"
            )
            distance = 0
        else:

            yandex_maps_url = await route.get_rout(coordinates[0], coordinates[1:])
            distance = round(await route.calculate_total_distance(coordinates), 2)

        log.info(f"yandex_maps_url: {yandex_maps_url}")

        price = await route.get_price(
            distance,
            time,
            city=city,
        )

        # Формируем текст для отображения адресов
        addresses_text = "\n".join(
            [
                f"⦿ <b>Адрес {i + 1}:</b> {formatted_addresses[i]}"
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
            "starting_point": coordinates[0],
        }

    @staticmethod
    async def format_order_form(
        data: dict,
        discount: int = 0,
    ) -> tuple:
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
            _,
        ) = [data[key] for key in data.keys()]

        if discount:
            plus_price = int(price * 1.0)
            price = int(plus_price - discount * plus_price / 100)

        routing_addresses = (
            f"⦿⌁⦿ <a href='{yandex_maps_url}'>Маршрут заказа</a>\n\n"
            if yandex_maps_url != "-"
            else ""
        )

        additional_msg = ""

        if price == 0:
            additional_msg = f"<i>Если стоимость не указывается, то по оплате вам нужно договориться между собой.</i>\n\n"

        order_forma = (
            f"<b>Город:</b> {city}\n\n"
            f"<b>Заказчик:</b> {customer_name if customer_name else '-'}\n"
            f"<b>Телефон:</b> {customer_phone if customer_phone else '-'}\n\n"
            f"{addresses_text}\n\n"
            f"{routing_addresses}"
            f"<b>Доставляем:</b> {delivery_object if delivery_object else 'не указано'}\n"
            f"<b>Расстояние:</b> {distance} км\n"
            f"<b>Стоимость:</b> {price} ₽\n"
            f"<i>Наличными или переводом!\n\n</i>"
            f"{additional_msg}"
            f"<b>Описание:</b> {description}\n\n"
        )

        return (
            (
                order_forma,
                plus_price,
                price,
            )
            if discount
            else (order_forma,)
        )


class MessageRecognizer:

    async def get_recognition_text(self, message: Message) -> str:
        """Обрабатывает голосовое сообщение или текст и возвращает распознанный текст."""

        if message.content_type == ContentType.VOICE:
            voice = message.voice
            file_info = await message.bot.get_file(voice.file_id)
            file = await message.bot.download_file(file_info.file_path)
            audio_data = io.BytesIO(file.read())
            return await self._process_audio_data(audio_data)
        return message.text

    async def _process_audio_data(self, audio_data: bytes) -> str | bool:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._sync_recognize_audio, audio_data)

    def _sync_recognize_audio(self, audio_data: bytes) -> str | bool:
        r = sr.Recognizer()

        try:
            # ogg -> wav
            audio_segment = AudioSegment.from_file(audio_data, format="ogg")
            audio_wav = io.BytesIO()
            audio_segment.export(audio_wav, format="wav")
            audio_wav.seek(0)

            with sr.AudioFile(audio_wav) as source:
                audio = r.record(source)
                return r.recognize_google(audio, language="ru-RU")

        except (sr.UnknownValueError, sr.RequestError) as e:
            log.error(f"_sync_recognize_audio ERROR: {e}")
            return False


formatter = OrderFormatter()
recognizer = MessageRecognizer()


__all__ = ["formatter", "recognizer"]
