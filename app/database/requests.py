import json
from sqlalchemy import select, update, delete, desc, func, extract, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import async_session_factory, moscow_time, Order, utc_time
from app.database.models import User, Courier, OrderStatus
from app.database.models import moscow_time
from sqlalchemy import select, and_
from app.common.coords_and_price import calculate_distance


class UserData:
    def __init__(self, async_session_factory):
        self.async_session_factory = async_session_factory

    async def get_user_tg_id_by_phone(self, phone_number: str) -> int:
        async with self.async_session_factory() as session:
            user = await session.scalar(select(User).where(User.user_phone_number == phone_number))
            if user:
                return user.user_tg_id
            else:
                raise ValueError("Пользователь не найден")

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

    async def set_user_accept_tou(self, tg_id: int, accepted: str):
        async with self.async_session_factory() as session:
            user = await session.scalar(select(User).where(User.user_tg_id == tg_id))
            if user:
                user.user_accept_terms_of_use = accepted
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

    async def set_courier_info(self, tg_id: int, name: str, phone_number: str,
                               default_city: str, accept_terms_tou: str,
                               registration_date: str):
        async with self.async_session_factory() as session:
            # Пытаемся найти существующего курьера
            courier = await session.scalar(select(Courier).where(Courier.courier_tg_id == tg_id))
            if courier:
                # Если курьер найден, обновляем его данные
                courier.courier_name = name
                courier.courier_phone_number = phone_number
                courier.courier_default_city = default_city
                courier.courier_accept_terms_of_use = accept_terms_tou
                courier.registration_date = registration_date
            else:
                # Если курьер не найден, создаем нового курьера
                new_courier = Courier(
                    courier_tg_id=tg_id,
                    courier_name=name,
                    courier_phone_number=phone_number,
                    courier_default_city=default_city,
                    courier_accept_terms_of_use=accept_terms_tou,
                    courier_registration_date=registration_date
                )
                session.add(new_courier)

            # Сохраняем изменения в базе данных
            await session.commit()

    async def set_courier_name(self, tg_id: int, name: str):
        async with self.async_session_factory() as session:
            courier = await session.scalar(select(Courier).where(Courier.courier_tg_id == tg_id))
            if courier:
                courier.courier_name = name
                await session.commit()

    async def set_courier_phone(self, tg_id: int, phone: str):
        async with self.async_session_factory() as session:
            courier = await session.scalar(select(Courier).where(Courier.courier_tg_id == tg_id))
            if courier:
                courier.courier_phone_number = phone
                await session.commit()

    async def set_courier_city(self, tg_id: int, city: str):
        async with self.async_session_factory() as session:
            courier = await session.scalar(select(Courier).where(Courier.courier_tg_id == tg_id))
            if courier:
                courier.courier_default_city = city
                await session.commit()

    async def get_courier_info(self, tg_id: int):
        async with self.async_session_factory() as session:
            courier = await session.scalar(select(Courier).where(Courier.courier_tg_id == tg_id))
            if courier:
                return (
                    courier.courier_name or "...",
                    courier.courier_phone_number or "...",
                )
            return (None, None)

    async def get_courier_full_info(self, tg_id: int):
        async with self.async_session_factory() as session:
            # Используем join для извлечения связанных данных о подписке
            courier = await session.scalar(
                select(Courier).where(Courier.courier_tg_id == tg_id).options(selectinload(Courier.subscription))
            )
            if courier:
                subscription_status = courier.subscription.status if courier.subscription else "Нет подписки"
                return (
                    courier.courier_name or "...",
                    courier.courier_phone_number or "...",
                    courier.courier_default_city or "...",  # убедитесь, что поле существует в модели
                    subscription_status
                )
            return (None, None, None, "Нет подписки")  # добавлено "Нет подписки" для более полного результата

    async def get_courier_phone(self, tg_id: int):
        async with self.async_session_factory() as session:
            courier = await session.scalar(select(Courier).where(Courier.courier_tg_id == tg_id))
            if courier:
                return courier.courier_phone_number
            return None

    async def get_courier_city(self, tg_id: int):
        async with self.async_session_factory() as session:
            courier = await session.scalar(select(Courier).where(Courier.courier_tg_id == tg_id))
            if courier:
                return courier.courier_default_city
            return None


