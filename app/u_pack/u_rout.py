# --------------------------------------------------- ✺ Start (u_rout) ✺ -------------------------------------------- #

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.enums import ContentType
from aiogram import filters

from app.common.coords_and_price import calculate_osrm_route, get_coordinates, get_price, calculate_total_distance
from app.common.fuzzy_city import find_most_compatible_response
from app.database.models import OrderStatus
from app.u_pack.u_middlewares import InnerMiddleware, OuterMiddleware
from app.u_pack.u_states import UserState
from app.u_pack.u_kb import get_user_kb, get_my_orders_kb, get_switch
from app.u_pack.u_ai_assistant import assistant_censure, process_order_text, get_parsed_addresses

from app.common.message_handler import MessageHandler
from app.common.titles import get_image_title_user

# from app.u_pack.u_order_utills import (handle_censorship, handle_message_content, process_censorship_response)

from app.database.requests import user_data, order_data

from datetime import datetime
import pytz

from app.u_pack.u_voice_to_text import process_audio_data

# ------------------------------------------------------------------------------------------------------------------- #
#                                             ⇣ Initializing Variables ⇣
# ------------------------------------------------------------------------------------------------------------------- #

users_router = Router()

# middlewares_Outer
users_router.message.outer_middleware(OuterMiddleware())
users_router.callback_query.outer_middleware(OuterMiddleware())

# middlewares_Inner
users_router.message.middleware(InnerMiddleware())
users_router.callback_query.middleware(InnerMiddleware())


# ------------------------------------------------------------------------------------------------------------------- #
#                                              ⇣ Registration steps ⇣
# ------------------------------------------------------------------------------------------------------------------- #

# start
@users_router.message(CommandStart())
async def cmd_start_user(message: Message, state: FSMContext) -> None:
    await state.set_state(UserState.reg_state)
    handler = MessageHandler(state, message.bot)
    user = await user_data.get_username_userphone(message.from_user.id)
    user_name, user_phone = user

    # Если пользователь уже зарегистрирован
    if user_name and user_phone:
        await state.set_state(UserState.default)
        await handler.delete_previous_message(message.chat.id)
        text = ("▼ <b>Выберите действие ...</b>")
        new_message = await message.answer(text)
        await handler.handle_new_message(new_message, message)
        return
    else:
        await user_data.set_user(message.from_user.id)
        await handler.delete_previous_message(message.chat.id)
        photo_title = await get_image_title_user("/start")
        text = (f"Raketa — современный сервис доставки с минимальными ценами и удобством использования.\n\n"
                f"Почему выбирают нас?\n\n"
                f"◉ Низкие цены:\n"
                f"Наши пешие курьеры находятся рядом с вами, что снижает стоимость и ускоряет доставку.\n\n"
                f"◉ Простота и удобство:\n"
                f"С помощью технологий ИИ вы можете быстро оформить заказ и сразу отправить его на выполнение.")
        reply_kb = await get_user_kb(message)

        new_message = await message.answer_photo(photo=photo_title,
                                                 caption=text,
                                                 reply_markup=reply_kb,
                                                 parse_mode="HTML",
                                                 disable_notification=True)
        await handler.handle_new_message(new_message, message)


# registration_Name
@users_router.callback_query(F.data == "reg")
async def data_reg_user(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.reg_Name)
    handler = MessageHandler(state, callback_query.bot)
    # text = "Пройдите небольшую регистрацию, это не займет много времени.\n\n"
    # await callback_query.answer(text, show_alert=True)
    text = ("Пройдите небольшую регистрацию.\n"
            "Это не займет много времени.\n\n"
            "<b>Как вас зовут?</b>")
    new_message = await callback_query.message.answer(text, disable_notification=True, parse_mode="HTML")
    await handler.handle_new_message(new_message, callback_query.message)


# registration_Phone
@users_router.message(filters.StateFilter(UserState.reg_Name))
async def data_name_user(message: Message, state: FSMContext):
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)

    tg_id = message.from_user.id
    name = message.text
    if len(name) > 42:
        text = (f"Слишком длинное имя!\n\n"
                f"<b>Введите имя еще раз:</b>")
        msg = await message.answer(text, disable_notification=True, parse_mode="HTML")
    else:
        await state.set_state(UserState.reg_Phone)
        await user_data.set_user_name(tg_id, name)
        reply_kb = await get_user_kb(text="phone_number")
        text = (f"Привет, {name}!👋\n\nЧтобы мы могли быстро оформить заказ и курьер смог связаться с вами "
                f"в случае необходимости, пожалуйста, укажите ваш номер телефона.\n\n"
                f"<i>*При регистрации с компьютера нажмите на значек команд рядом с полем ввода.</i>\n\n"
                f"<b>Ваш номер:</b>")

        msg = await message.answer(text, disable_notification=True, reply_markup=reply_kb, parse_mode="HTML")
    await handler.handle_new_message(msg, message)


# registration_City
@users_router.message(filters.StateFilter(UserState.reg_Phone))
async def data_phone_user(message: Message, state: FSMContext):
    await state.set_state(UserState.reg_City)
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)

    tg_id = message.from_user.id
    phone = message.contact.phone_number

    await user_data.set_user_phone(tg_id, phone)
    text = (f"Последний шаг!\n\n"
            f"Для того чтобы каждый раз не указывать город доставки, "
            f"скажите в каком городе вы будете в основном делать заказы "
            f"и он автоматически будет подставляться.\n\n"
            f"<b>Ваш город:</b>")
    msg = await message.answer(text, disable_notification=True, parse_mode="HTML")
    await handler.handle_new_message(msg, message)


# terms of use
@users_router.message(filters.StateFilter(UserState.reg_City))
async def data_city_user(message: Message, state: FSMContext):
    await state.set_state(UserState.reg_tou)
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)

    tg_id = message.from_user.id
    city = message.text

    await user_data.set_user_city(tg_id, city)
    reply_kb = await get_user_kb(text="accept_tou")
    text = (f"Начиная использование сервиса, вы соглашаетесь с "
            f"<a href='https://drive.google.com/file/d/1iKhjWckZhn54aYWjDFLQXL46W6J0NhhC/view?usp=sharing'>"
            f"Пользовательским соглашением и правилами использования</a>, а также "
            f"<a href='https://telegram.org/privacy'>Политикой конфиденциальности</a>.\n\n"
            f"<i>*Обращаем внимание, что любые действия, связанные с заказами, "
            f"отправкой или получением посылок, должны соответствовать законодательству "
            f"вашего государства и общепринятым этическим нормам.</i>\n\n"
            )
    new_message = await message.answer(text, reply_markup=reply_kb, disable_notification=True, parse_mode="HTML")
    await handler.handle_new_message(new_message, message)


@users_router.callback_query(F.data == "accept_tou")
async def user_accept_tou(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.default)
    handler = MessageHandler(state, callback_query.bot)

    tg_id = callback_query.from_user.id
    accept_tou = "Пользовательское соглашение и правила использования сервиса - Принимаю"
    await user_data.set_user_accept_tou(tg_id, accept_tou)
    name, phone_number, city = await user_data.get_user_info(tg_id)
    text = ("Вы успешно зарегистрировались! 🎉\n\n"
            f"Имя: {name}\n"
            f"Номер: {phone_number}\n"
            f"Город: {city}\n\n"
            f"▼ <b>Выберите действие ...</b>"
            )
    new_message = await callback_query.message.answer(text, disable_notification=True, parse_mode="HTML")
    await handler.handle_new_message(new_message, callback_query.message)


# ------------------------------------------------------------------------------------------------------------------- #
#                                                    ⇣ Bot functions ⇣
# ------------------------------------------------------------------------------------------------------------------- #


# commands_Profile
@users_router.message(F.text == "/profile")
async def cmd_profile(message: Message, state: FSMContext):
    await state.set_state(UserState.default)
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)
    tg_id = message.from_user.id
    await get_image_title_user(message.text)
    name, phone_number, city = await user_data.get_user_info(tg_id)

    text = (f"👥 <b>Профиль</b>\n\n"
            f"Посмотрите или измените данные о себе.\n\n"
            f"• Номер нужен для связи с курьером.\n"
            f"• Город подставляется в заказ.\n\n"
            f"<i>*При заказе в другом городе укажите его в описании к заказу.</i>\n\n"
            f"<b>Имя:</b> {name} \n"
            f"<b>Номер:</b> {phone_number}\n"
            f"<b>Город:</b> {city}")
    reply_kb = await get_user_kb(message=message)

    new_message = await message.answer(text,
                                       reply_markup=reply_kb,
                                       disable_notification=True,
                                       parse_mode="HTML")
    await handler.handle_new_message(new_message, message)


