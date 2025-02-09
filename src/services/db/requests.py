from .__deps__ import *


class UserData:
    def __init__(self, async_session_factory):
        self.async_session_factory = async_session_factory

    async def get_user_tg_id_by_phone(self, phone_number: str) -> int:
        async with self.async_session_factory() as session:
            user = await session.scalar(
                select(User).where(User.user_phone_number == phone_number)
            )
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
                return (
                    user.user_name or "...",
                    user.user_phone_number or "...",
                    user.user_default_city or "...",
                )
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

    async def set_courier_info(
        self,
        tg_id: int,
        name: str,
        phone_number: str,
        default_city: str,
        accept_terms_tou: str,
        registration_date: str,
    ):
        async with self.async_session_factory() as session:
            # Пытаемся найти существующего курьера
            courier = await session.scalar(
                select(Courier).where(Courier.courier_tg_id == tg_id)
            )
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
                    courier_registration_date=registration_date,
                )
                session.add(new_courier)

            # Сохраняем изменения в базе данных
            await session.commit()

    async def set_courier_name(self, tg_id: int, name: str):
        async with self.async_session_factory() as session:
            courier = await session.scalar(
                select(Courier).where(Courier.courier_tg_id == tg_id)
            )
            if courier:
                courier.courier_name = name
                await session.commit()

    async def set_courier_phone(self, tg_id: int, phone: str):
        async with self.async_session_factory() as session:
            courier = await session.scalar(
                select(Courier).where(Courier.courier_tg_id == tg_id)
            )
            if courier:
                courier.courier_phone_number = phone
                await session.commit()

    async def set_courier_city(self, tg_id: int, city: str):
        async with self.async_session_factory() as session:
            courier = await session.scalar(
                select(Courier).where(Courier.courier_tg_id == tg_id)
            )
            if courier:
                courier.courier_default_city = city
                await session.commit()

    async def get_courier_info(self, tg_id: int):
        async with self.async_session_factory() as session:
            courier = await session.scalar(
                select(Courier).where(Courier.courier_tg_id == tg_id)
            )
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
                select(Courier)
                .where(Courier.courier_tg_id == tg_id)
                .options(selectinload(Courier.subscription))
            )
            if courier:
                subscription_status = (
                    courier.subscription.status
                    if courier.subscription
                    else "Нет подписки"
                )
                return (
                    courier.courier_name or "...",
                    courier.courier_phone_number or "...",
                    courier.courier_default_city
                    or "...",  # убедитесь, что поле существует в модели
                    subscription_status,
                )
            return (
                None,
                None,
                None,
                "Нет подписки",
            )  # добавлено "Нет подписки" для более полного результата

    async def get_courier_phone(self, tg_id: int):
        async with self.async_session_factory() as session:
            courier = await session.scalar(
                select(Courier).where(Courier.courier_tg_id == tg_id)
            )
            if courier:
                return courier.courier_phone_number
            return None

    async def get_courier_city(self, tg_id: int):
        async with self.async_session_factory() as session:
            courier = await session.scalar(
                select(Courier).where(Courier.courier_tg_id == tg_id)
            )
            if courier:
                return courier.courier_default_city
            return None


