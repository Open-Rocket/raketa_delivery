import asyncio
from app.u_pack.u_ai_assistant import assistant_censure

messages = [
    # Чистый заказ
    ("Нужно забрать букет цветов на улице Цветочная, дом 8, Санкт-Петербург и доставить к дому 24 на улице Ленина. "
     "Важно, чтобы цветы не завяли. Можете привезти до 18:00?"),

    # Заказ с подозрительным содержанием
    ("Нужно забрать небольшую коробку с улицы Малая Дмитровка, дом 13, Москва и доставить на улицу Большая Садовая, "
     "дом 5. В коробке кое-что ценное. Не спрашивайте, что именно, просто доставьте."),

    # Заказ, который включает табачные изделия
    ("Заберите табачные изделия из магазина на улице Горького, дом 11, Екатеринбург и привезите их на проспект Ленина, "
     "дом 76, офис 204. Товар оплачу на месте, это срочно."),

    # Заказ с лекарствами
    ("Пожалуйста, заберите лекарства из аптеки на улице Бажова, дом 27, Москва и доставьте на улицу Красная Пресня, "
     "дом 12, квартира 5. Сам(а) не могу выйти, очень нужна помощь."),

    # Заказ с неразборчивым текстом
    ("sdjfksjdnfksdnfksdjnfksdnfksdjfnsdf"),

    # Подозрительный заказ (наркотические вещества)
    ("Заберите пакет с порошком с улицы Лесная, дом 3, Санкт-Петербург и доставьте его на улицу Свердлова, дом 9. "
     "Не задавайте вопросов, просто доставьте как можно быстрее."),

    # Нормальный заказ с просьбой доставки документов
    ("Пожалуйста, заберите документы на улице Советской, дом 34, Новосибирск и доставьте их в офис на улице Пушкина, "
     "дом 67. Это важные бумаги, будьте, пожалуйста, аккуратны."),

    # Заказ с алкоголем (разрешённый товар)
    ("Заберите бутылку вина из винного магазина на улице Красных Ворот, дом 23, Нижний Новгород и привезите на "
     "улицу Фрунзе, дом 18. Всё уже оплачено."),

    # Заказ с просьбой доставки продуктов
    ("Заберите продукты из магазина на улице Пионерской, дом 9, Челябинск и привезите их на улицу Победы, дом 23. "
     "Сам(а) не могу сходить, заранее спасибо."),

    # Заказ с электронной сигаретой (разрешённый товар)
    ("Нужно купить электронную сигарету в магазине на улице Строителей, дом 17, Казань и привезти её в общежитие на "
     "улице Академическая, дом 5, комната 412. Оплата при доставке.")
]

no_item_test1 = "Нужно сделать доставку с улицы Лобачевского 92 корпус 2 на станцию метро Маяковская"
no_item_test2 = "Нужно сделать доставку с улицы Херсонская 43 на Рыбный переулок дом 3"
no_item_test3 = "Нужно сделать 10 отжиманий с утра"
no_item_test4 = "Нужно сделать утипу акипи аляля секс шпекс пулапекс атубату"
no_item_test5 = "ываывьтпдылвпдлытьудп"
no_item_test6 = "Нужно сделать доставку из Изингарда в Мордор, доставлять будем кольцо всевластия"
no_item_test7 = "Нужно доставить коробку с котятами с улицы Лобачевского 92 корпус 2 на станцию метро Маяковская"
no_item_test8 = "Нужно доставить документы из Москвы в Санкт-Петербург"



async def print_answer(msg):
    answer = await assistant_censure(no_item_test7)
    print(answer)


# Запуск асинхронной функции через asyncio.run()
asyncio.run(print_answer(messages))



# @users_router.message(F.text == "/my_orders")
# async def send_user_orders(message: Message, state: FSMContext):
#     await state.set_state(UserState.myOrders)
#
#     handler = MessageHandler(state, message.bot)
#     my_tg_id = message.from_user.id
#
#     # Получаем заказы, сделанные пользователем
#     user_orders = await order_data.get_user_orders(my_tg_id)
#     # Сохраняем заказы в состоянии с их ID
#     orders_dict = {order.order_id: order for order in user_orders}  # Словарь ID -> заказ
#     await state.update_data(orders=orders_dict)
#
#     # Функция для формирования адреса и информации о получателе
#     def format_address(number, address, name, phone, url):
#         return (
#             f"⦿ Адрес {number}: <a href='{url}'>{address}</a>\n"
#             f"Имя: {name if name else '-'}\n"
#             f"Телефон: {phone if phone else '-'}\n\n"
#         )
#
#     # -------------------- Формируем список заказов для отображения -------------------- #
#     orders = []
#     for order in user_orders:
#         base_info = (
#             f"Всего заказов: {len(user_orders)}\n\n"
#             f"Заказ №{order.order_id}\n"
#             f"Дата оформления: {order.created_at_moscow_time}\n"
#             f"Статус заказа: {order.order_status.value}\n"
#             f"---------------------------------------------\n"
#             f"Город: {order.order_city}\n"
#             f"{format_address(1, order.starting_point_a, order.sender_name, order.sender_phone, order.a_url)}"
#         )
#
#         # Динамическое добавление адресов до 3-х
#         if order.destination_point_b:
#             base_info += format_address(2, order.destination_point_b,
#                                         order.receiver_name_1,
#                                         order.receiver_phone_1,
#                                         order.b_url)
#
#         if order.destination_point_c:
#             base_info += format_address(3, order.destination_point_c,
#                                         order.receiver_name_2,
#                                         order.receiver_phone_2,
#                                         order.c_url)
#
#         # Дополнительная информация о заказе
#         base_info += (
#             f"Доставляем: {order.delivery_object if order.delivery_object else '-'}\n\n"
#             f"Расстояние: {order.distance_km} км\n"
#             f"Стоимость доставки: {order.price_rub}₽\n"
#             f"---------------------------------------------\n"
#             f"Комментарии: {order.comments if order.comments else '-'}\n\n"
#             f"⦿⌁⦿ <a href='{order.full_rout}'>Маршрут</a>\n\n"
#         )
#
#         orders.append(base_info)
#
#     # -------------------- Если заказов нет -------------------- #
#     if not orders:
#         await handler.delete_previous_message(message.chat.id)
#         new_message = await message.answer("У вас нет заказов.")
#         await handler.handle_new_message(new_message, message)
#         return
#
#     await handler.delete_previous_message(message.chat.id)
#
#     # -------------------- Устанавливаем начальный заказ и сохраняем его -------------------- #
#     counter = 0
#     await state.update_data(orders=orders, counter=counter)
#
#     reply_kb = await get_user_kb(text="one_order_my" if len(orders) == 1 else message.text)
#     new_message = await message.answer(orders[counter], reply_markup=reply_kb,
#                                        parse_mode="HTML",
#                                        disable_notification=True)
#     await handler.handle_new_message(new_message, message)
#
#     # -------------- Finish -------------- #