# faq
@users_router.message(F.text == "/faq")
async def cmd_faq(message: Message, state: FSMContext):
    await state.set_state(UserState.default)
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)

    text = (f"🤔 <b>Вопросы и ответы</b>\n\n"
            f"Частые вопросы и ответы на них "
            f"<a href='https://drive.google.com/file/d/1cXYK_FqU7kRpTU9p04dVjcE4vRbmNvMw/view?usp=sharing'>FAQ</a>")

    new_message = await message.answer(text, disable_notification=True, parse_mode="HTML")
    await handler.handle_new_message(new_message, message)

# rules
@users_router.message(F.text == "/rules")
async def cmd_rules(message: Message, state: FSMContext):
    await state.set_state(UserState.default)
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)

    text = (f"⚖️ <b>Правила сервиса</b>\n\n"
            f"Начиная использование сервиса, вы соглашаетесь с "
            f"<a href='https://drive.google.com/file/d/1iKhjWckZhn54aYWjDFLQXL46W6J0NhhC/view?usp=sharing'>"
            f"Пользовательским соглашением и правилами использования</a>, а также "
            f"<a href='https://telegram.org/privacy'>Политикой конфиденциальности</a>.\n\n"
            f"<i>*Обращаем внимание, что любые действия, связанные с заказами, "
            f"отправкой или получением посылок, должны соответствовать законодательству "
            f"вашего государства и общепринятым этическим нормам.</i>\n\n"
            )

    new_message = await message.answer(text, disable_notification=True, parse_mode="HTML")
    await handler.handle_new_message(new_message, message)


# commands_BecomeCourier
@users_router.message(F.text == "/become_courier")
async def cmd_become_courier(message: Message, state: FSMContext):
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)
    photo_title = await get_image_title_user("/become_courier")
    text = ("⦿ Стать курьером у нас — это отличный способ заработать без комиссии!\n\n"
            "⦿ Работайте в удобное время, выбирайте заказы рядом и получайте бонусы за быструю доставку.\n\n"
            "⦿ Прокачивайте профиль, повышайте рейтинг и зарабатывайте от 3000₽ до 5000₽ в день уже сегодня!")
    reply_kb = await get_user_kb(message)
    new_message = await message.answer_photo(photo=photo_title,
                                             caption=text,
                                             reply_markup=reply_kb,
                                             disable_notification=True)

    await handler.handle_new_message(new_message, message)


@users_router.message(F.text == "/order")
async def cmd_order(message: Message, state: FSMContext):
    data = await state.get_data()
    read_info = data.get("read_info", False)  # Извлекаем флаг или устанавливаем False по умолчанию

    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)

    if not read_info:
        await state.set_state(UserState.default)
        # Отправляем инструкцию пользователю
        photo_title = await get_image_title_user(message.text)
        text = ("◉ Вы можете сделать заказ с помощью текста или голоса, "
                "и наш ИИ ассистент быстро его обработает и передаст курьеру.\n\n"
                "<i>*При записи голосового сообщения или набора текста описывайте заказ так, как вам удобно, "
                "ассистент создаст заявку для вашего заказа.</i>")
        reply_kb = await get_user_kb(message)

        new_message = await message.answer_photo(photo=photo_title,
                                                 caption=text,
                                                 reply_markup=reply_kb,
                                                 disable_notification=True,
                                                 parse_mode="HTML")


    else:
        await state.update_data(read_info=True)
        await state.set_state(UserState.ai_voice_order)
        text = ("✔︎ <b>Укажите в описании к заказу:</b>\n\n"
                "<b>Город:</b> <i>*если нужно</i>\n"
                "<b>Адреса доставки:</b> <i>*обязательно</i>\n"
                "<b>Предмет доставки:</b> <i>*обязательно</i>\n"
                "<b>Имя получателя:</b> <i>*желательно</i>\n"
                "<b>Номер получателя:</b> <i>*желательно</i>\n"
                "<b>Комментарии курьеру:</b> <i>*если нужно</i>\n\n"
                "<i>*Вы можете отрпвить как голосовое сообщение так и текстовое, "
                "заказ будет оформлен в считанные секунды.</i>")

        new_message = await message.answer(text=f"{text}\n\nゞ <b>Опишите ваш заказ ...</b>",
                                           disable_notification=True,
                                           parse_mode="HTML")

    # Обрабатываем новое сообщение
    await handler.handle_new_message(new_message, message)


# read_Info
@users_router.callback_query(F.data == "ai_order")
async def data_ai(callback_query: CallbackQuery, state: FSMContext):
    # Устанавливаем нужный стейт
    await state.set_state(UserState.ai_voice_order)
    # Устанавливаем флаг прочитанной информации
    await state.update_data(read_info=True)

    handler = MessageHandler(state, callback_query.bot)
    text = ("✔︎ <b>Укажите в описании к заказу:</b>\n\n"
            "<b>Город:</b> <i>*если нужно</i>\n"
            "<b>Адреса доставки:</b> <i>*обязательно</i>\n"
            "<b>Предмет доставки:</b> <i>*обязательно</i>\n"
            "<b>Имя получателя:</b> <i>*желательно</i>\n"
            "<b>Номер получателя:</b> <i>*желательно</i>\n"
            "<b>Комментарии курьеру:</b> <i>*если нужно</i>\n\n"
            "<i>*Вы можете отправить как голосовое сообщение так и текстовое, "
            "заказ будет оформлен в считанные секунды.</i>")

    new_message = await callback_query.message.answer(text=f"{text}\n\nゞ <b>Опишите ваш заказ ...</b>",
                                                      disable_notification=True,
                                                      parse_mode="HTML")
    await handler.handle_new_message(new_message, callback_query.message)


# cancel_Order
@users_router.callback_query(F.data == "cancel_order")
async def cancel_order(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.default)
    handler = MessageHandler(state, callback_query.bot)
    text = "▼ <b>Выберите действие ...</b>"
    new_message = await callback_query.message.answer(text, disable_notification=True, parse_mode="HTML")
    await handler.handle_new_message(new_message, callback_query.message)


@users_router.callback_query(F.data == "set_my_name")
async def set_name(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.change_Name)
    handler = MessageHandler(state, callback_query.bot)
    text = (f"Изменить данные профиля.\n\n"
            f"<b>Ваше имя:</b>")
    new_message = await callback_query.message.answer(text, disable_notification=True, parse_mode="HTML")
    await handler.handle_new_message(new_message, callback_query.message)


@users_router.callback_query(F.data == "set_my_phone")
async def set_phone(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.change_Phone)
    handler = MessageHandler(state, callback_query.bot)
    reply_kb = await get_user_kb(text="phone_number")
    text = (f"Изменить данные профиля.\n\n"
            f"<b>Ваш Телефон:</b>")
    new_message = await callback_query.message.answer(text,
                                                      disable_notification=True,
                                                      reply_markup=reply_kb,
                                                      parse_mode="HTML")
    await handler.handle_new_message(new_message, callback_query.message)


@users_router.callback_query(F.data == "set_my_city")
async def set_phone(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.change_City)
    handler = MessageHandler(state, callback_query.bot)
    text = (f"Изменить данные профиля.\n\n"
            f"<b>Ваш город:</b>")
    new_message = await callback_query.message.answer(text,
                                                      disable_notification=True,
                                                      parse_mode="HTML")
    await handler.handle_new_message(new_message, callback_query.message)


@users_router.message(filters.StateFilter(UserState.change_Name))
async def change_name(message: Message, state: FSMContext):
    await state.set_state(UserState.default)
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)

    tg_id = message.from_user.id
    name = message.text

    await user_data.set_user_name(tg_id, name)
    text = (f"Имя было изменено на {name} 🎉\n\n"
            f"▼ <b>Выберите действие ...</b>")
    new_message = await message.answer(text, disable_notification=True, parse_mode="HTML")

    await handler.handle_new_message(new_message, message)


@users_router.message(filters.StateFilter(UserState.change_Phone))
async def change_phone(message: Message, state: FSMContext):
    await state.set_state(UserState.default)
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)

    tg_id = message.from_user.id
    phone = message.contact.phone_number

    await user_data.set_user_phone(tg_id, phone)
    text = (f"Номер был изменено на {phone} 🎉\n\n"
            f"▼ <b>Выберите действие ...</b>")
    new_message = await message.answer(text, disable_notification=True, parse_mode="HTML")

    await handler.handle_new_message(new_message, message)


@users_router.message(filters.StateFilter(UserState.change_City))
async def change_name(message: Message, state: FSMContext):
    await state.set_state(UserState.default)
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)

    tg_id = message.from_user.id
    city = message.text

    await user_data.set_user_city(tg_id, city)
    text = (f"Город был изменен на {city} 🎉\n\n"
            f"▼ <b>Выберите действие ...</b>")
    new_message = await message.answer(text, disable_notification=True, parse_mode="HTML")

    await handler.handle_new_message(new_message, message)