class OrderData:
    def __init__(self, async_session_factory):
        self.async_session_factory = async_session_factory

    async def get_order_customer_phone(self, order_id: int) -> str:
        async with self.async_session_factory() as session:
            # Предполагается, что есть таблица Order и связанная таблица User
            order = await session.scalar(
                select(Order).where(Order.order_id == order_id)
            )
            if order:
                return order.customer_phone
            else:
                raise ValueError("Заказ не найден")

    async def get_order_customer_tg_id(self, order_id: int) -> int:
        async with self.async_session_factory() as session:
            # Ищем заказ по его ID
            order = await session.scalar(
                select(Order).where(Order.order_id == order_id)
            )

            if not order:
                raise ValueError(f"Заказ с ID {order_id} не найден")

            # Получаем tg_id клиента
            customer_tg_id = (
                order.customer_tg_id
            )  # предполагаем, что у объекта `order` есть поле `customer_tg_id`
            return customer_tg_id

    async def create_order(self, user_tg_id: int, data: dict):
        async with self.async_session_factory() as session:
            async with session.begin():

                user = await session.scalar(
                    select(User).where(User.user_tg_id == user_tg_id)
                )

                new_order = Order(
                    user_id=user.user_id,
                    order_city=data.get("city"),
                    delivery_object=data.get("delivery_object"),
                    customer_name=data.get("customer_name"),
                    customer_phone=data.get("customer_phone"),
                    description=data.get("description"),
                    distance_km=data.get("distance_km"),
                    price_rub=data.get("price_rub"),
                    created_at_moscow_time=data.get("order_time"),
                    full_rout=data.get("yandex_maps_url"),
                    order_status=OrderStatus.PENDING,
                )

                session.add(new_order)
                await session.flush()
                order_id = new_order.order_id

            await session.commit()

        return order_id

    async def assign_courier_to_order(self, order_id: int, courier_tg_id: int):
        async with self.async_session_factory() as session:
            # Ищем курьера по tg_id
            courier = await session.scalar(
                select(Courier).where(Courier.courier_tg_id == courier_tg_id)
            )
            if not courier:
                raise ValueError("Курьер не найден")

            # Ищем заказ и обновляем его
            order = await session.scalar(
                select(Order).where(Order.order_id == order_id)
            )
            if not order:
                raise ValueError("Заказ не найден")

            order.courier_id = courier.courier_id
            await session.commit()

    async def update_order_status(self, order_id: int, new_status: OrderStatus):
        async with self.async_session_factory() as session:
            order = await session.scalar(
                select(Order).where(Order.order_id == order_id)
            )
            if order:
                order.order_status = new_status
                if new_status == OrderStatus.COMPLETED:
                    order.completed_at_moscow_time = moscow_time
                await session.commit()

    async def get_order_courier_info(self, order_id):
        async with self.async_session_factory() as session:
            query = await session.execute(
                select(Order.courier_id).where(Order.order_id == order_id)
            )
            courier_id = query.scalar()
            query_2 = await session.execute(
                select(Courier.courier_name, Courier.courier_phone_number).where(
                    Courier.courier_id == courier_id
                )
            )
            courier_info = query_2.first()

            if courier_info:
                courier_name, courier_phone = courier_info
                return courier_name, courier_phone
            else:
                return "...", "..."

    async def assign_courier(self, order_id: int, courier_id: int):
        async with self.async_session_factory() as session:
            order = await session.scalar(
                select(Order).where(Order.order_id == order_id)
            )
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
                        Order.order_status == OrderStatus.PENDING,
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
                        Order.order_status == OrderStatus.IN_PROGRESS,
                    )
                )
            )
            active_orders = orders_query.scalars().all()
            return active_orders

    async def get_canceled_orders(self, user_tg_id: int):
        async with self.async_session_factory() as session:
            orders_query = await session.execute(
                select(Order).where(
                    and_(
                        User.user_tg_id == user_tg_id,
                        Order.order_status == OrderStatus.CANCELLED,
                    )
                )
            )

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
                        Order.order_status == OrderStatus.COMPLETED,
                    )
                )
            )
            completed_orders = orders_query.scalars().all()
            return completed_orders

    async def get_available_orders(
        self,
        courier_tg_id: int,
        courier_lat: float,
        courier_lon: float,
        radius_km: float,
    ) -> list:
        async with async_session_factory() as session:
            orders_query = await session.execute(
                select(Order).where(
                    and_(
                        Order.order_status == OrderStatus.PENDING,
                        # User.user_tg_id != Courier.courier_tg_id
                    )
                )
            )
            orders = orders_query.scalars().all()

            available_orders = []

            for order in orders:
                distance = calculate_distance(
                    order.a_latitude, order.a_longitude, courier_lat, courier_lon
                )
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
                        Order.order_status == OrderStatus.COMPLETED,
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
                        Order.order_status == OrderStatus.CANCELLED,
                    )
                )
            )
            return result.scalar()

    async def get_order_by_id(self, current_order_id):
        async with async_session_factory() as session:
            user_query = await session.execute(
                select(Order).where(Order.order_id == current_order_id)
            )
            current_order = user_query.scalar()
            return current_order

    async def _get_user_id(self, tg_id: int) -> int:
        async with self.async_session_factory() as session:
            user_query = await session.scalar(
                select(Courier.courier_id).where(Courier.courier_tg_id == tg_id)
            )
            if not user_query:
                raise ValueError("Пользователь не найден")
            return user_query

    async def update_order_status_and_time(
        self, order_id: int, new_status: OrderStatus, completed_time: datetime
    ):
        async with self.async_session_factory() as session:
            async with session.begin():
                # Получаем заказ по ID
                order = await session.execute(
                    select(Order).where(Order.order_id == order_id)
                )
                order = order.scalars().first()

                if not order:
                    raise ValueError("Заказ не найден")

                # Обновляем статус и время завершения
                order.order_status = new_status
                order.completed_at_moscow_time = completed_time

                # Сохраняем изменения
                await session.commit()


user_data = UserData(async_session_factory)
courier_data = CourierData(async_session_factory)
order_data = OrderData(async_session_factory)


__all__ = ["user_data", "courier_data", "order_data"]