class OrderData:
    def __init__(self, async_session_factory):
        self.async_session_factory = async_session_factory

    async def get_order_customer_phone(self, order_id: int) -> str:
        async with self.async_session_factory() as session:
            # Предполагается, что есть таблица Order и связанная таблица User
            order = await session.scalar(select(Order).where(Order.order_id == order_id))
            if order:
                return order.sender_phone
            else:
                raise ValueError("Заказ не найден")

    async def get_order_customer_tg_id(self, order_id: int) -> int:
        async with self.async_session_factory() as session:
            # Ищем заказ по его ID
            order = await session.scalar(select(Order).where(Order.order_id == order_id))

            if not order:
                raise ValueError(f"Заказ с ID {order_id} не найден")

            # Получаем tg_id клиента
            customer_tg_id = order.customer_tg_id  # предполагаем, что у объекта `order` есть поле `customer_tg_id`
            return customer_tg_id

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
                    order.completed_at_moscow_time = moscow_time
                await session.commit()

    async def get_order_courier_info(self, order_id):
        async with self.async_session_factory() as session:
            query = await session.execute(
                select(Order.courier_id)
                .where(Order.order_id == order_id)
            )
            courier_id = query.scalar()
            query_2 = await session.execute(
                select(Courier.courier_name, Courier.courier_phone_number)
                .where(Courier.courier_id == courier_id)
            )
            courier_info = query_2.first()

            if courier_info:
                courier_name, courier_phone = courier_info
                return courier_name, courier_phone
            else:
                return '...', '...'

    async def assign_courier(self, order_id: int, courier_id: int):
        async with self.async_session_factory() as session:
            order = await session.scalar(select(Order).where(Order.order_id == order_id))
            if order:
                order.courier_id = courier_id
                await session.commit()

    async def get_pending_orders(self, user_tg_id: int):
        async with self.async_session_factory() as session:
            user_query = await session.execute(
                select(User.user_id).where(User.user_tg_id == user_tg_id)
            )
            user_id = user_query.scalar()
            if user_id is None:
                return []
            orders_query = await session.execute(
                select(Order).where(
                    and_(
                        Order.user_id == user_id,
                        Order.order_status == OrderStatus.PENDING
                    )
                )
            )
            pending_orders = orders_query.scalars().all()
            return pending_orders

    async def get_active_orders(self, user_tg_id: int):
        async with self.async_session_factory() as session:
            user_query = await session.execute(
                select(User.user_id).where(User.user_tg_id == user_tg_id)
            )
            user_id = user_query.scalar()
            if user_id is None:
                return []
            orders_query = await session.execute(
                select(Order).where(
                    and_(
                        Order.user_id == user_id,
                        Order.order_status == OrderStatus.IN_PROGRESS
                    )
                )
            )
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
            user_query = await session.execute(
                select(User.user_id).where(User.user_tg_id == user_tg_id)
            )
            user_id = user_query.scalar()
            if user_id is None:
                return []
            orders_query = await session.execute(
                select(Order).where(
                    and_(
                        Order.user_id == user_id,
                        Order.order_status == OrderStatus.COMPLETED
                    )
                )
            )
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
            user_query = await session.execute(
                select(User.user_id).where(User.user_tg_id == user_tg_id)
            )
            user_id = user_query.scalar()

            if user_id is None:
                return []  # Если пользователь не найден

            orders_query = await session.execute(
                select(Order).where(Order.user_id == user_id)
            )
            orders = orders_query.scalars().all()

            return orders

    async def get_total_orders(self, user_tg_id: int):
        async with self.async_session_factory() as session:
            user_query = await session.execute(
                select(User.user_id).where(User.user_tg_id == user_tg_id)
            )
            user_id = user_query.scalar()

            if user_id is None:
                return 0

            result = await session.execute(
                select(func.count(Order.order_id)).where(Order.user_id == user_id)
            )
            return result.scalar()

    async def get_completed_orders_count(self, user_tg_id: int):
        async with self.async_session_factory() as session:
            user_query = await session.execute(
                select(User.user_id).where(User.user_tg_id == user_tg_id)
            )
            user_id = user_query.scalar()

            if user_id is None:
                return 0

            result = await session.execute(
                select(func.count(Order.order_id)).where(
                    and_(
                        Order.user_id == user_id,
                        Order.order_status == OrderStatus.COMPLETED
                    )
                )
            )
            return result.scalar()

    async def get_canceled_orders_count(self, user_tg_id: int):
        async with self.async_session_factory() as session:
            user_query = await session.execute(
                select(User.user_id).where(User.user_tg_id == user_tg_id)
            )
            user_id = user_query.scalar()

            if user_id is None:
                return 0

            result = await session.execute(
                select(func.count(Order.order_id)).where(
                    and_(
                        Order.user_id == user_id,
                        Order.order_status == OrderStatus.CANCELLED
                    )
                )
            )
            return result.scalar()

    async def get_avg_order_speed(self, user_tg_id: int):
        async with self.async_session_factory() as session:
            user_query = await session.execute(
                select(User.user_id).where(User.user_tg_id == user_tg_id)
            )
            user_id = user_query.scalar()

            if user_id is None:
                return 0

            result = await session.execute(
                select(func.avg(Order.distance_km / (extract('epoch', Order.execution_time) / 3600)))
                .where(
                    and_(
                        Order.user_id == user_id,
                        Order.order_status == OrderStatus.COMPLETED
                    )
                )
            )
            return result.scalar()

    async def get_avg_order_distance(self, user_tg_id: int):
        async with self.async_session_factory() as session:
            user_query = await session.execute(
                select(User.user_id).where(User.user_tg_id == user_tg_id)
            )
            user_id = user_query.scalar()

            if user_id is None:
                return 0

            result = await session.execute(
                select(func.avg(Order.distance_km))
                .where(
                    and_(
                        Order.user_id == user_id,
                        Order.order_status == OrderStatus.COMPLETED
                    )
                )
            )
            return result.scalar()

    async def get_fastest_order_speed(self, user_tg_id: int):
        async with self.async_session_factory() as session:
            user_query = await session.execute(
                select(User.user_id).where(User.user_tg_id == user_tg_id)
            )
            user_id = user_query.scalar()

            if user_id is None:
                return 0

            result = await session.execute(
                select(func.max(Order.distance_km / (extract('epoch', Order.execution_time) / 3600)))
                .where(
                    and_(
                        Order.user_id == user_id,
                        Order.order_status == OrderStatus.COMPLETED
                    )
                )
            )
            return result.scalar()

    async def get_slowest_order_speed(self, user_tg_id: int):
        async with self.async_session_factory() as session:
            user_query = await session.execute(
                select(User.user_id).where(User.user_tg_id == user_tg_id)
            )
            user_id = user_query.scalar()

            if user_id is None:
                return 0

            result = await session.execute(
                select(func.min(Order.distance_km / (extract('epoch', Order.execution_time) / 3600)))
                .where(
                    and_(
                        Order.user_id == user_id,
                        Order.order_status == OrderStatus.COMPLETED
                    )
                )
            )
            return result.scalar()

    async def get_avg_order_time(self, user_tg_id: int):
        async with self.async_session_factory() as session:
            user_query = await session.execute(
                select(User.user_id).where(User.user_tg_id == user_tg_id)
            )
            user_id = user_query.scalar()

            if user_id is None:
                return 0

            result = await session.execute(
                select(func.avg(extract('epoch', Order.execution_time)))
                .where(
                    and_(
                        Order.user_id == user_id,
                        Order.order_status == OrderStatus.COMPLETED
                    )
                )
            )
            avg_time = result.scalar()
            return (avg_time / 60) if avg_time is not None else 0

    async def get_fastest_order_time(self, user_tg_id: int):
        async with self.async_session_factory() as session:
            user_query = await session.execute(
                select(User.user_id).where(User.user_tg_id == user_tg_id)
            )
            user_id = user_query.scalar()

            if user_id is None:
                return 0

            result = await session.execute(
                select(func.min(extract('epoch', Order.execution_time)))
                .where(
                    and_(
                        Order.user_id == user_id,
                        Order.order_status == OrderStatus.COMPLETED
                    )
                )
            )
            fastest_time = result.scalar()
            return (fastest_time / 60) if fastest_time is not None else 0

    async def get_longest_order_time(self, user_tg_id: int):
        async with self.async_session_factory() as session:
            user_query = await session.execute(
                select(User.user_id).where(User.user_tg_id == user_tg_id)
            )
            user_id = user_query.scalar()

            if user_id is None:
                return 0

            result = await session.execute(
                select(func.max(extract('epoch', Order.execution_time)))
                .where(
                    and_(
                        Order.user_id == user_id,
                        Order.order_status == OrderStatus.COMPLETED
                    )
                )
            )
            longest_time = result.scalar()
            return (longest_time / 60) if longest_time is not None else 0

    async def get_shortest_order_distance(self, user_tg_id: int):
        async with self.async_session_factory() as session:
            user_query = await session.execute(
                select(User.user_id).where(User.user_tg_id == user_tg_id)
            )
            user_id = user_query.scalar()

            if user_id is None:
                return 0

            result = await session.execute(
                select(func.min(Order.distance_km))
                .where(
                    and_(
                        Order.user_id == user_id,
                        Order.order_status == OrderStatus.COMPLETED
                    )
                )
            )
            return result.scalar()

    async def get_longest_order_distance(self, user_tg_id: int):
        async with self.async_session_factory() as session:
            user_query = await session.execute(
                select(User.user_id).where(User.user_tg_id == user_tg_id)
            )
            user_id = user_query.scalar()

            if user_id is None:
                return 0

            result = await session.execute(
                select(func.max(Order.distance_km))
                .where(
                    and_(
                        Order.user_id == user_id,
                        Order.order_status == OrderStatus.COMPLETED
                    )
                )
            )
            return result.scalar()

    async def get_avg_order_price(self, user_tg_id: int):
        async with self.async_session_factory() as session:
            user_query = await session.execute(
                select(User.user_id).where(User.user_tg_id == user_tg_id)
            )
            user_id = user_query.scalar()

            if user_id is None:
                return 0

            result = await session.execute(
                select(func.avg(Order.price_rub))
                .where(
                    and_(
                        Order.user_id == user_id,
                        Order.order_status == OrderStatus.COMPLETED
                    )
                )
            )
            return result.scalar()

    async def get_max_order_price(self, user_tg_id: int):
        async with self.async_session_factory() as session:
            user_query = await session.execute(
                select(User.user_id).where(User.user_tg_id == user_tg_id)
            )
            user_id = user_query.scalar()

            if user_id is None:
                return 0

            result = await session.execute(
                select(func.max(Order.price_rub))
                .where(
                    and_(
                        Order.user_id == user_id,
                        Order.order_status == OrderStatus.COMPLETED
                    )
                )
            )
            return result.scalar()

    async def get_min_order_price(self, user_tg_id: int):
        async with self.async_session_factory() as session:
            user_query = await session.execute(
                select(User.user_id).where(User.user_tg_id == user_tg_id)
            )
            user_id = user_query.scalar()

            if user_id is None:
                return 0

            result = await session.execute(
                select(func.min(Order.price_rub))
                .where(
                    and_(
                        Order.user_id == user_id,
                        Order.order_status == OrderStatus.COMPLETED
                    )
                )
            )
            return result.scalar()

    async def get_order_by_id(self, current_order_id):
        async with async_session_factory() as session:
            user_query = await session.execute(
                select(Order)
                .where(Order.order_id == current_order_id)
            )
            current_order = user_query.scalar()
            return current_order

    async def _get_user_id(self, tg_id: int) -> int:
        async with self.async_session_factory() as session:
            user_query = await session.scalar(select(Courier.courier_id).where(Courier.courier_tg_id == tg_id))
            if not user_query:
                raise ValueError("Пользователь не найден")
            return user_query

    async def get_order_statistics(self, tg_id: int):
        user_id = await self._get_user_id(tg_id)

        async with self.async_session_factory() as session:
            # Используем агрегации в одном запросе
            result = await session.execute(
                select(
                    func.count(Order.order_id).label("total_orders"),
                    func.count(case((Order.order_status == OrderStatus.COMPLETED, 1))).label("completed_orders"),
                    func.count(case((Order.order_status == OrderStatus.CANCELLED, 1))).label("canceled_orders"),
                    func.avg(case((Order.order_status == OrderStatus.COMPLETED,
                                   Order.distance_km / (extract('epoch', Order.execution_time) / 3600)))).label(
                        "avg_order_speed"),
                    func.avg(case((Order.order_status == OrderStatus.COMPLETED, Order.distance_km))).label(
                        "avg_order_distance"),
                    func.min(case((Order.order_status == OrderStatus.COMPLETED,
                                   Order.distance_km / (extract('epoch', Order.execution_time) / 3600)))).label(
                        "slowest_order_speed"),
                    func.max(case((Order.order_status == OrderStatus.COMPLETED,
                                   Order.distance_km / (extract('epoch', Order.execution_time) / 3600)))).label(
                        "fastest_order_speed"),
                    func.avg(case(
                        (Order.order_status == OrderStatus.COMPLETED, extract('epoch', Order.execution_time)))).label(
                        "avg_order_time"),
                    func.min(case(
                        (Order.order_status == OrderStatus.COMPLETED, extract('epoch', Order.execution_time)))).label(
                        "fastest_order_time"),
                    func.max(case(
                        (Order.order_status == OrderStatus.COMPLETED, extract('epoch', Order.execution_time)))).label(
                        "longest_order_time"),
                    func.min(case((Order.order_status == OrderStatus.COMPLETED, Order.distance_km))).label(
                        "shortest_order_distance"),
                    func.max(case((Order.order_status == OrderStatus.COMPLETED, Order.distance_km))).label(
                        "longest_order_distance"),
                    # Новые агрегаты для стоимости заказов
                    func.min(case((Order.order_status == OrderStatus.COMPLETED, Order.price_rub))).label("min_price"),
                    func.max(case((Order.order_status == OrderStatus.COMPLETED, Order.price_rub))).label("max_price"),
                    func.avg(case((Order.order_status == OrderStatus.COMPLETED, Order.price_rub))).label("avg_price"),
                    func.sum(case((Order.order_status == OrderStatus.COMPLETED, Order.price_rub))).label("total_earn")
                ).where(Order.user_id == user_id)
            )

            # Достаем результаты
            stats = result.fetchone()
            return {
                "total_orders": stats.total_orders or 0,
                "completed_orders": stats.completed_orders or 0,
                "canceled_orders": stats.canceled_orders or 0,
                "avg_order_speed": stats.avg_order_speed or 0,
                "avg_order_distance": stats.avg_order_distance or 0,
                "slowest_order_speed": stats.slowest_order_speed or 0,
                "fastest_order_speed": stats.fastest_order_speed or 0,
                "avg_order_time": (stats.avg_order_time / 60) if stats.avg_order_time else 0,
                "fastest_order_time": (stats.fastest_order_time / 60) if stats.fastest_order_time else 0,
                "longest_order_time": (stats.longest_order_time / 60) if stats.longest_order_time else 0,
                "shortest_order_distance": stats.shortest_order_distance or 0,
                "longest_order_distance": stats.longest_order_distance or 0,
                "min_price": stats.min_price or 0,
                "max_price": stats.max_price or 0,
                "avg_price": stats.avg_price or 0,
                "total_earn": stats.total_earn or 0,

            }


user_data = UserData(async_session_factory)
courier_data = CourierData(async_session_factory)
order_data = OrderData(async_session_factory)