# ------------------------------------------------------------------------------------------------------------------- #
#                                                   ⇣ User orders ⇣
# ------------------------------------------------------------------------------------------------------------------- #


@users_router.message(F.text == "/my_orders")
@users_router.callback_query(F.data == "back_myOrders")
async def handle_my_orders(event, state: FSMContext):
    is_callback = isinstance(event, CallbackQuery)
    user_tg_id = event.from_user.id
    chat_id = event.message.chat.id if is_callback else event.chat.id
    bot = event.message.bot if is_callback else event.bot

    if not is_callback:
        handler = MessageHandler(state, bot)
        await handler.delete_previous_message(chat_id)

    await state.set_state(UserState.myOrders)

    pending_count = len(await order_data.get_pending_orders(user_tg_id))
    active_count = len(await order_data.get_active_orders(user_tg_id))
    canceled_count = len(await order_data.get_canceled_orders(user_tg_id))
    completed_count = len(await order_data.get_completed_orders(user_tg_id))

    reply_kb = await get_my_orders_kb(pending_count, active_count, canceled_count, completed_count)
    text = (f"✎ <b>Мои заказы</b>\n\n"
            f"Здесь вы можете посмотреть статус ваших заказов, "
            f"а также статистику за все время использования нашего сервиса.\n\n"
            f"<b>Статус ваших заказов:</b>")

    if is_callback:
        new_message = await event.message.edit_text(text,
                                                    reply_markup=reply_kb,
                                                    disable_notification=True,
                                                    parse_mode="HTML")
    else:
        new_message = await event.answer(text,
                                         reply_markup=reply_kb,
                                         disable_notification=True,
                                         parse_mode="HTML")

    # Если это сообщение, вызываем delete
    if not is_callback:
        handler = MessageHandler(state, bot)
        await handler.handle_new_message(new_message, event)
    else:
        await event.answer()


@users_router.callback_query(F.data.in_({"pending_orders", "active_orders", "canceled_orders",
                                         "completed_orders", "next_order", "prev_order"}))
async def get_orders(callback_query: CallbackQuery, state: FSMContext):
    # Если пользователь листает заказы (вперёд или назад)
    data = await state.get_data()

    if callback_query.data == "next_order" or callback_query.data == "prev_order":
        counter = data.get('counter', 0)
        total_orders = len(data.get('orders_text', []))

        if callback_query.data == "next_order":
            counter = (counter + 1) % total_orders  # Циклический переход к следующему заказу
        elif callback_query.data == "prev_order":
            counter = (counter - 1) % total_orders  # Циклический переход к предыдущему заказу

        await state.update_data(counter=counter)
        orders_text = data.get('orders_text', [])
        reply_kb = await get_user_kb(text="one_my_order")
        await callback_query.message.edit_text(
            orders_text[counter],
            reply_markup=reply_kb,
            parse_mode="HTML",
            disable_notification=True
        )
        return

    # Основная логика получения заказов
    order_type = callback_query.data
    user_tg_id = callback_query.from_user.id

    if order_type == "pending_orders":
        user_orders = await order_data.get_pending_orders(user_tg_id)
        await state.set_state(UserState.myOrders_pending)
        keyboard_type = "pending_orders"
        status_text = "ожидающих"
    elif order_type == "active_orders":
        user_orders = await order_data.get_active_orders(user_tg_id)
        await state.set_state(UserState.myOrders_active)
        keyboard_type = "active_orders"
        status_text = "активных"
    elif order_type == "canceled_orders":
        user_orders = await order_data.get_canceled_orders(user_tg_id)
        await state.set_state(UserState.myOrders_canceled)
        keyboard_type = "canceled_orders"
        status_text = "отмененных"
    elif order_type == "completed_orders":
        user_orders = await order_data.get_completed_orders(user_tg_id)
        await state.set_state(UserState.myOrders_completed)
        keyboard_type = "completed_orders"
        status_text = "завершенных"

    orders_dict = {order.order_id: order for order in user_orders}
    await state.update_data(orders=orders_dict)

    def format_address(number, address, name, phone, url):
        return (
            f"⦿ <b>Адрес {number}:</b> <a href='{url}'>{address}</a>\n"
            f"<b>Имя:</b> {name if name else '-'}\n"
            f"<b>Телефон:</b> {phone if phone else '-'}\n\n"
        )

    orders_text = []
    for order in user_orders:
        base_info = (
            f"{user_orders.index(order) + 1}/{len(user_orders)}\n\n"
            f"<b>Заказ №{order.order_id}</b>\n"
            f"<b>Дата оформления:</b> {order.created_at_moscow_time}\n"
            f"<b>Статус заказа:</b> {order.order_status.value}\n"
            f"---------------------------------------------\n"
            f"<b>Город:</b> {order.order_city}\n\n"
            f"{format_address(1, order.starting_point_a, order.sender_name, order.sender_phone, order.a_url)}"
        )

        if order.destination_point_b:
            base_info += format_address(2, order.destination_point_b,
                                        order.receiver_name_1,
                                        order.receiver_phone_1,
                                        order.b_url)
        if order.destination_point_c:
            base_info += format_address(3, order.destination_point_c,
                                        order.receiver_name_2,
                                        order.receiver_phone_2,
                                        order.c_url)
        if order.destination_point_d:
            base_info += format_address(4, order.destination_point_d,
                                        order.receiver_name_3,
                                        order.receiver_phone_3,
                                        order.d_url)
        if order.destination_point_e:
            base_info += format_address(5, order.destination_point_e,
                                        order.receiver_name_4,
                                        order.receiver_phone_4,
                                        order.e_url)

        counter = 0
        current_order_id = user_orders[counter].order_id
        courier_name, courier_phone = await order_data.get_order_courier_info(current_order_id)
        base_info += (
            f"<b>Доставляем:</b> {order.delivery_object if order.delivery_object else '-'}\n\n"
            f"<b>Расстояние:</b> {order.distance_km} км\n"
            f"<b>Стоимость доставки:</b> {order.price_rub}₽\n"
            f"---------------------------------------------\n"
            f"✰ <b>Курьер</b>\n"
            f"Имя: {courier_name}\n"
            f"Номер: {courier_phone}\n"
            f"---------------------------------------------\n"
            f"<b>Комментарии:</b> <i>{'*'}{order.comments if order.comments else '...'}</i>\n\n"
            f"⦿⌁⦿ <a href='{order.full_rout}'>Маршрут</a>\n\n"
        )

        orders_text.append(base_info)

    if not orders_text:
        handler = MessageHandler(state, callback_query.message)
        await handler.delete_previous_message(callback_query.message.chat.id)
        text = f"У вас нет {status_text} заказов."
        reply_kb = await get_user_kb(text="one_my_order")
        await callback_query.message.edit_text(text,
                                               reply_markup=reply_kb,
                                               disable_notification=True)
        return

    await state.update_data(orders_text=orders_text, counter=counter, current_order_id=current_order_id)

    if order_type == "pending_orders":
        reply_kb = await get_user_kb(text="one_my_pending" if len(orders_text) == 1 else keyboard_type)
    else:
        reply_kb = await get_user_kb(text="one_my_order" if len(orders_text) == 1 else keyboard_type)

    await callback_query.message.edit_text(orders_text[counter], reply_markup=reply_kb,
                                           parse_mode="HTML",
                                           disable_notification=True)


