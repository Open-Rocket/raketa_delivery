from .__deps__ import *

from app.customer.customer_services.coords_and_price import (
    get_coordinates,
    get_price,
)
from app.u_pack.service.u_ai_assistant import (
    process_order_text,
    get_parsed_addresses,
    assistant_censure,
)
from app.u_pack.u_states import UserState
from app.u_pack.service.u_voice_to_text import process_audio_data
from app.database.requests import user_data
from app.user.services.fuzzy_city import find_most_compatible_response
from app.u_pack.u_kb import get_user_kb


async def process_audio_message(bot, voice):
    file_info = await bot.get_file(voice.file_id)
    file = await bot.download_file(file_info.file_path)
    audio_data = file.read()
    return await process_audio_data(audio_data)


async def process_text_message(text):
    return text


async def get_order_data(recognized_text, user_city, moscow_time, message, state):
    addresses = await get_parsed_addresses(recognized_text, user_city)
    if len(addresses) == 2:
        pickup_address, delivery_address = addresses
        pickup_coords = await get_coordinates(pickup_address)
        delivery_coords = await get_coordinates(delivery_address)

        if all(pickup_coords) and all(delivery_coords):
            # Генерация ссылок для Яндекс.Карт
            yandex_maps_url = (
                f"https://yandex.ru/maps/?rtext={pickup_coords[0]},{pickup_coords[1]}"
                f"~{delivery_coords[0]},{delivery_coords[1]}&rtt=auto"
            )
            pickup_point = (
                f"https://yandex.ru/maps/?ll={pickup_coords[1]},{pickup_coords[0]}"
                f"&pt={pickup_coords[1]},{pickup_coords[0]}&z=14"
            )
            delivery_point = (
                f"https://yandex.ru/maps/?ll={delivery_coords[1]},{delivery_coords[0]}"
                f"&pt={delivery_coords[1]},{delivery_coords[0]}&z=14"
            )

            distance, duration = await calculate_osrm_route(
                *pickup_coords, *delivery_coords
            )
            price = await get_price(distance, moscow_time)
            structured_data = await process_order_text(recognized_text)

            sender_name, sender_phone = await user_data.get_username_userphone(
                message.from_user.id
            )
            structured_data.update(
                {
                    "distance_km": distance,
                    "duration_min": duration,
                    "price_rub": price,
                    "sender_name": sender_name,
                    "sender_phone": sender_phone,
                    "a_url": pickup_point,
                    "b_url": delivery_point,
                    "yandex_maps_url": yandex_maps_url,
                }
            )

            await state.update_data(structured_data)
            return structured_data

    return None


async def send_order_confirmation(message, structured_data, reply_kb):
    pickup_point = structured_data["a_url"]
    delivery_point = structured_data["b_url"]
    price_text = f"{structured_data['price_rub']}₽"
    distance_text = f"{structured_data['distance_km']} км"
    order_forma = (
        f"Ваш заказ ✍︎\n"
        f"---------------------------------------------\n"
        f"Город: {structured_data['city']}\n"
        f"⦿ Адрес 1: <a href='{pickup_point}'>{structured_data['starting_point_a']}</a>\n"
        f"⦿ Адрес 2: <a href='{delivery_point}'>{structured_data['destination_point_b']}</a>\n\n"
        f"Предмет доставки: {structured_data.get('delivery_object', ' -')}\n\n"
        f"Имя отправителя: {structured_data['sender_name']}\n"
        f"Номер отправителя: {structured_data['sender_phone']}\n"
        f"Имя получателя: {structured_data.get('receiver_name', '-')}\n"
        f"Номер получателя: {structured_data.get('receiver_phone', '-')}\n\n"
        f"Расстояние: {distance_text}\n"
        f"Стоимость доставки: {price_text}\n\n"
        f"Комментарии курьеру: {structured_data.get('comments', '-')}\n"
        f"---------------------------------------------\n"
        f"⦿⌁⦿ <a href='{structured_data['yandex_maps_url']}'>Маршрут доставки</a>\n\n"
    )
    await message.answer(
        text=order_forma,
        reply_markup=reply_kb,
        parse_mode="HTML",
        disable_notification=True,
    )


async def handle_message_content(message: Message):
    if message.content_type == ContentType.VOICE:
        return await process_audio_message(message.bot, message.voice)
    return await process_text_message(message.text)
