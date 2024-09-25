import json
from sqlalchemy import select, update, delete, desc, func, extract
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import async_session_factory, moscow_time, Order, utc_time
from app.database.models import User, Courier, OrderStatus
from sqlalchemy import select, and_
from app.common.coords_and_price import calculate_distance


class UserData:
    def __init__(self, async_session_factory):
        self.async_session_factory = async_session_factory

    async def set_user(self, tg_id: int):
        async with self.async_session_factory() as session:
            user = await session.scalar(select(User).where(User.user_tg_id == tg_id))
            if not user:
                new_user = User(user_tg_id=tg_id)
                session.add(new_user)
                await session.commit()

    async def set_user_name(self, tg_id: int, name: str):
        async with self.async_session_factory() as session:
            user = await session.scalar(select(User).where(User.user_tg_id == tg_id))
            if user:
                user.user_name = name
                await session.commit()

    async def set_user_phone(self, tg_id: int, phone: str):
        async with self.async_session_factory() as session:
            user = await session.scalar(select(User).where(User.user_tg_id == tg_id))
            if user:
                user.user_phone_number = phone
                await session.commit()

    async def set_user_city(self, tg_id: int, city: str):
        async with self.async_session_factory() as session:
            user = await session.scalar(select(User).where(User.user_tg_id == tg_id))
            if user:
                user.user_default_city = city
                await session.commit()

    async def get_user_info(self, tg_id: int):
        async with self.async_session_factory() as session:
            user = await session.scalar(select(User).where(User.user_tg_id == tg_id))
            if user:
                return (user.user_name or "...", user.user_phone_number or "...", user.user_default_city or "...")
            return ("...", "...", "...")

    async def get_username_userphone(self, tg_id: int):
        async with self.async_session_factory() as session:
            user = await session.scalar(select(User).where(User.user_tg_id == tg_id))

            if user:
                return user.user_name, user.user_phone_number
            else:
                return None, None

    async def get_user_city(self, tg_id: int):
        async with self.async_session_factory() as session:
            user = await session.scalar(select(User).where(User.user_tg_id == tg_id))

            if user:
                return user.user_default_city
            else:
                return None


class CourierData:
    def __init__(self, async_session_factory):
        self.async_session_factory = async_session_factory

    async def set_courier(self, tg_id: int):
        async with self.async_session_factory() as session:
            courier = await session.scalar(select(Courier).where(Courier.courier_tg_id == tg_id))
            if not courier:
                new_courier = Courier(courier_tg_id=tg_id)
                session.add(new_courier)
                await session.commit()

    async def set_courier_name(self, tg_id: int, name: str):
        async with self.async_session_factory() as session:
            courier = await session.scalar(select(Courier).where(Courier.courier_tg_id == tg_id))
            if courier:
                courier.courier_name = name
                await session.commit()

    async def set_courier_email(self, tg_id: int, email: str):
        async with self.async_session_factory() as session:
            courier = await session.scalar(select(Courier).where(Courier.courier_tg_id == tg_id))
            if courier:
                courier.courier_email = email
                await session.commit()

    async def set_courier_phone(self, tg_id: int, phone: str):
        async with self.async_session_factory() as session:
            courier = await session.scalar(select(Courier).where(Courier.courier_tg_id == tg_id))
            if courier:
                courier.courier_phone_number = phone
                await session.commit()

    async def get_courier_info(self, tg_id: int):
        async with self.async_session_factory() as session:
            courier = await session.scalar(select(Courier).where(Courier.courier_tg_id == tg_id))
            if courier:
                return (
                    courier.courier_name or "...", courier.courier_email or "...",
                    courier.courier_phone_number or "...")
            return ("...", "...", "...")


