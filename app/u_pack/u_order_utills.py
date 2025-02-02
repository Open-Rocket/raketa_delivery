import pytz
from datetime import datetime

from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.common.coords_and_price import get_coordinates, calculate_osrm_route, get_price
from app.u_pack.u_ai_assistant import (
    process_order_text,
    get_parsed_addresses,
    assistant_censure,
)
from app.u_pack.u_states import UserState
from app.u_pack.u_voice_to_text import process_audio_data
from app.database.requests import user_data
from app.common.fuzzy_city import find_most_compatible_response
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


async def handle_censorship(recognized_text):
    censore_response = await assistant_censure(recognized_text)
    censore_data = [
        "clear",
        "overprice",
        "inaudible",
        "no_item",
        "censure",
        "not_order",
    ]
    most_compatible_response = await find_most_compatible_response(
        censore_response, censore_data
    )
    return most_compatible_response


async def handle_order_flow(message, state):
    reply_kb = await get_user_kb(text="voice_order_accept")
    moscow_time = datetime.now(pytz.timezone("Europe/Moscow")).replace(
        tzinfo=None, microsecond=0
    )
    tg_id = message.from_user.id
    user_city = await user_data.get_user_city(tg_id)

    # Обработка сообщения в зависимости от типа контента
    recognized_text = None
    if message.content_type == ContentType.VOICE:
        recognized_text = await process_audio_message(message.bot, message.voice)
    else:
        recognized_text = await process_text_message(message.text)

    if not recognized_text:
        return await message.answer(
            "Ошибка распознавания. Попробуйте снова.", reply_markup=reply_kb
        )

    # Проверка на цензуру
    most_compatible_response = await handle_censorship(recognized_text)

    if most_compatible_response == "clear":
        structured_data = await get_order_data(
            recognized_text, user_city, moscow_time, message, state
        )
        if structured_data:
            await send_order_confirmation(message, structured_data, reply_kb)
        else:
            await message.answer(
                "Не удалось получить координаты для заказа. Проверьте заказ и попробуйте снова.",
                reply_markup=reply_kb,
            )

    elif most_compatible_response == "overprice":
        await state.set_state(UserState.default)
        reply_kb = await get_user_kb(text="overprice")
        await message.answer(
            text="<b>Внимание</b>！Ваш заказ содержит табачные изделия или алкогольную продукцию. "
            "<b>Доставка будет стоить немного дороже!</b>",
            reply_markup=reply_kb,
            parse_mode="HTML",
        )

    elif most_compatible_response == "inaudible":
        await state.set_state(UserState.default)
        reply_kb = await get_user_kb(text="rerecord")
        await message.answer(
            "<b>Ошибка</b> ⸘\n\nТекст сообщения неразборчив. Попробуйте отправить заказ снова.",
            reply_markup=reply_kb,
            parse_mode="HTML",
        )

    elif most_compatible_response == "no_item":
        await state.set_state(UserState.default)
        reply_kb = await get_user_kb(text="rerecord")
        await message.answer(
            "<b>Что везем?!</b> \n\nКурьер должен знать что он доставляет.",
            reply_markup=reply_kb,
            parse_mode="HTML",
        )

    elif most_compatible_response == "not_order":
        await state.set_state(UserState.default)
        reply_kb = await get_user_kb(text="rerecord")
        await message.answer(
            "<b>...</b> 🫤 \n\nСделайте корректный заказ!",
            reply_markup=reply_kb,
            parse_mode="HTML",
        )

    else:
        await state.set_state(UserState.default)
        reply_kb = await get_user_kb(text="rerecord")
        await message.answer(
            "<b>Отказ!!!</b> 🚫\n\nМы не можем это доставлять!",
            reply_markup=reply_kb,
            parse_mode="HTML",
        )


async def handle_message_content(message: Message):
    if message.content_type == ContentType.VOICE:
        return await process_audio_message(message.bot, message.voice)
    return await process_text_message(message.text)


async def process_censorship_response(
    message: Message,
    state: FSMContext,
    most_compatible_response: str,
    recognized_text: str,
    user_city: str,
    moscow_time: datetime,
):
    if most_compatible_response == "clear":
        structured_data = await get_order_data(
            recognized_text, user_city, moscow_time, message, state
        )
        if structured_data:
            await send_order_confirmation(
                message, structured_data, await get_user_kb(text="voice_order_accept")
            )
        else:
            await message.answer(
                "Не удалось получить координаты для заказа. Проверьте заказ и попробуйте снова."
            )
    elif most_compatible_response == "overprice":
        await message.answer(
            "Ваш заказ содержит табачные изделия или алкоголь. Стоимость будет выше.",
            reply_markup=await get_user_kb(text="overprice"),
        )
    elif most_compatible_response == "inaudible":
        await message.answer(
            "Текст сообщения неразборчив. Попробуйте снова.",
            reply_markup=await get_user_kb(text="rerecord"),
        )
    elif most_compatible_response == "no_item":
        await message.answer(
            "Курьер должен знать, что доставлять. Уточните заказ.",
            reply_markup=await get_user_kb(text="rerecord"),
        )
    elif most_compatible_response == "not_order":
        await message.answer(
            "Сделайте корректный заказ.",
            reply_markup=await get_user_kb(text="rerecord"),
        )
    else:
        await message.answer(
            "Мы не можем это доставлять.",
            reply_markup=await get_user_kb(text="rerecord"),
        )


