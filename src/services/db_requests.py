import zlib
from src.models import (
    async_session_factory,
    Customer,
    Courier,
    OrderStatus,
    Order,
    Subscription,
)
from sqlalchemy import select
from datetime import datetime, timedelta
from sqlalchemy.engine import Result
from typing import Optional
from src.config import moscow_time, log
from geopy.distance import geodesic
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Callable


class CustomerData:
    def __init__(self, async_session_factory):
        self.async_session_factory = async_session_factory

    # ---

    async def set_customer(
        self,
        tg_id: int,
        name: str,
        phone: str,
        city: str,
        tou: str,
    ) -> bool:
        """Добавляет в БД нового пользователя"""

        async with self.async_session_factory() as session:
            try:
                new_customer = Customer(
                    customer_tg_id=tg_id,
                    customer_name=name,
                    customer_phone=phone,
                    customer_city=city,
                    customer_accept_terms_of_use=tou,
                    customer_registration_date=moscow_time,
                )
                session.add(new_customer)
                await session.flush()
                await session.commit()
                return True
            except Exception as e:
                await session.rollback()
                log.error(f"Ошибка при добавлении пользователя: {e}")
                return False

    # ---

    async def update_customer_name(
        self,
        tg_id: int,
        new_name: str,
    ) -> bool:
        """Обновляет имя пользователя в БД"""

        async with self.async_session_factory() as session:
            try:
                # Находим пользователя по tg_id
                result = await session.execute(
                    select(Customer).where(Customer.customer_tg_id == tg_id)
                )
                customer = result.scalar_one_or_none()

                if not customer:
                    log.error(f"Пользователь с tg_id={tg_id} не найден.")
                    return False

                # Обновляем имя
                customer.customer_name = new_name

                # Сохраняем изменения
                await session.commit()
                log.info(f"Имя успешно обновлено для пользователя {tg_id}.")
                return True
            except Exception as e:
                await session.rollback()
                log.error(f"Ошибка при обновлении имени: {e}")
                return False

    async def update_customer_phone(
        self,
        tg_id: int,
        new_phone: str,
    ) -> bool:
        """Обновляет номер пользователя в БД"""

        async with self.async_session_factory() as session:
            try:
                # Находим пользователя по tg_id
                result = await session.execute(
                    select(Customer).where(Customer.customer_tg_id == tg_id)
                )
                customer = result.scalar_one_or_none()

                if not customer:
                    log.error(f"Пользователь с tg_id={tg_id} не найден.")
                    return False

                # Обновляем телефон
                customer.customer_phone = new_phone

                # Сохраняем изменения
                await session.commit()
                log.info(f"Телефон успешно обновлен для пользователя {tg_id}.")
                return True
            except Exception as e:
                await session.rollback()
                log.error(f"Ошибка при обновлении телефона: {e}")
                return False

    async def update_customer_city(
        self,
        tg_id: int,
        new_city: str,
    ) -> bool:
        """Обновляет город пользователя в БД"""

        async with self.async_session_factory() as session:
            try:
                # Находим пользователя по tg_id
                result = await session.execute(
                    select(Customer).where(Customer.customer_tg_id == tg_id)
                )
                customer = result.scalar_one_or_none()

                if not customer:
                    log.error(f"Пользователь с tg_id={tg_id} не найден.")
                    return False

                # Обновляем город
                customer.customer_city = new_city

                # Сохраняем изменения
                await session.commit()
                log.info(f"Город успешно обновлен для пользователя {tg_id}.")
                return True
            except Exception as e:
                await session.rollback()
                log.error(f"Ошибка при обновлении города: {e}")
                return False

    # ---

    async def get_customer_info(self, tg_id: int) -> tuple:
        """Возвращает имя, номер и город пользователя из БД"""
        async with self.async_session_factory() as session:
            customer = await session.scalar(
                select(Customer).where(Customer.customer_tg_id == tg_id)
            )
            if customer:
                return (
                    customer.customer_name or "...",
                    customer.customer_phone or "...",
                    customer.customer_city or "...",
                )
            return ("...", "...", "...")