@users_router.callback_query(F.data == "my_statistic")
async def get_my_statistic(callback_query: CallbackQuery, state: FSMContext):
    user_tg_id = callback_query.from_user.id

    # Получение статистики пользователя
    total_orders = await order_data.get_total_orders(user_tg_id) or 0
    completed_orders = await order_data.get_completed_orders_count(user_tg_id) or 0
    canceled_orders = await order_data.get_canceled_orders_count(user_tg_id) or 0
    avg_speed = await order_data.get_avg_order_speed(user_tg_id) or 0
    avg_distance = await order_data.get_avg_order_distance(user_tg_id) or 0
    fastest_order_speed = await order_data.get_fastest_order_speed(user_tg_id) or 0
    slowest_order_speed = await order_data.get_slowest_order_speed(user_tg_id) or 0
    avg_time = await order_data.get_avg_order_time(user_tg_id) or 0
    fastest_order_time = await order_data.get_fastest_order_time(user_tg_id) or 0
    longest_order_time = await order_data.get_longest_order_time(user_tg_id) or 0
    shortest_order_distance = await order_data.get_shortest_order_distance(user_tg_id) or 0
    longest_order_distance = await order_data.get_longest_order_distance(user_tg_id) or 0

    # Если заказов нет, то процент успешных заказов будет 0
    success_rate = (completed_orders / total_orders) * 100 if total_orders > 0 else 0

    avg_price = await order_data.get_avg_order_price(user_tg_id) or 0
    max_price = await order_data.get_max_order_price(user_tg_id) or 0
    min_price = await order_data.get_min_order_price(user_tg_id) or 0

    # Формирование текста для сообщения
    text = (
        f"☈ <b>Статистика заказов</b>\n\n"
        f"Всего заказов: {total_orders}\n"
        f"Выполненные: {completed_orders}\n"
        f"Отмененные: {canceled_orders}\n\n"
        f"Самый медленный (по скорости): {slowest_order_speed:.2f} км/ч\n"
        f"Самый быстрый (по скорости): {fastest_order_speed:.2f} км/ч\n"
        f"Средняя скорость выполнения: {avg_speed:.2f} км/ч\n\n"
        f"Самый долгий: {longest_order_time:.2f} мин\n"
        f"Самый быстрый (по времени): {fastest_order_time:.2f} мин\n"
        f"Среднее время выполнения: {avg_time:.2f} мин\n\n"
        f"Самое короткое расстояние: {shortest_order_distance:.2f} км\n"
        f"Самое большое расстояние: {longest_order_distance:.2f} км\n"
        f"Среднее расстояние: {avg_distance:.2f} км\n\n"
        f"Наименьшая стоимость: {min_price:.2f} руб.\n"
        f"Наибольшая стоимость: {max_price:.2f} руб.\n"
        f"Средняя стоимость: {avg_price:.2f} руб.\n\n"
        f"Процент успешных: {success_rate:.2f}%\n"

    )

    reply_kb = await get_user_kb(text="one_my_order")

    # Отправка сообщения пользователю
    await callback_query.message.edit_text(text,
                                           reply_markup=reply_kb,
                                           parse_mode="HTML")


# Обработчик кнопки "⇥" для перехода вперёд
@users_router.callback_query(F.data == "next_right_mo")
async def on_button_next_my_orders(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    orders_text = data.get("orders_text")
    orders = data.get("orders")  # Словарь с заказами
    counter = data.get("counter", 0)

    # Увеличиваем счетчик и зацикливаем его
    counter = (counter + 1) % len(orders_text)

    # Обновляем состояние с новым значением счетчика и ID текущего заказа
    current_order_id = list(orders.keys())[counter]  # Получаем ID нового активного заказа
    await state.update_data(counter=counter, current_order_id=current_order_id)

    # Обновляем сообщение с новым заказом
    new_order_info = orders_text[counter]
    await callback_query.message.edit_text(new_order_info,
                                           reply_markup=callback_query.message.reply_markup,
                                           parse_mode="HTML")


# Обработчик кнопки "⇤" для перехода назад
@users_router.callback_query(F.data == "back_left_mo")
async def on_button_back_my_orders(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    orders_text = data.get("orders_text")
    orders = data.get("orders")
    counter = data.get("counter", 0)

    # Уменьшаем счетчик и зацикливаем его
    counter = (counter - 1) % len(orders_text)

    # Обновляем состояние с новым значением счетчика
    current_order_id = list(orders.keys())[counter]
    await state.update_data(counter=counter, current_order_id=current_order_id)

    # Обновляем сообщение с новым заказом
    new_order_info = orders_text[counter]
    await callback_query.message.edit_text(new_order_info,
                                           reply_markup=callback_query.message.reply_markup,
                                           parse_mode="HTML")


# ------------------------------------------------------------------------------------------------------------------- #
#                                                   ⇣ Cancel order ⇣
# ------------------------------------------------------------------------------------------------------------------- #
@users_router.callback_query(F.data == "cancel_my_order")
async def cancel_order(callback_query: CallbackQuery, state: FSMContext):
    handler = MessageHandler(state, callback_query.message.bot)
    data = await state.get_data()
    current_order_id = data.get("current_order_id")  # Получаем ID текущего заказа

    if not current_order_id:
        await callback_query.message.answer("Не удалось найти заказ для отмены.")
        return

    order = await order_data.get_order_by_id(current_order_id)

    if order.order_status != OrderStatus.PENDING:
        new_message = await callback_query.message.answer(
            f"Заказ №{current_order_id} нельзя отменить, так как он не в статусе ожидания.")
        return

    await order_data.update_order_status(current_order_id, OrderStatus.CANCELLED)
    text = (f"<b>Заказ №{current_order_id} успешно отменен.</b>\n\n"
            # f"<i>*Вы можете отменить заказ до того как курьер его принял и начал выполнять!</i>\n"
            f"<i>*Посмотреть информацию вы можете в своих заказах в пункте</i> <b>Отмененные.</b>\n\n"
            f"▼ <b>Выберите действие ...</b>")
    new_message = await callback_query.message.answer(text,
                                                      disable_notification=True,
                                                      parse_mode="HTML")

    await handler.handle_new_message(new_message, callback_query.message)


# ------------------------------------------------------------------------------------------------------------------- #
#                                            ⇣ Test courier orders list vision ⇣
# ------------------------------------------------------------------------------------------------------------------- #


# test
@users_router.message(F.text == "/test")
async def send_orders(message: Message, state: FSMContext):
    await state.set_state(UserState.testOrders)

    handler = MessageHandler(state, message.bot)
    my_tg_id = message.from_user.id
    my_lon = 37.483554  # пример координат курьера
    my_lat = 55.680241  # пример координат курьера
    available_orders = await order_data.get_available_orders(my_tg_id, my_lat, my_lon, radius_km=5)

    # Функция для формирования адреса и информации о получателе
    def format_address(number, address, name, phone, url):
        return (
            f"⦿ Адрес {number}: <a href='{url}'>{address}</a>\n"
            f"Имя: {name if name else '-'}\n"
            f"Телефон: {phone if phone else '-'}\n\n"
        )

    # -------------------- Формируем список заказов для отображения -------------------- #
    orders = []
    for order in available_orders:
        base_info = (
            f"Заказов рядом: {len(available_orders)}\n\n"
            f"Заказ №{order.order_id}\n"
            f"Дата оформления: {order.created_at_moscow_time}\n"
            f"Статус заказа: {order.order_status.value}\n"
            f"---------------------------------------------\n"
            f"Город: {order.order_city}\n\n"
            f"{format_address(1, order.starting_point_a, order.sender_name, order.sender_phone, order.a_url)}"
        )

        # Динамическое добавление адресов до 5-ти
        if order.destination_point_b:
            base_info += format_address(2, order.destination_point_b,
                                        order.receiver_name_1,
                                        order.receiver_phone_1,
                                        order.b_url)

        if order.destination_point_c:
            base_info += format_address(3, order.destination_point_c,
                                        order.receiver_name_2,
                                        order.receiver_phone_2,
                                        order.c_url)

        if order.destination_point_d:
            base_info += format_address(4, order.destination_point_d,
                                        order.receiver_name_3,
                                        order.receiver_phone_3,
                                        order.d_url)

        if order.destination_point_e:
            base_info += format_address(5, order.destination_point_e,
                                        order.receiver_name_4,
                                        order.receiver_phone_4,
                                        order.e_url)

        # Дополнительная информация о заказе
        base_info += (
            f"Доставляем: {order.delivery_object if order.delivery_object else '-'}\n\n"
            f"Расстояние: {order.distance_km} км\n"
            f"Оплата: {order.price_rub}₽\n"
            f"* Принимайте оплату наличными или переводом.\n"
            f"---------------------------------------------\n"
            f"Комментарии: {order.comments if order.comments else '-'}\n\n"
            f"⦿⌁⦿ <a href='{order.full_rout}'>Маршрут</a>\n\n"
        )

        orders.append(base_info)

    # -------------------- Если заказов нет -------------------- #
    if not orders:
        await handler.delete_previous_message(message.chat.id)
        new_message = await message.answer("Нет доступных заказов в вашем радиусе.")
        await handler.handle_new_message(new_message, message)
        return

    await handler.delete_previous_message(message.chat.id)

    # -------------------- Устанавливаем начальный заказ и сохраняем его -------------------- #
    counter = 0
    await state.update_data(orders=orders, counter=counter)

    reply_kb = await get_user_kb(text="one_order" if len(orders) == 1 else message.text)
    new_message = await message.answer(orders[counter], reply_markup=reply_kb,
                                       parse_mode="HTML",
                                       disable_notification=True)
    await handler.handle_new_message(new_message, message)

    # -------------- Finish -------------- #


# Обработчик кнопки "⇥" для перехода вперёд
@users_router.callback_query(F.data == "next_right")
async def on_button_next(callback_query: CallbackQuery, state: FSMContext):
    handler = MessageHandler(state, callback_query.bot)
    await state.set_state(UserState.testOrders)
    data = await state.get_data()
    orders = data.get("orders")
    counter = data.get("counter", 0)

    # Увеличиваем счётчик и зацикливаем его
    counter = (counter + 1) % len(orders)

    # Обновляем состояние с новым значением счётчика
    await state.update_data(counter=counter)

    # Обновляем сообщение с новым заказом
    await callback_query.message.edit_text(orders[counter],
                                           reply_markup=callback_query.message.reply_markup,
                                           parse_mode="HTML")


# Обработчик кнопки "⇤" для перехода назад
@users_router.callback_query(F.data == "back_left")
async def on_button_back(callback_query: CallbackQuery, state: FSMContext):
    handler = MessageHandler(state, callback_query.bot)
    await state.set_state(UserState.testOrders)
    data = await state.get_data()
    orders = data.get("orders")
    counter = data.get("counter", 0)

    # Уменьшаем счётчик и зацикливаем его
    counter = (counter - 1) % len(orders)

    # Обновляем состояние с новым значением счётчика
    await state.update_data(counter=counter)

    # Обновляем сообщение с новым заказом
    await callback_query.message.edit_text(
        orders[counter],
        reply_markup=callback_query.message.reply_markup,
        parse_mode="HTML"
    )




# ------------------------------------------------------------------------------------------------------------------- #
#                                                 ⇣ Assistant test ⇣
# ------------------------------------------------------------------------------------------------------------------- #


# assistant
@users_router.message(F.text == "/ai")
async def cmd_ai(message: Message, state: FSMContext):
    await state.set_state(UserState.assistant_run)
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)
    text = ("Задайте свой вопрос ИИ ассистенту ...")
    new_message = await message.answer(text, disable_notification=True)
    await handler.handle_new_message(new_message, message)


@users_router.message(filters.StateFilter(UserState.assistant_run))
async def ai_answer(message: Message, state: FSMContext):
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)
    user_message = message.text
    assistant_response = await assistant_censure(req=user_message)
    new_message = await message.answer(assistant_response, disable_notification=True)
    await handler.handle_new_message(new_message, message)


