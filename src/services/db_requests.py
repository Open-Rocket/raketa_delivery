import zlib
import asyncio
from src.models import (
    async_session_factory,
    Customer,
    Courier,
    Admin,
    Partner,
    Payment,
    SeedKey,
    GlobalSettings,
    OrderStatus,
    Order,
    Subscription,
)
from sqlalchemy import select, delete, func
from sqlalchemy.sql.functions import min
from datetime import datetime, timedelta
from sqlalchemy.engine import Result
from typing import Optional
from src.config import Time, log
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Callable
from geopy.distance import geodesic


class CustomerData:
    def __init__(self, async_session_factory: Callable[..., AsyncSession]):
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
        """Добавляет в БД нового клиента"""
        async with self.async_session_factory() as session:
            try:
                new_customer = Customer(
                    customer_tg_id=tg_id,
                    customer_name=name,
                    customer_phone=phone,
                    customer_city=city,
                    customer_accept_terms_of_use=tou,
                    customer_registration_date=await Time.get_moscow_time(),
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

    async def update_customer_name(self, tg_id: int, new_name: str):
        """Обновляет имя клиента в БД"""
        async with self.async_session_factory() as session:
            customer = await session.get(Customer, tg_id)
            customer.customer_name = new_name
            await session.commit()

    async def update_customer_phone(self, tg_id: int, new_phone: str):
        """Обновляет номер клиента в БД"""
        async with self.async_session_factory() as session:
            customer = await session.get(Customer, tg_id)
            customer.customer_phone = new_phone
            await session.commit()

    async def update_customer_city(self, tg_id: int, new_city: str):
        """Обновляет город клиента в БД"""
        async with self.async_session_factory() as session:
            customer = await session.get(Customer, tg_id)
            customer.customer_city = new_city
            await session.commit()

    # ---

    async def get_customer_info(self, tg_id: int) -> tuple:
        """Возвращает имя, номер и город клиента из БД"""
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

    # ---

    async def is_set_key(self, tg_id: int) -> bool:
        async with self.async_session_factory() as session:
            customer = await session.scalar(
                select(Customer).where(Customer.customer_tg_id == tg_id)
            )
            if customer:
                if customer.seed_key_id:
                    return True
                return False

    # ---

    async def set_customer_seed_key(self, tg_id: int, seed_key: str) -> bool:
        """Привязывает seed ключ к клиенту"""

        async with self.async_session_factory() as session:

            seed_key_obj = await session.execute(
                select(SeedKey).where(SeedKey.seed_key == seed_key)
            )
            seed_key_obj = seed_key_obj.scalar_one_or_none()

            log.info(f"seed_key_obj: {seed_key_obj}")

            if not seed_key_obj.seed_key:
                log.info(f"seed_key_obj.seed_key: {seed_key_obj.seed_key}")
                return False

            customer = await session.scalar(
                select(Customer).where(Customer.customer_tg_id == tg_id)
            )

            if customer:
                log.info(f"customer: {customer.customer_id}")
                customer.seed_key_id = seed_key_obj.seed_key_id
                customer.partner_id = seed_key_obj.partner_id
                await session.flush()
                await session.commit()
                return True

            return False

    async def get_customer_seed_key(self, tg_id: int) -> Optional[str]:
        """Возвращает seed ключ клиента"""
        async with self.async_session_factory() as session:
            customer = await session.scalar(
                select(Customer).where(Customer.customer_tg_id == tg_id)
            )
            if customer:
                seed_key = await session.scalar(
                    select(SeedKey.seed_key).where(
                        SeedKey.partner_id == customer.partner_id
                    )
                )
                return seed_key

    # ---

    async def set_customer_discount(self, tg_id: int, discount: int) -> bool:
        """Устанавливает скидку клиенту"""
        async with self.async_session_factory() as session:
            customer = await session.scalar(
                select(Customer).where(Customer.customer_tg_id == tg_id)
            )
            customer.customer_discount = discount
            await session.commit()

    async def get_customer_discount(self, tg_id: int) -> int:
        """Возвращает скидку клиента"""
        async with self.async_session_factory() as session:
            customer = await session.scalar(
                select(Customer).where(Customer.customer_tg_id == tg_id)
            )
            customer_discount = customer.customer_discount
            return customer_discount if customer_discount else 0


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
                    courier_registration_date=await Time.get_moscow_time(),
                )
                session.add(new_courier)
                await session.flush()
                await session.commit()
                return True
            except Exception as e:
                await session.rollback()
                log.error(f"Ошибка при добавлении курьера: {e}")
                return False

    async def get_courier_id(self, tg_id: int) -> int:
        """Возвращает id курьера по tg_id"""
        async with self.async_session_factory() as session:
            courier = await session.scalar(
                select(Courier).where(Courier.courier_tg_id == tg_id)
            )
            return courier.courier_id if courier else 0

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

    async def update_courier_name(self, tg_id: int, new_name: str) -> bool:
        """Обновляет имя курьера в БД"""

        async with self.async_session_factory() as session:
            courier = await session.get(Courier, tg_id)
            if not courier:
                return False

            courier.courier_name = new_name
            await session.commit()
            return True

    async def update_courier_phone(
        self,
        tg_id: int,
        new_phone: str,
    ) -> bool:
        """Обновляет номер курьера в БД"""

        async with self.async_session_factory() as session:
            courier = await session.get(Courier, tg_id)
            if not courier:
                return False

            courier.courier_phone = new_phone
            await session.commit()
            return True

    async def update_courier_city(
        self,
        tg_id: int,
        new_city: str,
    ) -> bool:
        """Обновляет город курьера в БД"""

        async with self.async_session_factory() as session:
            courier = await session.get(Courier, tg_id)
            if not courier:
                return False

            courier.courier_city = new_city
            await session.commit()
            return True

    async def update_courier_subscription(self, tg_id: int, days: int) -> bool:
        """Продлевает подписку курьера на days дней, либо создаёт новую, если её нет."""

        async with self.async_session_factory() as session:
            try:
                result = await session.execute(
                    select(Courier).where(Courier.courier_tg_id == tg_id)
                )
                courier = result.scalar_one_or_none()

                if not courier:
                    log.error(f"Курьер с tg_id={tg_id} не найден.")
                    return False

                now = await Time.get_moscow_time()

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
                        end_date=now + timedelta(days=days),
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

    # ---

    async def update_free_period(self, days: int):
        """Обновляет количество дней бесплатного периода."""
        async with self.async_session_factory() as session:
            try:
                result = await session.execute(select(GlobalSettings.free_period_days))
                free_period: GlobalSettings = result.scalar_one_or_none()

                if free_period:
                    free_period.free_period_days = days
                else:
                    free_period = GlobalSettings(free_period_days=days)
                    session.add(free_period)

                await session.commit()

            except Exception as e:
                log.error(f"Ошибка при обновлении бесплатного периода: {e}")
                await session.rollback()

    async def get_free_period(self) -> int:
        """Получает количество дней бесплатного периода."""
        async with self.async_session_factory() as session:
            try:
                result = await session.execute(select(GlobalSettings.free_period_days))
                free_period: GlobalSettings = result.scalar_one_or_none()
                return free_period.free_period_days if free_period else 10

            except Exception as e:
                log.error(f"Ошибка при получении бесплатного периода: {e}")
                return 10

    # ---

    async def set_payment(self, payer_id: int, sum: int):
        """Добавляет платёж в БД и начисляет 30% партнёру, если он есть"""
        async with self.async_session_factory() as session:
            try:
                # Добавляем новый платёж
                new_payment = Payment(
                    payment_date=await Time.get_moscow_time(),
                    payment_sum_rub=sum,
                    payer_id=payer_id,
                )
                session.add(new_payment)

                # Проверяем, есть ли у курьера партнер
                courier = await session.scalar(
                    select(Courier).where(Courier.courier_id == payer_id)
                )
                if courier and courier.partner_id:
                    partner = await session.scalar(
                        select(Partner).where(Partner.partner_id == courier.partner_id)
                    )
                    if partner:
                        partner.balance += int(
                            sum * 0.3
                        )  # Начисляем 30% от суммы платежа

                await session.commit()
                return True

            except Exception as e:
                await session.rollback()
                log.error(f"Ошибка при добавлении платежа: {e}")
                return False

    # ---

    async def set_courier_seed_key(self, tg_id: int, seed_key: str) -> bool:
        """Привязывает seed ключ к курьеру"""

        async with self.async_session_factory() as session:

            seed_key_obj = await session.execute(
                select(SeedKey).where(SeedKey.seed_key == seed_key)
            )
            seed_key_obj = seed_key_obj.scalar_one_or_none()

            log.info(f"seed_key_obj: {seed_key_obj}")

            if not seed_key_obj.seed_key:
                log.info(f"seed_key_obj.seed_key: {seed_key_obj.seed_key}")
                return False

            courier = await session.scalar(
                select(Courier).where(Courier.courier_tg_id == tg_id)
            )

            if courier:
                log.info(f"courier: {courier.courier_id}")
                courier.seed_key_id = seed_key_obj.seed_key_id
                courier.partner_id = seed_key_obj.partner_id
                await session.flush()
                await session.commit()
                return True

            return False

    async def get_courier_seed_key(self, tg_id: int) -> Optional[str]:
        """Возвращает seed ключ курьера"""
        async with self.async_session_factory() as session:
            courier = await session.scalar(
                select(Courier).where(Courier.courier_tg_id == tg_id)
            )
            if courier:
                seed_key = await session.scalar(
                    select(SeedKey.seed_key).where(
                        SeedKey.partner_id == courier.partner_id
                    )
                )
                return seed_key

    async def is_set_key(self, tg_id: int) -> bool:
        async with self.async_session_factory() as session:
            courier = await session.scalar(
                select(Courier).where(Courier.courier_tg_id == tg_id)
            )
            if courier:
                if courier.seed_key_id:
                    return True
                return False

    # ---

    async def update_courier_location(self, tg_id, my_lat: float, my_lon: float):
        """Обновляет местоположение курьера в БД"""
        async with self.async_session_factory() as session:
            try:
                courier = await session.scalar(
                    select(Courier).where(Courier.courier_tg_id == tg_id)
                )
                if not courier:
                    return False

                courier.courier_location_lat = my_lat
                courier.courier_location_lon = my_lon
                await session.commit()
                return True
            except Exception as e:
                await session.rollback()
                log.error(f"Ошибка при обновлении местоположения курьера: {e}")
                return False

    async def get_courier_last_location(self, tg_id: int) -> tuple:
        """Возвращает местоположение курьера из БД"""
        async with self.async_session_factory() as session:
            try:
                courier = await session.scalar(
                    select(Courier).where(Courier.courier_tg_id == tg_id)
                )
                if not courier:
                    return None

                return (
                    courier.courier_location_lat,
                    courier.courier_location_lon,
                )
            except Exception as e:
                log.error(f"Ошибка при получении местоположения курьера: {e}")
                return None