# @users_router.message(
#     filters.StateFilter(UserState.ai_voice_order),
#     F.content_type.in_([ContentType.VOICE, ContentType.TEXT])
# )
# async def process_message(message: Message, state: FSMContext):
#     await state.set_state(UserState.waiting_Courier)
#
#     censore_data = ["clear", "overprice", "inaudible", "no_item", "censure", "not_order"]
#     wait_message = await message.answer(f"Заказ обрабатывается, подождите ...", disable_notification=True)
#
#     handler = MessageHandler(state, message.bot)
#     await handler.delete_previous_message(message.chat.id)
#
#     # Инициализация переменных
#     reply_kb = await get_user_kb(text="voice_order_accept")
#     moscow_time = datetime.now(pytz.timezone("Europe/Moscow")).replace(tzinfo=None, microsecond=0)
#     tg_id = message.from_user.id
#     user_city = await user_data.get_user_city(tg_id)
#
#     recognized_text = None
#
#     # Обработка сообщения в зависимости от типа контента
#     if message.content_type == ContentType.VOICE:
#         voice = message.voice
#         file_info = await message.bot.get_file(voice.file_id)
#         file = await message.bot.download_file(file_info.file_path)
#         audio_data = file.read()
#         recognized_text = await process_audio_data(audio_data)
#     else:
#         recognized_text = message.text
#
#     # Если распознавание не удалось
#     if not recognized_text:
#         recognized_text = "Ошибка распознавания. Попробуйте снова."
#         new_message = await message.answer(recognized_text, reply_markup=reply_kb)
#         await wait_message.delete()
#         await handler.handle_new_message(new_message, message)
#         return
#
#     # Проверка текста через ассистента на цензуру
#     censore_response = await assistant_censure(recognized_text)
#     print(censore_response)
#
#
#     # Определение наибольшей совместимости ответа с возможными сценариями
#     most_compatible_response = await find_most_compatible_response(censore_response, censore_data)
#     print(most_compatible_response)
#
#     # Обработка результата цензуры по наибольшему соответствию
#     if most_compatible_response == "clear":
#         # Обработка для разрешенных заказов (обычные товары)
#         addresses = await get_parsed_addresses(recognized_text, user_city)
#         if len(addresses) == 2:
#             pickup_address, delivery_address = addresses
#             pickup_coords = await get_coordinates(pickup_address)
#             delivery_coords = await get_coordinates(delivery_address)
#
#             if all(pickup_coords) and all(delivery_coords):
#                 # Продолжение обработки заказа
#                 yandex_maps_url = (
#                     f"https://yandex.ru/maps/?rtext={pickup_coords[0]},{pickup_coords[1]}"
#                     f"~{delivery_coords[0]},{delivery_coords[1]}&rtt=auto"
#                 )
#                 pickup_point = (
#                     f"https://yandex.ru/maps/?ll={pickup_coords[1]},{pickup_coords[0]}"
#                     f"&pt={pickup_coords[1]},{pickup_coords[0]}&z=14"
#                 )
#                 delivery_point = (
#                     f"https://yandex.ru/maps/?ll={delivery_coords[1]},{delivery_coords[0]}"
#                     f"&pt={delivery_coords[1]},{delivery_coords[0]}&z=14"
#                 )
#
#                 tg_id = message.from_user.id
#                 distance, duration = await calculate_osrm_route(*pickup_coords, *delivery_coords)
#                 distance_text = f"{distance} км"
#                 duration_text = f"{(duration - duration % 60) // 60} часов {duration % 60} минут"
#                 sender_name, sender_phone = await user_data.get_username_userphone(tg_id)
#                 price = await get_price(distance, moscow_time)
#                 price_text = f"{price}₽"
#
#                 # Структурирование данных заказа
#                 structured_data = await process_order_text(recognized_text)
#                 city = structured_data.get('City')
#                 if not city:
#                     city = user_city
#                 starting_point_a = structured_data.get('Starting point A')
#                 destination_point_b = structured_data.get('Destination point B')
#                 delivery_object = structured_data.get('Delivery object')
#                 receiver_name = structured_data.get('Receiver name')
#                 receiver_phone = structured_data.get('Receiver phone')
#                 order_details = structured_data.get('Order details', None)
#                 comments = structured_data.get('Comments', None)
#
#                 # Сохранение данных в состоянии
#                 await state.update_data(
#                     city=city,
#                     starting_point_a=starting_point_a,
#                     a_latitude=float(pickup_coords[0]),
#                     a_longitude=float(pickup_coords[1]),
#                     a_coordinates=pickup_coords,
#                     a_url=pickup_point,
#                     destination_point_b=destination_point_b,
#                     b_latitude=float(delivery_coords[0]),
#                     b_longitude=float(delivery_coords[1]),
#                     b_coordinates=delivery_coords,
#                     b_url=delivery_point,
#                     delivery_object=delivery_object,
#                     sender_name=sender_name,
#                     sender_phone=sender_phone,
#                     receiver_name=receiver_name,
#                     receiver_phone=receiver_phone,
#                     order_details=order_details,
#                     comments=comments,
#                     distance_km=distance,
#                     duration_min=duration,
#                     price_rub=price,
#                     order_time=moscow_time,
#                     yandex_maps_url=yandex_maps_url,
#                     pickup_point=pickup_point,
#                     delivery_point=delivery_point,
#                 )
#
#                 # Отправка ответа пользователю
#                 order_forma = (
#                     f"Ваш заказ ✍︎\n"
#                     f"---------------------------------------------\n"
#                     f"Город: {city}\n"
#                     f"⦿ Адрес 1: <a href='{pickup_point}'>{starting_point_a}</a>\n"
#                     f"⦿ Адрес 2: <a href='{delivery_point}'>{destination_point_b}</a>\n\n"
#                     f"Предмет доставки: {delivery_object if delivery_object else ' -'}\n\n"
#                     f"Имя отправителя: {sender_name}\n"
#                     f"Номер отправителя: {sender_phone}\n"
#                     f"Имя получателя: {receiver_name if receiver_name else '-'}\n"
#                     f"Номер получателя: {receiver_phone if receiver_phone else '-'}\n\n"
#                     f"Расстояние: {distance_text}\n"
#                     f"Стоимость доставки: {price_text}\n\n"
#                     f"Комментарии курьеру: {comments if comments else '-'}\n"
#                     f"---------------------------------------------\n"
#                     f"* Проверьте ваш заказ и если все верно, то разместите.\n"
#                     f"* Курьер может связаться с вами для уточнения деталей!\n"
#                     f"* Оплачивайте курьеру наличными или переводом.\n\n"
#                     f"⦿⌁⦿ <a href='{yandex_maps_url}'>Маршрут доставки</a>\n\n"
#                 )
#                 new_message = await message.answer(
#                     text=order_forma, reply_markup=reply_kb, disable_notification=True, parse_mode="HTML"
#                 )
#
#             else:
#                 new_message = await message.answer(
#                     text=f"Не удалось получить координаты для заказа. Проверьте заказ и попробуйте снова.",
#                     reply_markup=reply_kb, disable_notification=True
#                 )
#         else:
#             new_message = await message.answer(
#                 text=f"Ваш заказ ✍︎\n\n{recognized_text}\n\nПроверьте ваш заказ и разместите его, если всё верно.",
#                 reply_markup=reply_kb, disable_notification=True
#             )
#
#     elif most_compatible_response == "overprice":
#         await state.set_state(UserState.default)
#         reply_kb = await get_user_kb(text="overprice")
#         new_message = await message.answer(
#             text=("<b>Внимание</b>！ \n\nВаш заказ содержит табачные изделия или алкогольуню продукцию.\n\n"
#                   "<b>Доставка будет стоить немного дороже!</b>"),
#             reply_markup=reply_kb, disable_notification=True, parse_mode="HTML"
#         )
#
#     elif most_compatible_response == "inaudible":
#         await state.set_state(UserState.default)
#         reply_kb = await get_user_kb(text="rerecord")
#         new_message = await message.answer(
#             text="<b>Ошибка</b> ⸘\n\nТекст сообщения неразборчив.\nПопробуйте отправить заказ снова.",
#             reply_markup=reply_kb, disable_notification=True, parse_mode="HTML"
#         )
#
#     elif most_compatible_response == "no_item":
#         await state.set_state(UserState.default)
#         reply_kb = await get_user_kb(text="rerecord")
#         new_message = await message.answer(
#             text="<b>Что везем?!</b> \n\nКурьер должен знать что он доставляет.",
#             reply_markup=reply_kb, disable_notification=True, parse_mode="HTML"
#         )
#     elif most_compatible_response == "not_order":
#         await state.set_state(UserState.default)
#         reply_kb = await get_user_kb(text="rerecord")
#         new_message = await message.answer(
#             text="<b>...</b> 🫤 \n\nСделайте корректный заказ!",
#             reply_markup=reply_kb, disable_notification=True, parse_mode="HTML"
#         )
#     else:
#         await state.set_state(UserState.default)
#         reply_kb = await get_user_kb(text="rerecord")
#         new_message = await message.answer(
#             text="<b>Отказ!!!</b> 🚫\n\nМы не можем это доставлять!",
#             reply_markup=reply_kb, disable_notification=True, parse_mode="HTML"
#         )
#
#     # Завершение обработки
#     await wait_message.delete()
#     await handler.handle_new_message(new_message, message)