class OrderData:
    def __init__(self, async_session_factory):
        self.async_session_factory = async_session_factory

    async def create_order(self, user_tg_id: int, data: dict):
        async with self.async_session_factory() as session:  # Открываем асинхронный сеанс
            async with session.begin():  # Начинаем транзакцию
                # Ищем пользователя по tg_id
                user = await session.scalar(select(User).where(User.user_tg_id == user_tg_id))
                if not user:
                    raise ValueError("Пользователь не найден")

                # Создаем новый заказ на основе данных из состояния FSM
                new_order = Order(
                    user_id=user.user_id,
                    order_city=data.get('city'),
                    starting_point_a=data.get('starting_point_a'),
                    a_coordinates=data.get('a_coordinates'),
                    a_latitude=data.get("a_latitude"),
                    a_longitude=data.get("a_longitude"),
                    a_url=data.get("a_url"),
                    destination_point_b=data.get('destination_point_b'),
                    b_coordinates=data.get('b_coordinates'),
                    b_latitude=data.get("b_latitude"),
                    b_longitude=data.get("b_longitude"),
                    b_url=data.get("b_url"),
                    destination_point_c=data.get('destination_point_c', None),  # Латинская "c"
                    c_coordinates=data.get('c_coordinates', None),  # Латинская "c"
                    c_latitude=data.get("c_latitude", None),  # Латинская "c"
                    c_longitude=data.get("c_longitude", None),  # Латинская "c"
                    c_url=data.get("c_url", None),  # Латинская "c"
                    delivery_object=data.get('delivery_object'),
                    sender_name=data.get('sender_name'),
                    sender_phone=data.get('sender_phone'),
                    receiver_name_1=data.get('receiver_name_1', None),
                    receiver_phone_1=data.get('receiver_phone_1', None),
                    receiver_name_2=data.get('receiver_name_2', None),
                    receiver_phone_2=data.get('receiver_phone_2', None),
                    receiver_name_3=data.get('receiver_name_3', None),
                    receiver_phone_3=data.get('receiver_phone_3', None),
                    receiver_name_4=data.get('receiver_name_4', None),
                    receiver_phone_4=data.get('receiver_phone_4', None),
                    comments=data.get('comments'),
                    order_text=data.get('order_text'),
                    distance_km=data.get('distance_km'),
                    duration_min=data.get('duration_min'),
                    price_rub=data.get('price_rub'),
                    created_at_moscow_time=data.get('order_time'),
                    full_rout=data.get("yandex_maps_url")
                )

                # Добавляем новый заказ в сессию
                session.add(new_order)

                # Принудительно сохраняем изменения (чтобы объект привязался к сессии и получил ID)
                await session.flush()

                # Получаем ID заказа после flush
                order_id = new_order.order_id

            # Коммитим изменения
            await session.commit()

        return order_id  # Возвращаем ID созданного заказа

    async def assign_courier_to_order(self, order_id: int, courier_tg_id: int):
        async with self.async_session_factory() as session:
            # Ищем курьера по tg_id
            courier = await session.scalar(select(Courier).where(Courier.courier_tg_id == courier_tg_id))
            if not courier:
                raise ValueError("Курьер не найден")

            # Ищем заказ и обновляем его
            order = await session.scalar(select(Order).where(Order.order_id == order_id))
            if not order:
                raise ValueError("Заказ не найден")

            order.courier_id = courier.courier_id
            await session.commit()

    async def update_order_status(self, order_id: int, new_status: OrderStatus):
        async with self.async_session_factory() as session:
            order = await session.scalar(select(Order).where(Order.order_id == order_id))
            if order:
                order.order_status = new_status
                if new_status == OrderStatus.COMPLETED:
                    order.completed_at = utc_time()
                await session.commit()

    async def assign_courier(self, order_id: int, courier_id: int):
        async with self.async_session_factory() as session:
            order = await session.scalar(select(Order).where(Order.order_id == order_id))
            if order:
                order.courier_id = courier_id
                await session.commit()

    async def get_pending_orders(self, user_tg_id: int):
        async with self.async_session_factory() as session:
            orders_query = await session.execute(
                select(Order)
                .where(and_(
                    User.user_tg_id == user_tg_id,
                    Order.order_status == OrderStatus.PENDING
                )
                ))

            pending_orders = orders_query.scalars().all()
            return pending_orders

    async def get_active_orders(self, user_tg_id: int):
        async with self.async_session_factory() as session:
            orders_query = await session.execute(
                select(Order)
                .where(and_(
                    User.user_tg_id == user_tg_id,
                    Order.order_status == OrderStatus.IN_PROGRESS
                )
                ))

            active_orders = orders_query.scalars().all()
            return active_orders

    async def get_canceled_orders(self, user_tg_id: int):
        async with self.async_session_factory() as session:
            orders_query = await session.execute(
                select(Order)
                .where(and_(
                    User.user_tg_id == user_tg_id,
                    Order.order_status == OrderStatus.CANCELLED
                )
                ))

            canceled_orders = orders_query.scalars().all()
            return canceled_orders

    async def get_completed_orders(self, user_tg_id: int):
        async with self.async_session_factory() as session:
            orders_query = await session.execute(
                select(Order)
                .where(and_(
                    User.user_tg_id == user_tg_id,
                    Order.order_status == OrderStatus.COMPLETED
                )
                ))

            completed_orders = orders_query.scalars().all()
            return completed_orders

    async def get_available_orders(self, courier_tg_id: int,
                                   courier_lat: float,
                                   courier_lon: float,
                                   radius_km: float):
        async with async_session_factory() as session:
            orders_query = await session.execute(
                select(Order)
                .where(and_(
                    Order.order_status == OrderStatus.PENDING,
                    # User.user_tg_id != Courier.courier_tg_id
                ))
            )
            orders = orders_query.scalars().all()

            available_orders = []

            for order in orders:
                distance = calculate_distance(order.a_latitude, order.a_longitude, courier_lat, courier_lon)
                if distance <= radius_km:
                    available_orders.append(order)

            return available_orders

    async def get_user_orders(self, user_tg_id: int):
        async with async_session_factory() as session:
            orders_query = await session.execute(
                select(Order)
                .where(User.user_tg_id == user_tg_id)
            )

            # Извлекаем все заказы
            orders = orders_query.scalars().all()

            # Возвращаем список заказов
            return orders

    async def get_total_orders(self, user_id: int):
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(func.count(Order.order_id))
                .where(Order.user_id == user_id)
            )
            return result.scalar()

    async def get_completed_orders_count(self, user_id: int):
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(func.count(Order.order_id))
                .where(
                    and_(
                        Order.user_id == user_id,
                        Order.order_status == OrderStatus.COMPLETED
                    )
                )
            )
            return result.scalar()

    async def get_canceled_orders_count(self, user_id: int):
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(func.count(Order.order_id))
                .where(
                    and_(
                        Order.user_id == user_id,
                        Order.order_status == OrderStatus.CANCELLED
                    )
                )
            )
            return result.scalar()

    async def get_avg_order_speed(self, user_id: int):
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(func.avg(Order.distance_km / (extract('epoch', Order.execution_time) / 3600)))  # км/ч
                .where(Order.user_id == user_id)
            )
            return result.scalar()

    async def get_avg_order_distance(self, user_id: int):
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(func.avg(Order.distance_km))
                .where(Order.user_id == user_id)
            )
            return result.scalar()

    async def get_fastest_order_speed(self, user_id: int):
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(func.max(Order.distance_km / (extract('epoch', Order.execution_time) / 3600)))  # км/ч
                .where(
                    and_(
                        Order.user_id == user_id,
                        Order.order_status == OrderStatus.COMPLETED
                    )
                )
            )
            return result.scalar()

    async def get_slowest_order_speed(self, user_id: int):
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(func.min(Order.distance_km / (extract('epoch', Order.execution_time) / 3600)))  # км/ч
                .where(
                    and_(
                        Order.user_id == user_id,
                        Order.order_status == OrderStatus.COMPLETED
                    )
                )
            )
            return result.scalar()

    async def get_avg_order_time(self, user_id: int):
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(func.avg(extract('epoch', Order.execution_time)))  # среднее время в секундах
                .where(Order.user_id == user_id)
            )
            return result.scalar() / 60  # переводим в минуты

    async def get_fastest_order_time(self, user_id: int):
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(func.min(extract('epoch', Order.execution_time)))  # минимальное время в секундах
                .where(
                    and_(
                        Order.user_id == user_id,
                        Order.order_status == OrderStatus.COMPLETED
                    )
                )
            )
            return result.scalar() / 60  # переводим в минуты

    async def get_longest_order_time(self, user_id: int):
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(func.max(extract('epoch', Order.execution_time)))  # максимальное время в секундах
                .where(
                    and_(
                        Order.user_id == user_id,
                        Order.order_status == OrderStatus.COMPLETED
                    )
                )
            )
            return result.scalar() / 60  # переводим в минуты

    async def get_shortest_order_distance(self, user_id: int):
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(func.min(Order.distance_km))
                .where(Order.user_id == user_id)
            )
            return result.scalar()

    async def get_longest_order_distance(self, user_id: int):
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(func.max(Order.distance_km))
                .where(Order.user_id == user_id)
            )
            return result.scalar()

    async def get_avg_order_price(self, user_id: int):
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(func.avg(Order.price_rub))
                .where(Order.user_id == user_id)
            )
            return result.scalar()

    async def get_max_order_price(self, user_id: int):
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(func.max(Order.price_rub))
                .where(Order.user_id == user_id)
            )
            return result.scalar()

    async def get_min_order_price(self, user_id: int):
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(func.min(Order.price_rub))
                .where(Order.user_id == user_id)
            )
            return result.scalar()

# async def get_users():
#     async with async_session_factory() as session:  # Используйте свой async_session
#         result = await session.execute(select(User))
#         users = result.scalars().all()  # Получение всех пользователей
#         print(users)


user_data = UserData(async_session_factory)
courier_data = CourierData(async_session_factory)
order_data = OrderData(async_session_factory)