class AdminData:
    def __init__(self, async_session_factory: Callable[..., AsyncSession]):
        self.async_session_factory = async_session_factory

    # ---

    async def set_new_admin(
        self,
        tg_id: int,
        name: str,
        phone: str,
    ) -> bool:
        """Добавляет в БД нового администратора"""

        async with self.async_session_factory() as session:
            try:
                new_admin = Admin(
                    admin_tg_id=tg_id,
                    admin_name=name,
                    admin_phone=phone,
                )
                session.add(new_admin)
                await session.flush()
                await session.commit()
                return True
            except Exception as e:
                await session.rollback()
                log.error(f"Ошибка при добавлении администратора: {e}")
                return False

    async def get_all_admins(self) -> list:
        """Возвращает список администраторов"""

        async with self.async_session_factory() as session:
            query = await session.execute(select(Admin))
            return query.scalars().all()

    async def del_admin(self, phone: str):
        async with self.async_session_factory() as session:
            try:
                await session.execute(delete(Admin).where(Admin.admin_phone == phone))
                await session.commit()
                return True
            except Exception as e:
                await session.rollback()
                log.error(f"Ошибка при удалении администратора: {e}")
                return False

    # ---

    async def change_partner_program(self, status: bool):
        """Изменяет статут партнерской программы, включает и приостанавливает ее"""

        async with self.async_session_factory() as session:

            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()

            if settings:
                settings.partner_program_is_active = status
            else:
                settings = GlobalSettings(partner_program_is_active=status)
                session.add(settings)
            await session.commit()

    async def get_partner_program_status(self) -> bool:
        """Возвращает статус партнерской программы"""
        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()
            if not settings:
                return True

            return settings.partner_program_is_active

    # ---

    async def change_service_status(self, status: bool):
        """Изменяет статус сервиса"""
        async with self.async_session_factory() as session:

            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()

            if settings:
                settings.service_is_active = status
            else:
                settings = GlobalSettings(service_is_active=status)
                session.add(settings)

            log.info(f"Статус сервиса изменён на {status}")

            await session.commit()

    async def get_service_status(self) -> bool:
        """Возвращает статус сервиса"""
        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()
            if not settings:
                return True

            return settings.service_is_active

    # ---

    async def change_standard_order_price(self, price: int):
        """Обновляет стандартную цену заказа"""
        async with self.async_session_factory() as session:

            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()

            if settings:
                settings.order_price_per_km = price
            else:
                settings = GlobalSettings(order_price_per_km=price)
                session.add(settings)

            await session.commit()

    async def change_max_order_price(self, price: int):
        """Обновляет максимальную цену заказа"""
        async with self.async_session_factory() as session:

            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()

            if settings:
                settings.order_max_price = price
            else:
                settings = GlobalSettings(order_max_price=price)
                session.add(settings)

            await session.commit()

    async def get_order_prices(self) -> tuple:
        """Возвращает минимальную и максимальную цену заказа"""
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(
                    GlobalSettings.order_price_per_km, GlobalSettings.order_max_price
                )
            )
            settings = result.scalar_one_or_none()

            if not settings:
                return 38, 100

            if isinstance(settings, GlobalSettings):
                return (
                    settings.order_price_per_km if settings.order_price_per_km else 38,
                    settings.order_max_price if settings.order_max_price else 100,
                )
            else:

                return 38, 100

    # ---

    async def change_subscription_price(self, price: int):
        """Обновляет цену подписки"""
        async with self.async_session_factory() as session:

            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()

            if settings:
                settings.subs_price = price * 100
            else:
                settings = GlobalSettings(subs_price=price * 100)
                session.add(settings)

            await session.commit()

    async def get_subscription_price(self) -> int:
        """Возвращает цену подписки"""
        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings.subs_price))

            subs_price = result.scalar_one_or_none()
            return subs_price if subs_price is not None else 99000

    # ---

    async def change_discount_percent_courier(self, percent: int):
        """Обновляет процент скидки курьеру"""
        async with self.async_session_factory() as session:

            if percent > 75:
                percent = 75
            elif percent < 0:
                percent = 0

            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()

            if settings:
                settings.discount_percent_courier = percent
            else:
                settings = GlobalSettings(discount_percent_courier=percent)
                session.add(settings)

            await session.commit()

    async def change_first_order_discount(self, percent: int):
        """Обновляет процент скидки на первый заказ"""
        async with self.async_session_factory() as session:

            if percent > 75:
                percent = 75
            elif percent < 0:
                percent = 0

            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()

            if settings:
                settings.discount_percent_first_order = percent
            else:
                settings = GlobalSettings(discount_percent_first_order=percent)
                session.add(settings)

            await session.commit()

    async def get_discount_percent_courier(self) -> int:
        """Возвращает процент скидки для курьера."""
        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()

            if settings is not None:
                return settings.discount_percent_courier

            return 15

    async def get_first_order_discount(self) -> float:
        """Возвращает процент скидки на первый заказ"""
        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()

            if settings is not None:
                return settings.discount_percent_first_order

            return 15

    # ---

    async def change_free_period_days(self, days: int):
        """Обновляет количество дней бесплатного периода"""
        async with self.async_session_factory() as session:

            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()

            if days < 0:
                days = 0
            elif days > 30:
                days = 30

            if settings:
                settings.free_period_days = days
            else:
                settings = GlobalSettings(free_period_days=days)
                session.add(settings)

            await session.commit()

    async def get_free_period_days(self) -> int:
        """Возвращает количество дней бесплатного периода"""
        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()

            if settings is not None:
                return settings.free_period_days
            return 10

    # ---

    async def get_profit(self) -> int:
        """Возвращает прибыль сервиса"""
        async with self.async_session_factory() as session:
            result = await session.execute(select(func.sum(Payment.payment_sum_rub)))
            profit = result.scalar_one_or_none()
            return profit if profit else 0

    async def get_turnover(self) -> int:
        """Возвращает оборот сервиса"""
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(func.sum(Order.price_rub)).where(
                    Order.order_status == OrderStatus.COMPLETED
                )
            )
            turnover = result.scalar_one_or_none()
            return turnover if turnover else 0

    # ---

    async def get_all_users(self) -> tuple:
        """Возвращает количество всех пользователей"""
        async with self.async_session_factory() as session:
            customers_query = await session.execute(select(Customer))
            couriers_query = await session.execute(select(Courier))
            partners_query = await session.execute(select(Partner))

            customers = list(customers_query.scalars())
            couriers = list(couriers_query.scalars())
            partners = list(partners_query.scalars())

            return (customers, couriers, partners)

    # ---

    async def change_refund_percent(self, percent: int):
        """Обновляет процент возврата"""
        async with self.async_session_factory() as session:

            if percent > 50:
                percent = 50
            elif percent < 15:
                percent = 15

            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()

            if settings:
                settings.refund_percent = percent
            else:
                settings = GlobalSettings(refund_percent=percent)
                session.add(settings)

            await session.commit()

    async def get_refund_percent(self) -> int:
        """Возвращает процент возврата"""
        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()

            if settings is not None:
                return settings.refund_percent
            return 30

    # ---

    async def change_distance_coefficient_less_5(self, coefficient: float):
        """Обновляет коэффициент для расстояний меньше 5 км"""

        if coefficient < 0:
            coefficient = 1
        elif coefficient > 3.0:
            coefficient = 3.0

        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()

            if settings:
                settings.distance_coefficient_less_5 = coefficient
            else:
                settings = GlobalSettings(distance_coefficient_less_5=coefficient)
                session.add(settings)

    async def change_distance_coefficient_5_10(self, coefficient: float):
        """Обновляет коэффициент для расстояний от 5 до 10 км"""

        if coefficient < 0:
            coefficient = 1
        elif coefficient > 3.0:
            coefficient = 3.0

        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()

            if settings:
                settings.distance_coefficient_5_10 = coefficient
            else:
                settings = GlobalSettings(distance_coefficient_5_10=coefficient)
                session.add(settings)

    async def change_distance_coefficient_10_20(self, coefficient: float):
        """Обновляет коэффициент для расстояний от 10 до 20 км"""

        if coefficient < 0:
            coefficient = 1
        elif coefficient > 3.0:
            coefficient = 3.0

        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()

            if settings:
                settings.distance_coefficient_10_20 = coefficient
            else:
                settings = GlobalSettings(distance_coefficient_10_20=coefficient)
                session.add(settings)

    async def change_distance_coefficient_more_20(self, coefficient: float):
        """Обновляет коэффициент для расстояний больше 20 км"""

        if coefficient < 0:
            coefficient = 1
        elif coefficient > 3.0:
            coefficient = 3.0

        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()

            if settings:
                settings.distance_coefficient_more_20 = coefficient
            else:
                settings = GlobalSettings(distance_coefficient_more_20=coefficient)
                session.add(settings)

    # ---

    async def get_distance_coefficient_less_5(self) -> float:
        """Возвращает коэффициент для расстояний меньше 5 км"""
        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()

            return settings.distance_coefficient_less_5 if settings else 1.0

    async def get_distance_coefficient_5_10(self) -> float:
        """Возвращает коэффициент для расстояний от 5 до 10 км"""
        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()
            return settings.distance_coefficient_5_10 if settings else 1.0

    async def get_distance_coefficient_10_20(self) -> float:
        """Возвращает коэффициент для расстояний от 10 до 20 км"""
        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()
            return settings.distance_coefficient_10_20 if settings else 1.0

    async def get_distance_coefficient_more_20(self) -> float:
        """Возвращает коэффициент для расстояний больше 20 км"""
        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()
            return settings.distance_coefficient_more_20 if settings else 1.0

    # ---

    async def change_time_coefficient_00_06(self, coefficient: float):
        """Обновляет коэффициент для времени от 0 до 6 часов"""

        if coefficient < 0:
            coefficient = 1
        elif coefficient > 3.0:
            coefficient = 3.0

        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()

            if settings:
                settings.time_coefficient_00_06 = coefficient
            else:
                settings = GlobalSettings(time_coefficient_0_6=coefficient)
                session.add(settings)
                await session.commit()

    async def change_time_coefficient_06_12(self, coefficient: float):
        """Обновляет коэффициент для времени от 6 до 12 часов"""

        if coefficient < 0:
            coefficient = 1
        elif coefficient > 3.0:
            coefficient = 3.0

        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()

            if settings:
                settings.time_coefficient_06_12 = coefficient
            else:
                settings = GlobalSettings(time_coefficient_6_12=coefficient)
                session.add(settings)
                await session.commit()

    async def change_time_coefficient_12_18(self, coefficient: float):
        """Обновляет коэффициент для времени от 12 до 18 часов"""

        if coefficient < 0:
            coefficient = 1
        elif coefficient > 3.0:
            coefficient = 3.0

        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()

            if settings:
                settings.time_coefficient_12_18 = coefficient
            else:
                settings = GlobalSettings(time_coefficient_12_18=coefficient)
                session.add(settings)
                await session.commit()

    async def change_time_coefficient_18_21(self, coefficient: float):
        """Обновляет коэффициент для времени от 18 до 21 часов"""

        if coefficient < 0:
            coefficient = 1
        elif coefficient > 3.0:
            coefficient = 3.0

        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()

            if settings:
                settings.time_coefficient_18_21 = coefficient
            else:
                settings = GlobalSettings(time_coefficient_18_21=coefficient)
                session.add(settings)
                await session.commit()

    async def change_time_coefficient_21_00(self, coefficient: float):
        """Обновляет коэффициент для времени от 21 до 0 часов"""

        if coefficient < 0:
            coefficient = 1
        elif coefficient > 3.0:
            coefficient = 3.0

        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()

            if settings:
                settings.time_coefficient_21_00 = coefficient
            else:
                settings = GlobalSettings(time_coefficient_21_0=coefficient)
                session.add(settings)
                await session.commit()

    # ---

    async def get_time_coefficient_00_06(self) -> float:
        """Возвращает коэффициент для времени от 0 до 6 часов"""
        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()
            return settings.time_coefficient_00_06 if settings else 1.0

    async def get_time_coefficient_06_12(self) -> float:
        """Возвращает коэффициент для времени от 6 до 12 часов"""
        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()
            return settings.time_coefficient_06_12 if settings else 1.0

    async def get_time_coefficient_12_18(self) -> float:
        """Возвращает коэффициент для времени от 12 до 18 часов"""
        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()
            return settings.time_coefficient_12_18 if settings else 1.0

    async def get_time_coefficient_18_21(self) -> float:
        """Возвращает коэффициент для времени от 18 до 21 часов"""
        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()
            return settings.time_coefficient_18_21 if settings else 1.0

    async def get_time_coefficient_21_00(self) -> float:
        """Возвращает коэффициент для времени от 21 до 0 часов"""
        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()
            return settings.time_coefficient_21_00 if settings else 1.0

    # ---

    async def change_big_cities_coefficient(self, coefficient: float):
        """Обновляет коэффициент для больших городов"""

        if coefficient < 0:
            coefficient = 1
        elif coefficient > 3.0:
            coefficient = 3.0

        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()

            if settings:
                settings.big_cities_coefficient = coefficient
            else:
                settings = GlobalSettings(big_cities_coefficient=coefficient)
                session.add(settings)
                await session.commit()

    async def change_small_cities_coefficient(self, coefficient: float):
        """Обновляет коэффициент для маленьких городов"""

        if coefficient < 0:
            coefficient = 1
        elif coefficient > 3.0:
            coefficient = 3.0

        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()

            if settings:
                settings.small_cities_coefficient = coefficient
            else:
                settings = GlobalSettings(small_cities_coefficient=coefficient)
                session.add(settings)
                await session.commit()

    # ---

    async def get_big_cities_coefficient(self) -> float:
        """Возвращает коэффициент для больших городов"""
        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()
            return settings.big_cities_coefficient if settings else 1.0

    async def get_small_cities_coefficient(self) -> float:
        """Возвращает коэффициент для маленьких городов"""
        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()
            return settings.small_cities_coefficient if settings else 1.0

    # ---

    async def get_all_coefficients(self) -> dict:
        """Возвращает все коэффициенты"""
        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()
            if settings:
                return {
                    "big_cities_coefficient": settings.big_cities_coefficient,
                    "small_cities_coefficient": settings.small_cities_coefficient,
                    "distance_coefficient_less_5": settings.distance_coefficient_less_5,
                    "distance_coefficient_5_10": settings.distance_coefficient_5_10,
                    "distance_coefficient_10_20": settings.distance_coefficient_10_20,
                    "distance_coefficient_more_20": settings.distance_coefficient_more_20,
                    "time_coefficient_00_06": settings.time_coefficient_00_06,
                    "time_coefficient_06_12": settings.time_coefficient_06_12,
                    "time_coefficient_12_18": settings.time_coefficient_12_18,
                    "time_coefficient_18_21": settings.time_coefficient_18_21,
                    "time_coefficient_21_00": settings.time_coefficient_21_00,
                }
            return {}

    # ---