class CourierData:
    def __init__(self, async_session_factory: Callable[..., AsyncSession]):
        self.async_session_factory = async_session_factory

    # ---

    async def set_courier(
        self,
        tg_id: int,
        name: str,
        phone: str,
        city: str,
        tou: str,
    ) -> bool:
        """Добавляет в БД нового курьера"""

        async with self.async_session_factory() as session:
            try:
                new_courier = Courier(
                    courier_tg_id=tg_id,
                    courier_name=name,
                    courier_phone=phone,
                    courier_city=city,
                    courier_accept_terms_of_use=tou,
                    courier_registration_date=moscow_time,
                )
                session.add(new_courier)
                await session.flush()
                await session.commit()
                return True
            except Exception as e:
                await session.rollback()
                log.error(f"Ошибка при добавлении курьера: {e}")
                return False

    # ---
    async def change_order_active_count(self, tg_id: int, count: int) -> bool:
        """Изменяет счетчик активных заказов курьера на count"""

        async with self.async_session_factory() as session:
            try:
                result = await session.execute(
                    select(Courier).where(Courier.courier_tg_id == tg_id)
                )
                courier = result.scalar_one_or_none()

                if not courier:
                    log.error(f"Курьер с tg_id={tg_id} не найден.")
                    return False

                if courier.orders_active_now:
                    courier.orders_active_now += count

                await session.flush()
                await session.commit()
                return True
            except Exception as e:
                await session.rollback()
                log.error(f"Ошибка при увеличении счетчика активных заказов: {e}")
                return False

    # ---

    async def update_courier_name(
        self,
        tg_id: int,
        new_name: str,
    ) -> bool:
        """Обновляет имя курьера в БД"""

        async with self.async_session_factory() as session:
            try:

                result = await session.execute(
                    select(Courier).where(Courier.courier_tg_id == tg_id)
                )
                courier = result.scalar_one_or_none()

                if not courier:
                    log.error(f"Курьер с tg_id={tg_id} не найден.")
                    return False

                courier.courier_name = new_name

                await session.flush()
                await session.commit()
                log.info(f"Имя успешно обновлено для курьера {tg_id}.")
                return True
            except Exception as e:
                await session.rollback()
                log.error(f"Ошибка при обновлении имени: {e}")
                return False

    async def update_courier_phone(
        self,
        tg_id: int,
        new_phone: str,
    ) -> bool:
        """Обновляет номер курьера в БД"""

        async with self.async_session_factory() as session:
            try:

                result = await session.execute(
                    select(Courier).where(Courier.courier_tg_id == tg_id)
                )
                courier = result.scalar_one_or_none()

                if not courier:
                    log.error(f"Курьер с tg_id={tg_id} не найден.")
                    return False

                courier.courier_phone = new_phone

                await session.flush()
                await session.commit()
                log.info(f"Телефон успешно обновлен для курьера {tg_id}.")
                return True
            except Exception as e:
                await session.rollback()
                log.error(f"Ошибка при обновлении телефона: {e}")
                return False

    async def update_courier_city(
        self,
        tg_id: int,
        new_city: str,
    ) -> bool:
        """Обновляет город курьера в БД"""

        async with self.async_session_factory() as session:
            try:

                result = await session.execute(
                    select(Courier).where(Courier.courier_tg_id == tg_id)
                )
                courier = result.scalar_one_or_none()

                if not courier:
                    log.error(f"Курьер с tg_id={tg_id} не найден.")
                    return False

                courier.courier_city = new_city

                await session.flush()
                await session.commit()
                log.info(f"Город успешно обновлен для курьера {tg_id}.")
                return True
            except Exception as e:
                await session.rollback()
                log.error(f"Ошибка при обновлении города: {e}")
                return False

    async def update_courier_subscription(self, tg_id: int, days: int) -> bool:
        """Продлевает подписку курьера на 30 дней, либо создаёт новую, если её нет."""

        async with self.async_session_factory() as session:
            try:
                result = await session.execute(
                    select(Courier).where(Courier.courier_tg_id == tg_id)
                )
                courier = result.scalar_one_or_none()

                if not courier:
                    log.error(f"Курьер с tg_id={tg_id} не найден.")
                    return False

                now = moscow_time

                result = await session.execute(
                    select(Subscription).where(
                        Subscription.courier_id == courier.courier_id
                    )
                )
                subscription = result.scalar_one_or_none()

                if subscription:

                    if subscription.end_date >= now:
                        subscription.end_date += timedelta(days=days)
                    else:

                        subscription.end_date = now + timedelta(days=days)
                else:

                    new_subscription = Subscription(
                        end_date=now + timedelta(days=30),
                        courier_id=courier.courier_id,
                    )
                    session.add(new_subscription)

                await session.flush()
                await session.commit()
                log.info(f"Подписка успешно обновлена/создана для курьера {tg_id}.")
                return True

            except Exception as e:
                await session.rollback()
                log.error(f"Ошибка при обновлении подписки: {e}")
                return False

    # ---

    async def get_courier_info(self, tg_id: int) -> tuple:
        """Возвращает имя, номер и город курьера из БД"""
        async with self.async_session_factory() as session:
            courier = await session.scalar(
                select(Courier).where(Courier.courier_tg_id == tg_id)
            )
            if courier:
                return (
                    courier.courier_name or "...",
                    courier.courier_phone or "...",
                    courier.courier_city or "...",
                )
            return ("...", "...", "...")

    async def get_courier_city(self, tg_id: int) -> str:
        """Возвращает имя, номер и город курьера из БД"""
        async with self.async_session_factory() as session:
            courier = await session.scalar(
                select(Courier).where(Courier.courier_tg_id == tg_id)
            )
            if courier:
                return courier.courier_city or "..."
            return "..."

    async def get_courier_full_info(self, tg_id: int) -> tuple:
        """Возвращает полную информацию о курьере, включая дату окончания подписки"""
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(Courier, Subscription.end_date)
                .join(
                    Subscription,
                    Subscription.courier_id == Courier.courier_id,
                    isouter=True,
                )
                .where(Courier.courier_tg_id == tg_id)
                .order_by(Subscription.end_date.desc())
                .limit(1)
            )
            row = result.first()

            if row:
                courier, end_date = row
            else:
                courier, end_date = None, None

            return (
                courier.courier_name if courier else "...",
                courier.courier_phone if courier else "...",
                courier.courier_city if courier else "...",
                end_date,
            )

    # ---

    async def get_courier_statistic(self, tg_id: int) -> tuple:
        """Возвращает статистику курьера"""

        async with self.async_session_factory() as session:
            courier = await session.scalar(
                select(Courier).where(Courier.courier_tg_id == tg_id)
            )
            if courier:
                orders = await session.execute(
                    select(Order).where(Order.courier_id == courier.courier_id)
                )
                orders = orders.scalars().all()
                total_orders = len(orders)
                completed_orders = len(
                    [
                        order
                        for order in orders
                        if order.order_status == OrderStatus.COMPLETED
                    ]
                )

                total_money_earned = sum(
                    order.price_rub
                    for order in orders
                    if order.order_status == OrderStatus.COMPLETED
                )
                total_execution_time = sum(
                    (
                        order.completed_at_moscow_time - order.started_at_moscow_time
                    ).total_seconds()
                    for order in orders
                    if order.order_status == OrderStatus.COMPLETED
                )
                total_distance = sum(
                    order.distance_km
                    for order in orders
                    if order.order_status == OrderStatus.COMPLETED
                )
                average_execution_time = (
                    total_execution_time / completed_orders
                    if completed_orders > 0
                    else 0
                )
                average_speed = (
                    total_distance / (total_execution_time / 3600)
                    if total_execution_time > 0
                    else 0
                )

                return (
                    total_orders,
                    completed_orders,
                    average_execution_time,
                    average_speed,
                    total_money_earned,
                )
            return 0, 0, 0, 0, 0, 0

    async def get_courier_active_orders_count(self, tg_id: int) -> int:
        """Возвращает количество активных заказов у курьера"""

        async with self.async_session_factory() as session:
            query: Result = await session.execute(
                select(Courier.orders_active_now).where(Courier.courier_tg_id == tg_id)
            )
            active_order_count = query.scalar()
            return active_order_count if active_order_count else 0