# ------------------------------------------------------------------------------------------------------------------- #
#                                               ⇣ Formation of an order ⇣
# ------------------------------------------------------------------------------------------------------------------- #


# form_Order
@users_router.message(
    filters.StateFilter(UserState.ai_voice_order),
    F.content_type.in_([ContentType.VOICE, ContentType.TEXT])
)
async def process_message(message: Message, state: FSMContext):
    await state.set_state(UserState.waiting_Courier)

    censore_data = ["clear", "overprice", "inaudible", "no_item", "censure", "not_order", "intercity"]
    wait_message = await message.answer(f"Заказ обрабатывается, подождите ...", disable_notification=True)

    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)

    # Инициализация переменных
    reply_kb = await get_user_kb(text="voice_order_accept")
    moscow_time = datetime.now(pytz.timezone("Europe/Moscow")).replace(tzinfo=None, microsecond=0)
    tg_id = message.from_user.id
    user_city = await user_data.get_user_city(tg_id)
    new_message = "Ошибка распознавания. Попробуйте снова."

    recognized_text = None

    # Обработка сообщения в зависимости от типа контента
    if message.content_type == ContentType.VOICE:
        voice = message.voice
        file_info = await message.bot.get_file(voice.file_id)
        file = await message.bot.download_file(file_info.file_path)
        audio_data = file.read()
        recognized_text = await process_audio_data(audio_data)
    else:
        recognized_text = message.text

    # Если распознавание не удалось
    if not recognized_text:
        recognized_text = new_message
        new_message = await message.answer(recognized_text, reply_markup=reply_kb)
        await wait_message.delete()
        await handler.handle_new_message(new_message, message)
        return

    # Проверка текста через ассистента на цензуру
    censore_response = await assistant_censure(recognized_text)
    # print(censore_response)

    # Определение наибольшей совместимости ответа с возможными сценариями
    most_compatible_response = await find_most_compatible_response(censore_response, censore_data)
    # print(most_compatible_response)

    # Обработка результата цензуры по наибольшему соответствию
    if most_compatible_response == "clear":
        # Обработка для разрешенных заказов (обычные товары)
        addresses = await get_parsed_addresses(recognized_text, user_city)
        if len(addresses) == 2:
            pickup_address, delivery_address = addresses
            pickup_coords = await get_coordinates(pickup_address)
            delivery_coords = await get_coordinates(delivery_address)
            all_coordinates = [pickup_coords, delivery_coords]

            if all(pickup_coords) and all(delivery_coords):
                # Продолжение обработки заказа
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

                distance, duration = await calculate_total_distance(all_coordinates)
                distance = round(distance, 2)

                sender_name, sender_phone = await user_data.get_username_userphone(tg_id)
                price = await get_price(distance, moscow_time)

                # Структурирование данных заказа
                structured_data = await process_order_text(recognized_text)
                city = structured_data.get('City')
                if not city:
                    city = user_city
                starting_point_a = structured_data.get('Starting point A')
                destination_point_b = structured_data.get('Destination point B')
                delivery_object = structured_data.get('Delivery object')
                receiver_name_1 = structured_data.get('Receiver name 1')
                receiver_phone_1 = structured_data.get('Receiver phone 1')
                order_details = structured_data.get('Order details', None)
                comments = structured_data.get('Comments', None)

                # Сохранение данных в состоянии
                await state.update_data(
                    city=city,
                    starting_point_a=starting_point_a,
                    a_latitude=float(pickup_coords[0]),
                    a_longitude=float(pickup_coords[1]),
                    a_coordinates=pickup_coords,
                    a_url=pickup_point,
                    destination_point_b=destination_point_b,
                    b_latitude=float(delivery_coords[0]),
                    b_longitude=float(delivery_coords[1]),
                    b_coordinates=delivery_coords,
                    b_url=delivery_point,
                    delivery_object=delivery_object,
                    sender_name=sender_name,
                    sender_phone=sender_phone,
                    receiver_name_1=receiver_name_1,
                    receiver_phone_1=receiver_phone_1,
                    order_details=order_details,
                    comments=comments,
                    distance_km=distance,
                    duration_min=duration,
                    price_rub=price,
                    order_text=recognized_text,
                    order_time=moscow_time,
                    yandex_maps_url=yandex_maps_url,
                    pickup_point=pickup_point,
                    delivery_point=delivery_point,
                )

                # Отправка ответа пользователю
                order_forma = (
                    f"<b>Ваш заказ</b> ✍︎\n"
                    f"---------------------------------------------\n"
                    f"<b>Город:</b> {city}\n\n"
                    f"⦿ <b>Адрес 1:</b> <a href='{pickup_point}'>{starting_point_a}</a>\n"
                    f"<b>Имя:</b> {sender_name}\n"
                    f"<b>Номер:</b> {sender_phone}\n\n"
                    f"⦿ <b>Адрес 2:</b> <a href='{delivery_point}'>{destination_point_b}</a>\n"
                    f"<b>Имя:</b> {receiver_name_1 if receiver_name_1 else '...'}\n"
                    f"<b>Номер:</b> {receiver_phone_1 if receiver_phone_1 else '...'}\n\n"
                    f"<b>Доставляем:</b> {delivery_object if delivery_object else '...'}\n\n"
                    f"<b>Расстояние:</b> {distance} км\n"
                    f"<b>Стоимость доставки:</b> {price}₽\n\n"
                    f"<b>Комментарии курьеру:</b> <i>{'*'}{comments if comments else '...'}</i>\n"
                    f"---------------------------------------------\n"
                    f"• Проверьте ваш заказ и если все верно, то разместите.\n"
                    f"• Курьер может связаться с вами для уточнения деталей!\n"
                    f"• Оплачивайте курьеру наличными или переводом.\n\n"
                    f"⦿⌁⦿ <a href='{yandex_maps_url}'>Маршрут доставки</a>\n\n"
                )
                new_message = await message.answer(
                    text=order_forma, reply_markup=reply_kb, disable_notification=True, parse_mode="HTML")

            else:
                new_message = await message.answer(
                    text=f"Не удалось получить координаты для заказа. Проверьте заказ и попробуйте снова.",
                    reply_markup=reply_kb, disable_notification=True
                )
        elif len(addresses) == 3:
            pickup_address, delivery_address_1, delivery_address_2 = addresses
            pickup_coords = await get_coordinates(pickup_address)
            delivery_coords_1 = await get_coordinates(delivery_address_1)
            delivery_coords_2 = await get_coordinates(delivery_address_2)
            all_coordinates = [pickup_coords, delivery_coords_1, delivery_coords_2]

            if all(pickup_coords) and all(delivery_coords_1) and (delivery_coords_2):
                # Продолжение обработки заказа
                yandex_maps_url = (
                    f"https://yandex.ru/maps/?rtext={pickup_coords[0]},{pickup_coords[1]}"
                    f"~{delivery_coords_1[0]},{delivery_coords_1[1]}"
                    f"~{delivery_coords_2[0]},{delivery_coords_2[1]}&rtt=auto"
                )
                pickup_point = (
                    f"https://yandex.ru/maps/?ll={pickup_coords[1]},{pickup_coords[0]}"
                    f"&pt={pickup_coords[1]},{pickup_coords[0]}&z=14"
                )
                delivery_point_1 = (
                    f"https://yandex.ru/maps/?ll={delivery_coords_1[1]},{delivery_coords_1[0]}"
                    f"&pt={delivery_coords_1[1]},{delivery_coords_1[0]}&z=14"
                )
                delivery_point_2 = (
                    f"https://yandex.ru/maps/?ll={delivery_coords_2[1]},{delivery_coords_2[0]}"
                    f"&pt={delivery_coords_2[1]},{delivery_coords_2[0]}&z=14"
                )

                distance, duration = await calculate_total_distance(all_coordinates)
                distance = round(distance, 2)

                sender_name, sender_phone = await user_data.get_username_userphone(tg_id)
                price = await get_price(distance, moscow_time, over_price=50)

                # Структурирование данных заказа
                structured_data = await process_order_text(recognized_text)
                city = structured_data.get('City')
                if not city:
                    city = user_city
                starting_point_a = structured_data.get('Starting point A')
                destination_point_b = structured_data.get('Destination point B')
                destination_point_c = structured_data.get('Destination point C')
                delivery_object = structured_data.get('Delivery object')
                receiver_name_1 = structured_data.get('Receiver name 1')
                receiver_phone_1 = structured_data.get('Receiver phone 1')
                receiver_name_2 = structured_data.get('Receiver name 2')
                receiver_phone_2 = structured_data.get('Receiver phone 2')
                order_details = structured_data.get('Order details', None)
                comments = structured_data.get('Comments', None)

                # Сохранение данных в состоянии
                await state.update_data(
                    city=city,
                    starting_point_a=starting_point_a,
                    a_latitude=float(pickup_coords[0]),
                    a_longitude=float(pickup_coords[1]),
                    a_coordinates=pickup_coords,
                    a_url=pickup_point,
                    destination_point_b=destination_point_b,
                    b_latitude=float(delivery_coords_1[0]),
                    b_longitude=float(delivery_coords_1[1]),
                    b_coordinates=delivery_coords_1,
                    b_url=delivery_point_1,
                    destination_point_c=destination_point_c,
                    c_latitude=float(delivery_coords_2[0]),
                    c_longitude=float(delivery_coords_2[1]),
                    c_coordinates=delivery_coords_2,
                    c_url=delivery_point_2,
                    delivery_object=delivery_object,
                    sender_name=sender_name,
                    sender_phone=sender_phone,
                    receiver_name_1=receiver_name_1,
                    receiver_phone_1=receiver_phone_1,
                    receiver_name_2=receiver_name_2,
                    receiver_phone_2=receiver_phone_2,
                    order_details=order_details,
                    comments=comments,
                    distance_km=distance,
                    duration_min=duration,
                    price_rub=price,
                    order_text=recognized_text,
                    order_time=moscow_time,
                    yandex_maps_url=yandex_maps_url,
                    pickup_point=pickup_point,
                    delivery_point=delivery_point_1,
                )

                # Отправка ответа пользователю
                order_forma = (
                    f"<b>Ваш заказ</b> ✍︎\n"
                    f"---------------------------------------------\n"
                    f"<b>Город:</b> {city}\n\n"
                    f"⦿ <b>Адрес 1:</b> <a href='{pickup_point}'>{starting_point_a}</a>\n"
                    f"<b>Имя:</b> {sender_name}\n"
                    f"<b>Телефон:</b> {sender_phone}\n\n"
                    f"⦿ <b>Адрес 2:</b> <a href='{delivery_point_1}'>{destination_point_b}</a>\n"
                    f"<b>Имя:</b> {receiver_name_1 if receiver_name_1 else '...'}\n"
                    f"<b>Телефон:</b> {receiver_phone_1 if receiver_phone_1 else '...'}\n\n"
                    f"⦿ <b>Адрес 3:</b> <a href='{delivery_point_2}'>{destination_point_c}</a>\n"
                    f"<b>Имя:</b> {receiver_name_2 if receiver_name_2 else '...'}\n"
                    f"<b>Телефон:</b> {receiver_phone_2 if receiver_phone_2 else '...'}\n\n"
                    f"<b>Доставляем:</b> {delivery_object if delivery_object else '...'}\n\n"
                    f"<b>Расстояние:</b> {distance} км\n"
                    f"<b>Стоимость доставки:</b> {price}₽\n\n"
                    f"<b>Комментарии курьеру:</b> <i>{'*'}{comments if comments else '...'}</i>\n"
                    f"---------------------------------------------\n"
                    f"• Проверьте ваш заказ и если все верно, то разместите.\n"
                    f"• Курьер может связаться с вами для уточнения деталей!\n"
                    f"• Оплачивайте курьеру наличными или переводом.\n\n"
                    f"⦿⌁⦿ <a href='{yandex_maps_url}'>Маршрут доставки</a>\n\n"
                )
                new_message = await message.answer(
                    text=order_forma, reply_markup=reply_kb, disable_notification=True, parse_mode="HTML"
                )
        elif len(addresses) == 4:
            pickup_address, delivery_address_1, delivery_address_2, delivery_address_3 = addresses
            pickup_coords = await get_coordinates(pickup_address)
            delivery_coords_1 = await get_coordinates(delivery_address_1)
            delivery_coords_2 = await get_coordinates(delivery_address_2)
            delivery_coords_3 = await get_coordinates(delivery_address_3)
            all_coordinates = [pickup_coords, delivery_coords_1, delivery_coords_2, delivery_coords_3]

            if all(pickup_coords) and all(delivery_coords_1) and all(delivery_coords_2) and all(delivery_coords_3):
                # Формирование ссылки для маршрута на Яндекс.Картах
                yandex_maps_url = (
                    f"https://yandex.ru/maps/?rtext={pickup_coords[0]},{pickup_coords[1]}"
                    f"~{delivery_coords_1[0]},{delivery_coords_1[1]}"
                    f"~{delivery_coords_2[0]},{delivery_coords_2[1]}"
                    f"~{delivery_coords_3[0]},{delivery_coords_3[1]}&rtt=auto"
                )

                # Ссылки на точки на карте
                pickup_point = (
                    f"https://yandex.ru/maps/?ll={pickup_coords[1]},{pickup_coords[0]}"
                    f"&pt={pickup_coords[1]},{pickup_coords[0]}&z=14"
                )
                delivery_point_1 = (
                    f"https://yandex.ru/maps/?ll={delivery_coords_1[1]},{delivery_coords_1[0]}"
                    f"&pt={delivery_coords_1[1]},{delivery_coords_1[0]}&z=14"
                )
                delivery_point_2 = (
                    f"https://yandex.ru/maps/?ll={delivery_coords_2[1]},{delivery_coords_2[0]}"
                    f"&pt={delivery_coords_2[1]},{delivery_coords_2[0]}&z=14"
                )
                delivery_point_3 = (
                    f"https://yandex.ru/maps/?ll={delivery_coords_3[1]},{delivery_coords_3[0]}"
                    f"&pt={delivery_coords_3[1]},{delivery_coords_3[0]}&z=14"
                )

                # Рассчет дистанции и продолжительности
                distance, duration = await calculate_total_distance(all_coordinates)
                distance = round(distance, 2)

                # Получение информации о пользователе
                sender_name, sender_phone = await user_data.get_username_userphone(tg_id)
                price = await get_price(distance, moscow_time, over_price=50)

                # Структурирование данных заказа
                structured_data = await process_order_text(recognized_text)
                city = structured_data.get('City', user_city)
                starting_point_a = structured_data.get('Starting point A')
                destination_point_b = structured_data.get('Destination point B')
                destination_point_c = structured_data.get('Destination point C')
                destination_point_d = structured_data.get('Destination point D')
                delivery_object = structured_data.get('Delivery object')
                receiver_name_1 = structured_data.get('Receiver name 1')
                receiver_phone_1 = structured_data.get('Receiver phone 1')
                receiver_name_2 = structured_data.get('Receiver name 2')
                receiver_phone_2 = structured_data.get('Receiver phone 2')
                receiver_name_3 = structured_data.get('Receiver name 3')
                receiver_phone_3 = structured_data.get('Receiver phone 3')
                order_details = structured_data.get('Order details', None)
                comments = structured_data.get('Comments', None)

                # Сохранение данных в состоянии
                await state.update_data(
                    city=city,
                    starting_point_a=starting_point_a,
                    a_latitude=float(pickup_coords[0]),
                    a_longitude=float(pickup_coords[1]),
                    a_coordinates=pickup_coords,
                    a_url=pickup_point,
                    destination_point_b=destination_point_b,
                    b_latitude=float(delivery_coords_1[0]),
                    b_longitude=float(delivery_coords_1[1]),
                    b_coordinates=delivery_coords_1,
                    b_url=delivery_point_1,
                    destination_point_c=destination_point_c,
                    c_latitude=float(delivery_coords_2[0]),
                    c_longitude=float(delivery_coords_2[1]),
                    c_coordinates=delivery_coords_2,
                    c_url=delivery_point_2,
                    destination_point_d=destination_point_d,
                    d_latitude=float(delivery_coords_3[0]),
                    d_longitude=float(delivery_coords_3[1]),
                    d_coordinates=delivery_coords_3,
                    d_url=delivery_point_3,
                    delivery_object=delivery_object,
                    sender_name=sender_name,
                    sender_phone=sender_phone,
                    receiver_name_1=receiver_name_1,
                    receiver_phone_1=receiver_phone_1,
                    receiver_name_2=receiver_name_2,
                    receiver_phone_2=receiver_phone_2,
                    receiver_name_3=receiver_name_3,
                    receiver_phone_3=receiver_phone_3,
                    order_details=order_details,
                    comments=comments,
                    distance_km=distance,
                    duration_min=duration,
                    price_rub=price,
                    order_text=recognized_text,
                    order_time=moscow_time,
                    yandex_maps_url=yandex_maps_url,
                    pickup_point=pickup_point,
                    delivery_point=delivery_point_1,
                )

                # Формирование ответа пользователю
                order_forma = (
                    f"<b>Ваш заказ</b> ✍︎\n"
                    f"---------------------------------------------\n"
                    f"<b>Город:</b> {city}\n\n"
                    f"⦿ <b>Адрес 1:</b> <a href='{pickup_point}'>{starting_point_a}</a>\n"
                    f"<b>Имя:</b> {sender_name}\n"
                    f"<b>Телефон:</b> {sender_phone}\n\n"
                    f"⦿ <b>Адрес 2:</b> <a href='{delivery_point_1}'>{destination_point_b}</a>\n"
                    f"<b>Имя:</b> {receiver_name_1 if receiver_name_1 else '...'}\n"
                    f"<b>Телефон:</b> {receiver_phone_1 if receiver_phone_1 else '...'}\n\n"
                    f"⦿ <b>Адрес 3:</b> <a href='{delivery_point_2}'>{destination_point_c}</a>\n"
                    f"<b>Имя:</b> {receiver_name_2 if receiver_name_2 else '...'}\n"
                    f"<b>Телефон:</b> {receiver_phone_2 if receiver_phone_2 else '...'}\n\n"
                    f"⦿ <b>Адрес 4:</b> <a href='{delivery_point_3}'>{destination_point_d}</a>\n"
                    f"<b>Имя:</b> {receiver_name_3 if receiver_name_3 else '...'}\n"
                    f"<b>Телефон:</b> {receiver_phone_3 if receiver_phone_3 else '...'}\n\n"
                    f"<b>Доставляем:</b> {delivery_object if delivery_object else '...'}\n\n"
                    f"<b>Расстояние:</b> {distance} км\n"
                    f"<b>Стоимость доставки:</b> {price}₽\n\n"
                    f"<b>Комментарии курьеру:</b> <i>{'*'}{comments if comments else '...'}</i>\n"
                    f"---------------------------------------------\n"
                    f"• Проверьте ваш заказ и если все верно, то разместите.\n"
                    f"• Курьер может связаться с вами для уточнения деталей!\n"
                    f"• Оплачивайте курьеру наличными или переводом.\n\n"
                    f"⦿⌁⦿ <a href='{yandex_maps_url}'>Маршрут доставки</a>\n\n"
                )
                new_message = await message.answer(
                    text=order_forma, reply_markup=reply_kb, disable_notification=True, parse_mode="HTML"
                )
        elif len(addresses) == 5:
            pickup_address, delivery_address_1, delivery_address_2, delivery_address_3, delivery_address_4 = addresses
            pickup_coords = await get_coordinates(pickup_address)
            delivery_coords_1 = await get_coordinates(delivery_address_1)
            delivery_coords_2 = await get_coordinates(delivery_address_2)
            delivery_coords_3 = await get_coordinates(delivery_address_3)
            delivery_coords_4 = await get_coordinates(delivery_address_4)
            all_coordinates = [pickup_coords, delivery_coords_1, delivery_coords_2, delivery_coords_3,
                               delivery_coords_4]

            if all(pickup_coords) and all(delivery_coords_1) and all(delivery_coords_2) and all(
                    delivery_coords_3) and all(delivery_coords_4):
                # Формирование ссылки для маршрута на Яндекс.Картах
                yandex_maps_url = (
                    f"https://yandex.ru/maps/?rtext={pickup_coords[0]},{pickup_coords[1]}"
                    f"~{delivery_coords_1[0]},{delivery_coords_1[1]}"
                    f"~{delivery_coords_2[0]},{delivery_coords_2[1]}"
                    f"~{delivery_coords_3[0]},{delivery_coords_3[1]}"
                    f"~{delivery_coords_4[0]},{delivery_coords_4[1]}&rtt=auto"
                )

                # Ссылки на точки на карте
                pickup_point = (
                    f"https://yandex.ru/maps/?ll={pickup_coords[1]},{pickup_coords[0]}"
                    f"&pt={pickup_coords[1]},{pickup_coords[0]}&z=14"
                )
                delivery_point_1 = (
                    f"https://yandex.ru/maps/?ll={delivery_coords_1[1]},{delivery_coords_1[0]}"
                    f"&pt={delivery_coords_1[1]},{delivery_coords_1[0]}&z=14"
                )
                delivery_point_2 = (
                    f"https://yandex.ru/maps/?ll={delivery_coords_2[1]},{delivery_coords_2[0]}"
                    f"&pt={delivery_coords_2[1]},{delivery_coords_2[0]}&z=14"
                )
                delivery_point_3 = (
                    f"https://yandex.ru/maps/?ll={delivery_coords_3[1]},{delivery_coords_3[0]}"
                    f"&pt={delivery_coords_3[1]},{delivery_coords_3[0]}&z=14"
                )
                delivery_point_4 = (
                    f"https://yandex.ru/maps/?ll={delivery_coords_4[1]},{delivery_coords_4[0]}"
                    f"&pt={delivery_coords_4[1]},{delivery_coords_4[0]}&z=14"
                )

                # Рассчет дистанции и продолжительности
                distance, duration = await calculate_total_distance(all_coordinates)
                distance = round(distance, 2)

                # Получение информации о пользователе
                sender_name, sender_phone = await user_data.get_username_userphone(tg_id)
                price = await get_price(distance, moscow_time, over_price=50)

                # Структурирование данных заказа
                structured_data = await process_order_text(recognized_text)
                city = structured_data.get('City', user_city)
                starting_point_a = structured_data.get('Starting point A')
                destination_point_b = structured_data.get('Destination point B')
                destination_point_c = structured_data.get('Destination point C')
                destination_point_d = structured_data.get('Destination point D')
                destination_point_e = structured_data.get('Destination point E')
                delivery_object = structured_data.get('Delivery object')
                receiver_name_1 = structured_data.get('Receiver name 1')
                receiver_phone_1 = structured_data.get('Receiver phone 1')
                receiver_name_2 = structured_data.get('Receiver name 2')
                receiver_phone_2 = structured_data.get('Receiver phone 2')
                receiver_name_3 = structured_data.get('Receiver name 3')
                receiver_phone_3 = structured_data.get('Receiver phone 3')
                receiver_name_4 = structured_data.get('Receiver name 4')
                receiver_phone_4 = structured_data.get('Receiver phone 4')
                order_details = structured_data.get('Order details', None)
                comments = structured_data.get('Comments', None)

                # Сохранение данных в состоянии
                await state.update_data(
                    city=city,
                    starting_point_a=starting_point_a,
                    a_latitude=float(pickup_coords[0]),
                    a_longitude=float(pickup_coords[1]),
                    a_coordinates=pickup_coords,
                    a_url=pickup_point,
                    destination_point_b=destination_point_b,
                    b_latitude=float(delivery_coords_1[0]),
                    b_longitude=float(delivery_coords_1[1]),
                    b_coordinates=delivery_coords_1,
                    b_url=delivery_point_1,
                    destination_point_c=destination_point_c,
                    c_latitude=float(delivery_coords_2[0]),
                    c_longitude=float(delivery_coords_2[1]),
                    c_coordinates=delivery_coords_2,
                    c_url=delivery_point_2,
                    destination_point_d=destination_point_d,
                    d_latitude=float(delivery_coords_3[0]),
                    d_longitude=float(delivery_coords_3[1]),
                    d_coordinates=delivery_coords_3,
                    d_url=delivery_point_3,
                    destination_point_e=destination_point_e,
                    e_latitude=float(delivery_coords_4[0]),
                    e_longitude=float(delivery_coords_4[1]),
                    e_coordinates=delivery_coords_4,
                    e_url=delivery_point_4,
                    delivery_object=delivery_object,
                    sender_name=sender_name,
                    sender_phone=sender_phone,
                    receiver_name_1=receiver_name_1,
                    receiver_phone_1=receiver_phone_1,
                    receiver_name_2=receiver_name_2,
                    receiver_phone_2=receiver_phone_2,
                    receiver_name_3=receiver_name_3,
                    receiver_phone_3=receiver_phone_3,
                    receiver_name_4=receiver_name_4,
                    receiver_phone_4=receiver_phone_4,
                    order_details=order_details,
                    comments=comments,
                    distance_km=distance,
                    duration_min=duration,
                    price_rub=price,
                    order_text=recognized_text,
                    order_time=moscow_time,
                    yandex_maps_url=yandex_maps_url,
                    pickup_point=pickup_point,
                    delivery_point=delivery_point_1,
                )

                # Формирование ответа пользователю
                order_forma = (
                    f"<b>Ваш заказ</b> ✍︎\n"
                    f"---------------------------------------------\n"
                    f"<b>Город:</b> {city}\n\n"
                    f"⦿ <b>Адрес 1:</b> <a href='{pickup_point}'>{starting_point_a}</a>\n"
                    f"<b>Имя:</b> {sender_name}\n"
                    f"<b>Телефон:</b> {sender_phone}\n\n"
                    f"⦿ <b>Адрес 2:</b> <a href='{delivery_point_1}'>{destination_point_b}</a>\n"
                    f"<b>Имя:</b> {receiver_name_1 if receiver_name_1 else '...'}\n"
                    f"<b>Телефон:</b> {receiver_phone_1 if receiver_phone_1 else '...'}\n\n"
                    f"⦿ <b>Адрес 3:</b> <a href='{delivery_point_2}'>{destination_point_c}</a>\n"
                    f"<b>Имя:</b> {receiver_name_2 if receiver_name_2 else '...'}\n"
                    f"<b>Телефон:</b> {receiver_phone_2 if receiver_phone_2 else '...'}\n\n"
                    f"⦿ <b>Адрес 4:</b> <a href='{delivery_point_3}'>{destination_point_d}</a>\n"
                    f"<b>Имя:</b> {receiver_name_3 if receiver_name_3 else '...'}\n"
                    f"<b>Телефон:</b> {receiver_phone_3 if receiver_phone_3 else '...'}\n\n"
                    f"⦿ <b>Адрес 5:</b> <a href='{delivery_point_4}'>{destination_point_e}</a>\n"
                    f"<b>Имя:</b> {receiver_name_4 if receiver_name_4 else '...'}\n"
                    f"<b>Телефон:</b> {receiver_phone_4 if receiver_phone_4 else '...'}\n\n"
                    f"<b>Доставляем:</b> {delivery_object if delivery_object else '...'}\n\n"
                    f"<b>Расстояние:</b> {distance} км\n"
                    f"<b>Стоимость доставки:</b> {price}₽\n\n"
                    f"<b>Комментарии курьеру:</b> <i>{'*'}{comments if comments else '...'}</i>\n"
                    f"---------------------------------------------\n"
                    f"• Проверьте ваш заказ и если все верно, то разместите.\n"
                    f"• Курьер может связаться с вами для уточнения деталей!\n"
                    f"• Оплачивайте курьеру наличными или переводом.\n\n"
                    f"⦿⌁⦿ <a href='{yandex_maps_url}'>Маршрут доставки</a>\n\n"
                )

                new_message = await message.answer(text=order_forma,
                                                   reply_markup=reply_kb,
                                                   disable_notification=True,
                                                   parse_mode="HTML")

        elif len(addresses) > 5:
            new_message = await message.answer(
                text=f"<b>Слишком много пунктов</b> 𐒀 \n\nМы не оформляем доставки с более чем 5 адресами, "
                     "так как курьер может запутаться и не выполнить ваш заказ!",
                reply_markup=reply_kb, disable_notification=True, parse_mode="HTML")



        else:
            new_message = await message.answer(
                text=f"Ваш заказ ✍︎\n\n{recognized_text}\n\nПроверьте ваш заказ и разместите его, если всё верно.",
                reply_markup=reply_kb, disable_notification=True
            )

    # elif most_compatible_response == "overprice":
    #     await state.set_state(UserState.default)
    #     reply_kb = await get_user_kb(text="overprice")
    #     new_message = await message.answer(
    #         text=("<b>Внимание</b>！ \n\nВаш заказ содержит табачные изделия или алкогольуню продукцию.\n\n"
    #               "<b>Доставка будет стоить немного дороже!</b>"),
    #         reply_markup=reply_kb, disable_notification=True, parse_mode="HTML"
    #     )
    elif most_compatible_response == "inaudible":
        await state.set_state(UserState.default)
        reply_kb = await get_user_kb(text="rerecord")
        new_message = await message.answer(
            text="<b>Ошибка</b> ⸘\n\nТекст сообщения неразборчив.\nПопробуйте отправить заказ снова.",
            reply_markup=reply_kb, disable_notification=True, parse_mode="HTML"
        )
    elif most_compatible_response == "no_item":
        await state.set_state(UserState.default)
        reply_kb = await get_user_kb(text="rerecord")
        new_message = await message.answer(
            text="<b>Что везем?!</b> \n\nКурьер должен знать что он доставляет.",
            reply_markup=reply_kb, disable_notification=True, parse_mode="HTML"
        )
    elif most_compatible_response == "not_order":
        await state.set_state(UserState.default)
        reply_kb = await get_user_kb(text="rerecord")
        new_message = await message.answer(
            text="<b>...</b> 🫤 \n\nСделайте корректный заказ!",
            reply_markup=reply_kb, disable_notification=True, parse_mode="HTML"
        )
    elif most_compatible_response == "intercity":
        await state.set_state(UserState.default)
        reply_kb = await get_user_kb(text="rerecord")
        new_message = await message.answer(
            text="<b>Так далеко мы не доставляем</b> ⟷ \n\nМы осуществляем доставку только в пределах одного города!",
            reply_markup=reply_kb, disable_notification=True, parse_mode="HTML"
        )

    else:
        await state.set_state(UserState.default)
        reply_kb = await get_user_kb(text="rerecord")
        new_message = await message.answer(
            text="<b>Отказ!!!</b> 🚫\n\nМы не можем это доставлять!",
            reply_markup=reply_kb, disable_notification=True, parse_mode="HTML"
        )

    # Завершение обработки
    await wait_message.delete()
    await handler.handle_new_message(new_message, message)