class PartnerData:
    def __init__(self, async_session_factory: Callable[..., AsyncSession]):
        self.async_session_factory = async_session_factory

    # ---

    async def create_new_partner(
        self,
        tg_id: int,
    ) -> int | bool:
        """Добавляет в БД нового партнера, если такого еще нет."""

        async with self.async_session_factory() as session:
            try:
                existing_partner = await session.scalar(
                    select(Partner).where(Partner.partner_tg_id == tg_id)
                )
                if existing_partner:
                    log.error(f"Партнёр с tg_id {tg_id} уже существует.")
                    return False

                new_partner = Partner(
                    partner_tg_id=tg_id,
                    partner_registration_date=await Time.get_moscow_time(),
                )
                session.add(new_partner)
                await session.flush()
                new_partner_id = new_partner.partner_id
                await session.commit()
                return new_partner_id
            except Exception as e:
                await session.rollback()
                log.error(f"Ошибка при добавлении партнера: {e}")
                return False

    # ---

    async def get_all_seed_keys(self) -> list:
        """Возвращает все seed ключи"""
        async with self.async_session_factory() as session:
            query = await session.execute(select(SeedKey))
            return query.scalars().all()

    # ---

    async def get_my_seed_key(self, tg_id: int) -> Optional[str]:
        """Возвращает seed ключ партнера"""
        async with self.async_session_factory() as session:
            partner = await session.scalar(
                select(Partner.partner_id).where(Partner.partner_tg_id == tg_id)
            )
            if partner:
                seed_key = await session.scalar(
                    select(SeedKey.seed_key).where(SeedKey.partner_id == partner)
                )
                return seed_key

    # ---

    async def create_new_seed_key(
        self,
        partner_id: int,
        key: str,
    ) -> bool:
        """Добавляет новый seed ключ"""
        async with self.async_session_factory() as session:
            try:
                new_key = SeedKey(
                    partner_id=partner_id,
                    seed_key=key,
                )
                session.add(new_key)
                await session.flush()
                await session.commit()
                return True
            except Exception as e:
                await session.rollback()
                log.error(f"Ошибка при добавлении seed ключа: {e}")
                return False

    # ---

    async def get_all_my_seed_key_referrals(self, tg_id: int) -> tuple:
        """Возвращает все seed ключи, привязанные к партнеру"""
        async with self.async_session_factory() as session:
            partner = await session.scalar(
                select(Partner).where(Partner.partner_tg_id == tg_id)
            )
            if partner:

                customer_query_seed_key = await session.execute(
                    select(Customer).where(Customer.seed_key_id == partner.partner_id)
                )
                courier_query_seed_key = await session.execute(
                    select(Courier).where(Courier.seed_key_id == partner.partner_id)
                )

                customers = customer_query_seed_key.scalars().all()
                couriers = courier_query_seed_key.scalars().all()

                return (customers, couriers)

            return ([], [])

    # ---

    async def change_partner_balance(self, tg_id: int, new_balance: int) -> None:
        """Устанавливает новый баланс партнера"""
        async with self.async_session_factory() as session:
            partner = await session.scalar(
                select(Partner).where(Partner.partner_tg_id == tg_id)
            )
            if partner:
                partner.balance = new_balance
                await session.commit()

    async def get_partner_balance(self, tg_id: int) -> int:
        """Возвращает текущий баланс партнера"""
        async with self.async_session_factory() as session:
            partner = await session.scalar(
                select(Partner).where(Partner.partner_tg_id == tg_id)
            )
        return partner.balance if partner else 0

    async def get_my_all_time_earn(self, tg_id: int) -> int:
        """Возвращает общую сумму заработка партнера (30% от подписок курьеров)"""
        async with self.async_session_factory() as session:
            partner = await session.scalar(
                select(Partner).where(Partner.partner_tg_id == tg_id)
            )
            if not partner:
                return 0

            total_earnings = await session.scalar(
                select(func.sum(Payment.payment_sum_rub * 0.3))
                .join(Courier, Courier.courier_id == Payment.payer_id)
                .where(Courier.partner_id == partner.partner_id)
            )

            return int(total_earnings or 0)

    async def get_paid_subscriptions_count(self, tg_id: int) -> int:
        """Возвращает количество оплаченных подписок курьеров, привязанных к партнеру"""
        async with self.async_session_factory() as session:
            partner = await session.scalar(
                select(Partner).where(Partner.partner_tg_id == tg_id)
            )
            if not partner:
                return 0

            paid_count = await session.scalar(
                select(func.count(Payment.payment_id))
                .join(Courier, Courier.courier_id == Payment.payer_id)
                .where(Courier.partner_id == partner.partner_id)
            )

            return int(paid_count or 0)