class OrderData:
    def __init__(self, async_session_factory: Callable[..., AsyncSession]):
        self.async_session_factory = async_session_factory

    # ---

    async def create_order(self, tg_id: int, data: dict, order_forma: str) -> int:
        """Создает новый заказ в БД"""

        async with self.async_session_factory() as session:
            async with session.begin():

                customer = await session.scalar(
                    select(Customer).where(Customer.customer_tg_id == tg_id)
                )

                new_order = Order(
                    customer_id=customer.customer_id,
                    order_city=data.get("city"),
                    delivery_object=data.get("delivery_object"),
                    customer_name=customer.customer_name,
                    customer_phone=customer.customer_phone,
                    customer_tg_id=customer.customer_tg_id,
                    description=data.get("description"),
                    distance_km=data.get("distance"),
                    price_rub=data.get("price"),
                    created_at_moscow_time=data.get("order_time"),
                    full_rout=data.get("yandex_maps_url"),
                    starting_point=data.get("starting_point"),
                    order_forma=order_forma,
                    order_status=OrderStatus.PENDING,
                )

                session.add(new_order)
                await session.flush()
                order_id = new_order.order_id

            await session.commit()

        return order_id

    # ---

    async def get_order_courier_info(self, order_id) -> tuple:
        """Возвращает информацию из заказа о курьере"""

        async with self.async_session_factory() as session:
            query = await session.execute(
                select(Order.courier_id).where(Order.order_id == order_id)
            )
            courier_id = query.scalar()
            query_courier_info = await session.execute(
                select(Courier.courier_name, Courier.courier_phone_number).where(
                    Courier.courier_id == courier_id
                )
            )
            courier_info = query_courier_info.first()

            if courier_info:
                courier_name, courier_phone = courier_info
                return (courier_name, courier_phone)
            else:
                return ("...", "...")

    # ---

    async def assign_courier_to_order(self, order_id: int, tg_id: int) -> bool:
        """Назначает курьера на заказ"""

        async with self.async_session_factory() as session:
            order = await session.get(Order, order_id)
            courier_id_query = await session.execute(
                select(Courier.courier_id).where(Courier.courier_tg_id == tg_id)
            )
            courier_id = courier_id_query.scalar()

            if not order:
                return False

            if order.courier_id is not None:
                log.error(f"Заказ {order_id} уже имеет назначенного курьера.")
                return False

            order.courier_id = courier_id
            order.courier_tg_id = tg_id
            await session.flush()
            await session.commit()
            return True

    # ---

    async def update_order_status(self, order_id: int, new_status: OrderStatus) -> bool:
        """Обновляет статус заказа"""

        async with self.async_session_factory() as session:
            order = await session.get(Order, order_id)
            if not order or order.order_status in (
                OrderStatus.IN_PROGRESS,
                OrderStatus.COMPLETED,
                OrderStatus.CANCELLED,
            ):
                return False

            order.order_status = new_status
            await session.flush()
            await session.commit()
            return True

    async def update_order_status_and_started_time(
        self, order_id: int, new_status: OrderStatus, started_time: datetime
    ) -> bool:
        """Обновляет статус заказа и время начала его выполнения"""

        async with self.async_session_factory() as session:
            async with session.begin():
                order = await session.get(Order, order_id)
                if not order or order.order_status == new_status:
                    return False

                if not order:
                    log.error("Заказ не найден")
                    return False

                order.order_status = new_status
                order.started_at_moscow_time = started_time

                await session.flush()
                await session.commit()
                return True

    async def update_order_status_and_completed_time(
        self, order_id: int, new_status: OrderStatus, completed_time: datetime
    ) -> bool:
        """Обновляет статус заказа и время завершения его выполнения"""

        async with self.async_session_factory() as session:
            async with session.begin():
                order = await session.execute(
                    select(Order).where(Order.order_id == order_id)
                )
                order = order.scalars().first()

                if not order:
                    log.error("Заказ не найден")
                    return False

                order.order_status = new_status
                order.completed_at_moscow_time = completed_time

                await session.flush()
                await session.commit()
                return True

    # ---

    async def get_pending_orders(self, tg_id: int) -> list:
        """Возвращает доступные заказы"""

        async with self.async_session_factory() as session:
            query = await session.execute(
                select(Order)
                .join(
                    Customer,
                    Customer.customer_id == Order.customer_id,
                )
                .where(
                    Customer.customer_tg_id == tg_id,
                    Order.order_status == OrderStatus.PENDING,
                )
            )
            return query.scalars().all()

    async def get_active_orders(self, tg_id: int) -> list:
        """Возвращает активные заказы"""

        async with self.async_session_factory() as session:
            query = await session.execute(
                select(Order)
                .join(
                    Customer,
                    Customer.customer_id == Order.customer_id,
                )
                .where(
                    Customer.customer_tg_id == tg_id,
                    Order.order_status == OrderStatus.IN_PROGRESS,
                )
            )
            return query.scalars().all()

    async def get_canceled_orders(self, tg_id: int) -> list:
        """Возвращает отмененные заказы"""

        async with self.async_session_factory() as session:
            query = await session.execute(
                select(Order)
                .join(
                    Customer,
                    Customer.customer_id == Order.customer_id,
                )
                .where(
                    Customer.customer_tg_id == tg_id,
                    Order.order_status == OrderStatus.CANCELLED,
                )
            )
            return query.scalars().all()

    async def get_completed_orders(self, tg_id: int) -> list:
        """Возвращает завершенные заказы"""

        async with self.async_session_factory() as session:
            query = await session.execute(
                select(Order)
                .join(
                    Customer,
                    Customer.customer_id == Order.customer_id,
                )
                .where(
                    Customer.customer_tg_id == tg_id,
                    Order.order_status == OrderStatus.COMPLETED,
                )
            )
            return query.scalars().all()

    # ---

    async def get_pending_orders_in_city(self, city: str) -> list:
        """Возвращает все ожидающие заказы в указанном городе"""

        async with self.async_session_factory() as session:
            query = await session.execute(
                select(Order).where(
                    Order.order_city == city, Order.order_status == OrderStatus.PENDING
                )
            )
            return query.scalars().all()

    # ---

    async def get_customer_tg_id(self, order_id: int) -> Optional[int]:
        """Возвращает Telegram ID заказчика по ID заказа"""

        async with self.async_session_factory() as session:
            query = await session.execute(
                select(Order.customer_tg_id).where(Order.order_id == order_id)
            )
            customer_tg_id = query.scalar()

            return customer_tg_id

    # ---

    async def get_courier_phone(self, order_id: int) -> Optional[str]:
        """Возвращает номер телефона курьера по ID заказа"""

        async with self.async_session_factory() as session:
            query = await session.execute(
                select(Courier.courier_phone)
                .join(Order)
                .where(Order.order_id == order_id)
            )
            courier_phone = query.scalar()
            return courier_phone

    async def get_order_by_id(self, order_id: int) -> Optional[Order]:
        """Возвращает заказ по его ID"""
        async with self.async_session_factory() as session:
            order = await session.get(Order, order_id)
            return order

    # ---

    async def get_available_orders(
        self, lat: float, lon: float, radius_km: int
    ) -> dict:
        """Возвращает доступные заказы в заданном радиусе в виде словаря."""

        async with self.async_session_factory() as session:
            query = await session.execute(
                select(Order).where(Order.order_status == OrderStatus.PENDING)
            )
            all_orders = query.scalars().all()

            available_orders = {}
            for order in all_orders:
                try:
                    start_lat = float(order.starting_point[0])
                    start_lon = float(order.starting_point[1])
                    if self.is_within_radius(
                        (lat, lon), (start_lat, start_lon), radius_km
                    ):
                        order_forma = (
                            zlib.decompress(order.order_forma).decode("utf-8")
                            if order.order_forma
                            else "-"
                        )
                        available_orders[order.order_id] = {
                            "text": order_forma,
                            "starting_point": [start_lat, start_lon],
                            "status": order.order_status.value,
                            "distance_km": order.distance_km,
                        }
                except (ValueError, TypeError) as e:
                    log.error(
                        f"Ошибка обработки координат заказа {order.order_id}: {e}"
                    )
                    continue
                except Exception as e:
                    log.error(
                        f"Ошибка декодирования order_forma для заказа {order.order_id}: {e}"
                    )
                    continue

            return available_orders

    @staticmethod
    def is_within_radius(
        courier_coords: tuple, order_coords: tuple, radius_km: int
    ) -> bool:
        """Проверяет, находится ли заказ в радиусе курьера"""
        return geodesic(courier_coords, order_coords).km <= radius_km


customer_data = CustomerData(async_session_factory)
courier_data = CourierData(async_session_factory)
order_data = OrderData(async_session_factory)


__all__ = [
    "customer_data",
    "courier_data",
    "order_data",
]