# send_Order
@users_router.callback_query(F.data == "order_sent")
async def set_order_to_db(callback_query: CallbackQuery, state: FSMContext):
    # Устанавливаем состояние
    await state.set_state(UserState.default)

    # Создаем обработчик сообщений
    handler = MessageHandler(state, callback_query.bot)

    # Получаем ID пользователя
    tg_id = callback_query.from_user.id
    data = await state.get_data()
    await state.set_state(UserState.default)

    try:
        # Асинхронно создаем заказ
        order_number = await order_data.create_order(tg_id, data)
        text = (
            f"Заказ <b>№{order_number}</b> успешно создан! 🎉\n"
            f"Мы ищем курьера для вашего заказа 🔎\n\n"
            f"<i>*Информацию о заказах можно посмотреть в разделе</i> <b>Мои заказы</b>.\n\n"
            f"▼ <b>Выберите действие ...</b>"
        )
    except Exception as e:
        # Обработка возможных ошибок
        print(f"Ошибка при создании заказа: {str(e)}")

        text = ("Ошибка при создании заказа.\n"
                "Попробуйте повторить заказ.")

    new_message = await callback_query.message.answer(text,
                                                      disable_notification=True,
                                                      parse_mode="HTML")

    # Обрабатываем новое сообщение
    await handler.handle_new_message(new_message, callback_query.message)


# ---------------------------------------------✺ The end (u_rout) ✺ ------------------------------------------------- #


@users_router.message(F.text == "/share")
async def switch_button(message: Message, state: FSMContext):
    await state.set_state(UserState.default)
    handler = MessageHandler(state, message.bot)
    await handler.delete_previous_message(message.chat.id)
    reply_kb = await get_switch()
    new_message = await message.answer("Нажмите на кнопку", reply_markup=reply_kb)
    await handler.handle_new_message(new_message, message)