class OrderData:
    def __init__(self, async_session_factory: Callable[..., AsyncSession]):
        self.async_session_factory = async_session_factory

    # ---

    async def create_order(
        self,
        tg_id: int,
        data: dict,
        order_forma: str,
    ) -> int:
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
                    created_at_moscow_time=await Time.get_moscow_time(),
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

    async def get_customer_info_by_order_id(self, order_id: int) -> tuple:
        """Возвращает информацию из заказа о заказчике"""

        async with self.async_session_factory() as session:
            query = await session.execute(
                select(
                    Order.customer_name,
                    Order.customer_phone,
                    Order.customer_tg_id,
                ).where(Order.order_id == order_id)
            )
            customer_info = query.first()

            if customer_info:
                customer_name, customer_phone, customer_tg_id = customer_info
                return (customer_name, customer_phone, customer_tg_id)
            else:
                return ("...", "...", "...")

    # ---

    async def assign_courier_to_order(self, order_id: int, tg_id: int) -> bool:
        """Назначает курьера на заказ"""
        async with self.async_session_factory() as session:
            order = await session.get(Order, order_id)

            courier_query = await session.execute(
                select(
                    Courier.courier_id, Courier.courier_name, Courier.courier_phone
                ).where(Courier.courier_tg_id == tg_id)
            )
            courier_data = courier_query.first()

            if not courier_data:
                log.error(f"Курьер с tg_id={tg_id} не найден.")
                return False

            courier_id, courier_name, courier_phone = courier_data

            if not order:
                return False

            if order.courier_id is not None:
                log.error(f"Заказ {order_id} уже имеет назначенного курьера.")
                return False

            order.courier_id = courier_id
            order.courier_tg_id = tg_id
            order.courier_name = courier_name
            order.courier_phone = courier_phone
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
        self,
        order_id: int,
        new_status: OrderStatus,
    ) -> bool:
        """Обновляет статус заказа и время начала его выполнения"""

        async with self.async_session_factory() as session:
            order = await session.get(Order, order_id)
            if not order or order.order_status == new_status:
                return False

            order.order_status = new_status
            order.started_at_moscow_time = await Time.get_moscow_time()

            await session.flush()
            await session.commit()
            return True

    async def update_order_status_and_completed_time(
        self,
        order_id: int,
        new_status: OrderStatus,
        speed_kmh: float,
    ) -> bool:
        """Обновляет статус заказа и время завершения его выполнения"""

        async with self.async_session_factory() as session:
            order = await session.get(Order, order_id)
            if not order:
                log.error("Заказ не найден")
                return False

            order.order_status = new_status
            order.completed_at_moscow_time = await Time.get_moscow_time()
            order.speed_kmh = speed_kmh

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

    async def get_nearby_orders(self, lat: float, lon: float, radius_km: int) -> dict:
        """Возвращает доступные заказы в заданном радиусе в виде словаря."""

        async with self.async_session_factory() as session:

            query = await session.execute(
                select(Order).where(Order.order_status == OrderStatus.PENDING)
            )

            all_orders = query.scalars().all()
            available_orders = {}

            async def check_order(order):
                try:
                    start_lat = float(order.starting_point[0])
                    start_lon = float(order.starting_point[1])
                    if geodesic((lat, lon), (start_lat, start_lon)).km <= radius_km:
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
                except Exception as e:
                    log.error(
                        f"Ошибка декодирования order_forma для заказа {order.order_id}: {e}"
                    )

            await asyncio.gather(*[check_order(order) for order in all_orders])

            return available_orders

    async def get_pending_orders_in_city(self, city: str) -> list:
        """Возвращает все ожидающие заказы в указанном городе"""
        async with self.async_session_factory() as session:
            query = await session.execute(
                select(Order).where(
                    Order.order_city == city, Order.order_status == OrderStatus.PENDING
                )
            )

            city_orders = query.scalars().all()
            city_orders_dict = {}

            for order in city_orders:
                order_forma = (
                    zlib.decompress(order.order_forma).decode("utf-8")
                    if order.order_forma
                    else "-"
                )
                city_orders_dict[order.order_id] = {
                    "text": order_forma,
                    "starting_point": order.starting_point,
                    "status": order.order_status.value,
                    "distance_km": order.distance_km,
                }

            return city_orders_dict

    # ---

    async def get_all_orders(self) -> list:
        """Возвращает все заказы"""
        async with self.async_session_factory() as session:
            query = await session.execute(select(Order))

            all_orders = query.scalars().all()

            pending_orders = [
                order
                for order in all_orders
                if order.order_status == OrderStatus.PENDING
            ]
            active_orders = [
                order
                for order in all_orders
                if order.order_status == OrderStatus.IN_PROGRESS
            ]
            completed_orders = [
                order
                for order in all_orders
                if order.order_status == OrderStatus.COMPLETED
            ]
            canceled_orders = [
                order
                for order in all_orders
                if order.order_status == OrderStatus.CANCELLED
            ]

            return (
                pending_orders,
                active_orders,
                completed_orders,
                canceled_orders,
            )

    # ---

    async def get_fastest_order_ever(self) -> Optional[Order]:
        """Возвращает самый быстрый заказ"""
        async with self.async_session_factory() as session:
            stmt = (
                select(Order)
                .where(Order.order_status == OrderStatus.COMPLETED)
                .order_by(
                    (
                        Order.completed_at_moscow_time - Order.started_at_moscow_time
                    ).asc()
                )
                .limit(1)
            )

            query = await session.execute(stmt)
            fastest_order = query.scalars().first()
            return fastest_order if fastest_order else None


customer_data = CustomerData(async_session_factory)
courier_data = CourierData(async_session_factory)
order_data = OrderData(async_session_factory)
admin_data = AdminData(async_session_factory)
partner_data = PartnerData(async_session_factory)

__all__ = [
    "customer_data",
    "courier_data",
    "order_data",
    "admin_data",
    "partner_data",
]
