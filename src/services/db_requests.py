from src.models import async_session_factory, Customer, Courier, OrderStatus, Order
from sqlalchemy import select, and_, func, update
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from src.config import moscow_time, log
from .routing import route


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
        """Добавляет в БД нового пользователя."""

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
                    customer_name=data.get("customer_name"),
                    customer_phone=data.get("customer_phone"),
                    description=data.get("description"),
                    distance_km=data.get("distance"),
                    price_rub=data.get("price"),
                    created_at_moscow_time=data.get("order_time"),
                    full_rout=data.get("yandex_maps_url"),
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

    async def assign_courier_to_order(self, order_id: int, courier_id: int) -> bool:
        """Назначает курьера на заказ"""

        async with self.async_session_factory() as session:
            order = await session.get(Order, order_id)
            if not order:
                return False

            order.courier_id = courier_id
            await session.flush()
            await session.commit()
            return True

    # ---

    async def update_order_status(self, order_id: int, new_status: OrderStatus) -> bool:
        """Обновляет статус заказа"""

        async with self.async_session_factory() as session:
            order = await session.get(Order, order_id)
            if not order or order.order_status == new_status:
                return False

            order.order_status = new_status
            await session.flush()
            await session.commit()
            return True

    async def update_order_status_and_time(
        self, order_id: int, new_status: OrderStatus, completed_time: datetime
    ) -> bool:
        """Обновляет статус заказа и время его выполнения"""

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


customer_data = CustomerData(async_session_factory)
courier_data = CourierData(async_session_factory)
order_data = OrderData(async_session_factory)


__all__ = ["customer_data", "courier_data", "order_data"]
