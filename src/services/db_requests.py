import zlib
import asyncio
from src.models import (
    async_session_factory,
    sync_session_factory,
    Customer,
    Courier,
    Admin,
    Partner,
    Payment,
    SeedKey,
    GlobalSettings,
    EarnRequest,
    OrderStatus,
    RefundStatus,
    Order,
    Subscription,
    CustomerClicks,
    CourierClicks,
)
from sqlalchemy import select, delete, func
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.functions import min
from datetime import datetime, timedelta
from sqlalchemy.engine import Result
from typing import Optional
from src.config import Time, log
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Callable
from geopy.distance import geodesic
from decimal import Decimal, ROUND_HALF_UP


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
            query = await session.execute(
                select(Customer).where(Customer.customer_tg_id == tg_id)
            )

            customer = query.scalar_one_or_none()

            if not customer:
                return False

            customer.customer_name = new_name
            await session.commit()

    async def update_customer_phone(self, tg_id: int, new_phone: str):
        """Обновляет номер клиента в БД"""
        async with self.async_session_factory() as session:
            query = await session.execute(
                select(Customer).where(Customer.customer_tg_id == tg_id)
            )

            customer = query.scalar_one_or_none()

            if not customer:
                return False

            customer.customer_phone = new_phone
            await session.commit()

    async def update_customer_city(self, tg_id: int, new_city: str):
        """Обновляет город клиента в БД"""
        async with self.async_session_factory() as session:
            query = await session.execute(
                select(Customer).where(Customer.customer_tg_id == tg_id)
            )

            customer = query.scalar_one_or_none()

            if not customer:
                return False

            customer.customer_city = new_city
            await session.commit()

    # ---

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

    async def get_customer_is_reg(self, tg_id: int) -> bool:
        """Возвращает статус регистрации курьера"""
        async with self.async_session_factory() as session:
            customer = await session.scalar(
                select(Customer).where(Customer.customer_tg_id == tg_id)
            )

            if customer:
                return True
            return False

    # ---
    async def get_customer_city(self, tg_id: int) -> str:
        """Возвращает город пользователя"""
        async with self.async_session_factory() as session:
            res = await session.execute(
                select(Customer.customer_city).where(Customer.customer_tg_id == tg_id)
            )

            city = res.scalar_one_or_none()

            return city

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

            if not seed_key_obj or not seed_key_obj.seed_key:
                return False

            customer = await session.scalar(
                select(Customer).where(Customer.customer_tg_id == tg_id)
            )

            if customer:
                log.info(f"customer: {customer.customer_id}")
                customer.seed_key_id = seed_key_obj.seed_key_id
                customer.partner_id = seed_key_obj.partner_id
                customer.activation_seed_date = (await Time.get_moscow_time()).date()
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

    # ---

    async def get_all_customers_tg_ids(self) -> list:
        """Возвращает список tg_id всех пользователей"""
        async with self.async_session_factory() as session:
            query = await session.execute(select(Customer.customer_tg_id))
            return query.scalars().all()

    async def get_all_customers_tg_ids_notify_status_true(self) -> list:
        """Возвращает список tg_id всех пользователей"""
        async with self.async_session_factory() as session:
            query = await session.execute(
                select(Customer.customer_tg_id).where(Customer.notify_status == True)
            )
            return query.scalars().all()

    # ---

    async def set_customer_notify_status(self, tg_id: int, status: bool) -> bool:
        """Устанавливает статус уведомлений клиента в БД"""
        async with self.async_session_factory() as session:
            try:
                result = await session.execute(
                    select(Customer).where(Customer.customer_tg_id == tg_id)
                )
                customer = result.scalar_one_or_none()

                if not customer:
                    return False

                customer.notify_status = status
                await session.commit()
                return True
            except Exception as e:
                await session.rollback()
                log.error(f"Ошибка при обновлении статуса уведомлений: {e}")
                return False

    async def get_customer_notify_status(self, tg_id: int) -> bool:
        """Возвращает статус уведомлений клиента"""
        async with self.async_session_factory() as session:
            customer = await session.scalar(
                select(Customer).where(Customer.customer_tg_id == tg_id)
            )
            if customer:
                return customer.notify_status
            return False

    # ---

    async def check_click_customer(self, tg_id: int) -> bool:
        """Сохраняет tg_id клиента в БД при первом взаимодействии с ботом"""
        async with self.async_session_factory() as session:
            try:
                existing = await session.execute(
                    select(CustomerClicks).where(CustomerClicks.customer_tg_id == tg_id)
                )
                if existing.scalar():
                    return False  # Уже кликал — ничего не делаем

                new_customer_click = CustomerClicks(
                    customer_tg_id=tg_id,
                    click_date=await Time.get_moscow_time(),
                )
                session.add(new_customer_click)
                await session.commit()
                return True
            except Exception as e:
                await session.rollback()
                log.error(f"Ошибка при добавлении первого клика клиента: {e}")
                return False


class CourierData:

    def __init__(self, async_session_factory: Callable[..., AsyncSession]):
        self.async_session_factory = async_session_factory
        self.sync_session_factory = sync_session_factory

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

    async def get_courier_tg_id(self, id: int) -> int:
        """Возвращает tg_id курьера по id"""
        async with self.async_session_factory() as session:
            courier = await session.scalar(
                select(Courier).where(Courier.courier_id == id)
            )
            return courier.courier_tg_id if courier else None

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

    async def get_count_and_sum_orders_in_my_city(
        self, tg_id: int
    ) -> tuple[int, float]:
        """Возвращает количество заказов и их общую сумму в городе курьера"""

        async with self.async_session_factory() as session:
            try:
                courier = await session.scalar(
                    select(Courier).where(Courier.courier_tg_id == tg_id)
                )
                if not courier:
                    return 0, 0.0

                orders_result = await session.execute(
                    select(Order).where(
                        (Order.order_city == courier.courier_city),
                        (Order.order_status == OrderStatus.PENDING),
                    )
                )
                orders = orders_result.scalars().all()

                count = len(orders)
                total_sum = sum(order.price_rub for order in orders if order.price_rub)

                return count, total_sum

            except Exception as e:
                log.error(f"Ошибка при получении количества и суммы заказов: {e}")
                return 0, 0.0

    async def get_all_couriers_tg_ids(self) -> list:
        """Возвращает список tg_id всех курьеров"""
        async with self.async_session_factory() as session:
            query = await session.execute(select(Courier.courier_tg_id))
            return query.scalars().all()

    async def get_all_couriers_tg_ids_notify_status_true(self) -> list:
        """Возвращает список tg_id всех курьеров"""
        async with self.async_session_factory() as session:
            query = await session.execute(
                select(Courier.courier_tg_id).where(Courier.notify_status == True)
            )
            return query.scalars().all()

    async def get_all_couriers_tg_ids_notify_status_true_in_current_city(
        self, city: str
    ) -> list:
        """Возвращает список tg_id всех курьеров в указанном городе"""
        async with self.async_session_factory() as session:
            query = await session.execute(
                select(Courier.courier_tg_id).where(
                    Courier.notify_status == True,
                    Courier.courier_city == city,
                ),
            )
            return query.scalars().all()

    # ---

    async def get_couriers_in_city(self, city) -> list:
        """Возвращает список всех курьеров в указанном городе"""
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(Courier.courier_id).where(Courier.courier_city == city)
            )
            return result.scalars().all()

    # ---

    async def set_courier_notify_status(self, tg_id: int, status: bool) -> bool:
        """Устанавливает статус уведомлений курьера в БД"""

        async with self.async_session_factory() as session:
            try:
                result = await session.execute(
                    select(Courier).where(Courier.courier_tg_id == tg_id)
                )
                courier = result.scalar_one_or_none()

                if not courier:
                    return False

                courier.notify_status = status
                await session.commit()
                return True
            except Exception as e:
                await session.rollback()
                log.error(f"Ошибка при обновлении статуса уведомлений: {e}")
                return False

    async def get_courier_notify_status(self, tg_id: int) -> bool:
        """Возвращает статус уведомлений курьера"""
        async with self.async_session_factory() as session:
            courier = await session.scalar(
                select(Courier).where(Courier.courier_tg_id == tg_id)
            )
            if courier:
                return courier.notify_status
            return False

    # ---

    async def update_courier_name(self, tg_id: int, new_name: str) -> bool:
        """Обновляет имя курьера в БД"""

        async with self.async_session_factory() as session:
            query = await session.execute(
                select(Courier).where(Courier.courier_tg_id == tg_id)
            )

            courier = query.scalar_one_or_none()

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
            query = await session.execute(
                select(Courier).where(Courier.courier_tg_id == tg_id)
            )

            courier = query.scalar_one_or_none()

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
            query = await session.execute(
                select(Courier).where(Courier.courier_tg_id == tg_id)
            )

            courier = query.scalar_one_or_none()

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

    async def get_courier_info_by_id(self, id: int) -> tuple:
        """Возвращает имя, номер и город курьера из БД по его id"""
        async with self.async_session_factory() as session:
            courier = await session.scalar(
                select(Courier).where(Courier.courier_id == id)
            )
            if courier:
                return (
                    courier.courier_name or "...",
                    courier.courier_phone or "...",
                    courier.courier_city or "...",
                )
            return ("...",) * 3

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

    async def get_courier_is_reg(self, tg_id: int) -> bool:
        """Возвращает статус регистрации курьера"""
        async with self.async_session_factory() as session:
            courier = await session.scalar(
                select(Courier).where(Courier.courier_tg_id == tg_id)
            )

            if courier:
                return True
            return False

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

                cancelled_orders = len(
                    [
                        order
                        for order in orders
                        if order.order_status == OrderStatus.CANCELLED
                    ]
                )

                total_money_earned = courier.total_earned
                total_XP_earned = courier.total_earned_XP
                total_execution_time = sum(
                    (
                        order.completed_at_moscow_time - order.started_at_moscow_time
                    ).total_seconds()
                    for order in orders
                    if order.order_status == OrderStatus.COMPLETED
                )
                total_distance = courier.covered_distance_km
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
                    cancelled_orders,
                    average_execution_time,
                    average_speed,
                    total_distance,
                    total_money_earned,
                    total_XP_earned,
                )
            return (0,) * 6

    async def get_courier_earned_today(self, tg_id: int) -> float:
        """Возвращает сумму заработка курьера за сегодня"""

        async with self.async_session_factory() as session:
            courier = await session.scalar(
                select(Courier).where(Courier.courier_tg_id == tg_id)
            )
            if not courier:
                return 0.0

            today = (await Time.get_moscow_time()).date()
            orders = await session.execute(
                select(Order).where(
                    Order.courier_id == courier.courier_id,
                    Order.order_status == OrderStatus.COMPLETED,
                    func.date(Order.completed_at_moscow_time) == today,
                )
            )
            orders = orders.scalars().all()

            total_earned = sum(order.price_rub for order in orders if order.price_rub)

            return total_earned

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
                result = await session.execute(select(GlobalSettings))
                free_period: GlobalSettings = result.scalar_one_or_none()
                return free_period.free_period_days if free_period else 10

            except Exception as e:
                log.error(f"Ошибка при получении бесплатного периода: {e}")
                return 10

    # ---

    async def set_payment(self, payer_id: int, summa: int):
        """Добавляет платёж в БД и начисляет 30% партнёру, если он есть и не заблокирован."""
        async with self.async_session_factory() as session:
            try:
                # Сохраняем платёж
                new_payment = Payment(
                    payment_date=await Time.get_moscow_time(),
                    payment_sum_rub=summa,
                    payer_id=payer_id,
                )
                session.add(new_payment)

                # Проверяем, есть ли партнёр
                courier = await session.scalar(
                    select(Courier).where(Courier.courier_id == payer_id)
                )

                if courier and courier.partner_id:
                    refund_percent = await session.scalar(
                        select(GlobalSettings.refund_percent)
                    )
                    partner = await session.scalar(
                        select(Partner).where(Partner.partner_id == courier.partner_id)
                    )

                    partner.balance += int(summa * refund_percent / 100)

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

            if not seed_key_obj or not seed_key_obj.seed_key:
                return False

            courier = await session.scalar(
                select(Courier).where(Courier.courier_tg_id == tg_id)
            )

            if courier:
                log.info(f"courier: {courier.courier_id}")
                courier.seed_key_id = seed_key_obj.seed_key_id
                courier.partner_id = seed_key_obj.partner_id
                courier.activation_seed_date = (await Time.get_moscow_time()).date()
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

    # ---

    async def update_courier_XP(self, tg_id: int, new_XP: float) -> bool:
        """Обновляет XP курьера в БД"""
        async with self.async_session_factory() as session:
            try:
                courier = await session.scalar(
                    select(Courier).where(Courier.courier_tg_id == tg_id)
                )
                if not courier:
                    return False

                xp_to_add = Decimal(str(new_XP)).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )

                courier.courier_XP += xp_to_add
                courier.total_earned_XP += xp_to_add

                log.info(f"XP курьера {tg_id} обновлён на {xp_to_add}.")
                log.info(f"Общая сумма XP курьера {tg_id}: {courier.courier_XP}.")

                await session.commit()
                return True
            except Exception as e:
                await session.rollback()
                log.error(f"Ошибка при обновлении XP курьера: {e}")
                return False

    async def get_courier_XP(self, tg_id: int) -> int:
        """Возвращает XP курьера из БД"""
        async with self.async_session_factory() as session:
            try:
                courier = await session.scalar(
                    select(Courier).where(Courier.courier_tg_id == tg_id)
                )
                if not courier:
                    return 0

                return round(courier.courier_XP, 2)
            except Exception as e:
                log.error(f"Ошибка при получении XP курьера: {e}")
                return 0

    async def update_courier_records(
        self,
        tg_id,
        count: int,
        distance: float,
        earned: float,
    ):
        """Обновляет рекорды курьера в БД"""
        async with self.async_session_factory() as session:
            try:
                courier = await session.scalar(
                    select(Courier).where(Courier.courier_tg_id == tg_id)
                )
                if not courier:
                    return False

                courier.orders_completed += count
                courier.total_earned += earned
                courier.covered_distance_km += round(distance, 2)

                await session.commit()
                return True
            except Exception as e:
                await session.rollback()
                log.error(f"Ошибка при обновлении рекордов курьера: {e}")
                return False

    # ---

    async def get_courier_seed_key_by_tg_id(self, tg_id: int) -> str | None:
        """Возвращает seed_key, привязанный к курьеру по его Telegram ID"""
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(SeedKey.seed_key)
                .join(Courier, SeedKey.seed_key_id == Courier.seed_key_id)
                .where(Courier.courier_tg_id == tg_id)
            )
            seed_key = result.scalar_one_or_none()
            return seed_key

    # ---

    async def get_courier_completed_orders_count(self, tg_id: int) -> int:
        """Возвращает количество завершённых заказов курьера"""
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(Courier.orders_completed).where(Courier.courier_tg_id == tg_id)
            )

            completed_orders_count = result.scalar_one_or_none()
            if completed_orders_count is None:
                return 0
            return completed_orders_count

    async def get_courier_total_earned_XP(self, tg_id: int) -> float:
        """Возвращает общую сумму заработанных курьером денег"""
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(Courier).where(Courier.courier_tg_id == tg_id)
            )

            courier = result.scalar_one_or_none()
            total_earned_XP = courier.total_earned_XP
            if total_earned_XP is None:
                return 0.0
            return total_earned_XP

    # ---

    async def check_click_courier(self, tg_id: int) -> bool:
        """Сохраняет tg_id курьера в БД при первом взаимодействии с ботом"""
        async with self.async_session_factory() as session:
            try:
                existing = await session.execute(
                    select(CourierClicks).where(CourierClicks.courier_tg_id == tg_id)
                )
                if existing.scalar():
                    return False  # Уже кликал — ничего не делаем

                new_courier_click = CourierClicks(
                    courier_tg_id=tg_id,
                    click_date=await Time.get_moscow_time(),
                )
                session.add(new_courier_click)
                await session.commit()
                return True
            except Exception as e:
                await session.rollback()
                log.error(f"Ошибка при добавлении первого клика курьера: {e}")
                return False


class AdminData:

    def __init__(self, async_session_factory: Callable[..., AsyncSession]):
        self.async_session_factory = async_session_factory

    # ---

    async def set_new_admin(
        self,
        name: str,
        phone: str,
    ) -> bool:
        """Добавляет в БД нового администратора"""
        async with self.async_session_factory() as session:
            try:
                new_admin = Admin(
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

    async def reg_admin_tg_id(
        self,
        tg_id: int,
        phone: str,
    ) -> bool:
        """Добавляет в БД нового администратора"""
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(Admin).where(Admin.admin_phone == phone)
            )

            admin = result.scalar_one_or_none()

            if not admin:
                return False

            try:
                admin.admin_tg_id = tg_id
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

    async def change_new_orders_notification_interval(self, interval_seconds: int):
        """Устанавливает интервал отправки уведомлений о новых заказах курьерам"""

        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))

            settings: GlobalSettings = result.scalar_one_or_none()

            if settings:
                settings.new_orders_notification_interval = interval_seconds

            else:
                settings = GlobalSettings(
                    new_orders_notification_interval=interval_seconds
                )
                session.add(session)

            await session.commit()

    async def get_new_orders_notification_interval(self) -> int:
        """Возвращает интервал отправки уведомлений о новых заказах курьерам"""
        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings = result.scalar_one_or_none()

            if not settings:
                return 14400

            return settings.new_orders_notification_interval

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
                return False

            return settings.service_is_active

    # ---

    async def change_standard_order_price(self, new_price: int):
        """Обновляет стандартную цену заказа"""
        async with self.async_session_factory() as session:

            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()

            if settings:
                settings.order_price_per_km = new_price
            else:
                settings = GlobalSettings(order_price_per_km=new_price)
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
            result = await session.execute(select(GlobalSettings))
            settings = result.scalar_one_or_none()

            if not settings:
                return 37, 70

            if isinstance(settings, GlobalSettings):
                return settings.order_price_per_km, settings.order_max_price
            else:
                return 37, 70

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

            if settings:
                return settings.free_period_days

            return 10

    # ---

    async def change_distance_radius(self, distance: int):
        """Изменяет радиус поиска заказов"""

        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()

            try:
                distance = int(distance)
            except Exception as e:
                log.error(f"Error {e}")

            if settings:
                settings.distance_radius = distance
            else:
                settings = GlobalSettings(distance_radius=distance)
                session.add(settings)

            await session.commit()

    async def get_distance_radius(self) -> int:
        """Возвращает величину радиуса поиска заказов"""

        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()

            if settings:
                return settings.distance_radius
            return 5

    # ---

    async def change_support_link(self, link: str):
        """Меняет ссылку поддержки"""

        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()

            if settings:
                settings.support_link = link
            else:
                settings = GlobalSettings(support_link=link)
                session.add(settings)

            await session.commit()

    async def get_support_link(self) -> int:
        """Возвращает ссылку на поддержку"""

        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()

            if settings:
                return settings.support_link
            return "https://t.me/Ruslan_Ch66"

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

            await session.commit()

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

            await session.commit()

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

            await session.commit()

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

            await session.commit()

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

            log.info(f"settings: {settings}")

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

    async def change_reward_for_fastest_speed(self, reward: int | float):
        """Обновляет вознаграждение за самую быструю скорость"""
        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()

            if settings:
                settings.reward_for_day_fastest_speed = float(reward)
            else:
                settings = GlobalSettings(reward_for_day_fastest_speed=float(reward))
                session.add(settings)

            await session.commit()

    async def get_reward_for_day_fastest_speed(self) -> float:
        """Возвращает вознаграждение за самую быструю дневную скорость"""
        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()
            return settings.reward_for_day_fastest_speed if settings else 0.0

    async def get_reward_for_month_fastest_speed(self) -> float:
        """Возвращает вознаграждение за самую быструю месячную скорость"""
        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()
            return settings.reward_for_month_fastest_speed if settings else 0.0

    # ---

    async def get_date_payments(self, date: datetime) -> list:
        """Возвращает все платежи за определенную дату"""
        async with self.async_session_factory() as session:
            query = await session.execute(
                select(Payment).where(
                    func.date_trunc("day", Payment.payment_date) == date
                )
            )
            payments = query.scalars().all()
            log.info(f"payments by date {date}: {payments}")
            return payments

    async def get_date_turnover(self, date: datetime) -> float:
        """Возвращает оборот за определенную дату"""
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(func.sum(Order.price_rub)).where(
                    Order.order_status == OrderStatus.COMPLETED,
                    func.date_trunc("day", Order.completed_at_moscow_time) == date,
                )
            )
            turnover = result.scalar_one_or_none()
            return turnover if turnover else 0.0

    async def get_date_profit(self, date: datetime) -> float:
        """Возвращает прибыль за определенную дату"""
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(func.sum(Payment.payment_sum_rub)).where(
                    func.date_trunc("day", Payment.payment_date) == date
                )
            )
            profit = result.scalar_one_or_none()
            return profit if profit else 0.0

    # ---

    async def get_period_payments(
        self, start_date: datetime.date, end_date: datetime.date
    ) -> list:
        """Возвращает все платежи за определенный период"""
        async with self.async_session_factory() as session:
            query = await session.execute(
                select(Payment).where(
                    func.date_trunc("day", Payment.payment_date) >= start_date,
                    func.date_trunc("day", Payment.payment_date) <= end_date,
                )
            )
            payments = query.scalars().all()
            log.info(f"payments by period {start_date}:{end_date}: {payments}")
            return payments

    async def get_turnover_by_period(
        self, start_date: datetime, end_date: datetime
    ) -> float:
        """Возвращает оборот за определенный период"""
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(func.sum(Order.price_rub)).where(
                    Order.order_status == OrderStatus.COMPLETED,
                    func.date_trunc("day", Order.completed_at_moscow_time)
                    >= start_date,
                    func.date_trunc("day", Order.completed_at_moscow_time) <= end_date,
                )
            )
            turnover = result.scalar_one_or_none()
            return turnover if turnover else 0.0

    async def get_profit_by_period(
        self, start_date: datetime, end_date: datetime
    ) -> float:
        """Возвращает прибыль за определенный период"""
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(func.sum(Payment.payment_sum_rub)).where(
                    func.date_trunc("day", Payment.payment_date) >= start_date,
                    func.date_trunc("day", Payment.payment_date) <= end_date,
                )
            )
            profit = result.scalar_one_or_none()
            return profit if profit else 0.0

    # ---

    async def get_all_payments(self) -> list:
        """Возвращает все платежи"""
        async with self.async_session_factory() as session:
            query = await session.execute(select(Payment))
            payments = query.scalars().all()
            return payments

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

    async def get_profit(self) -> int:
        """Возвращает прибыль сервиса"""
        async with self.async_session_factory() as session:
            result = await session.execute(select(func.sum(Payment.payment_sum_rub)))
            profit = result.scalar_one_or_none()
            return profit if profit else 0

    # ---

    async def change_base_order_XP(self, new_XP: float):
        """Обновляет базовый XP за заказ"""
        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()

            if settings:
                settings.base_order_XP = new_XP
            else:
                settings = GlobalSettings(base_order_XP=new_XP)
                session.add(settings)

            await session.commit()

    async def change_distance_XP(self, new_XP: float):
        """Обновляет базовый XP за расстояние"""
        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()

            if settings:
                settings.distance_XP = new_XP
            else:
                settings = GlobalSettings(distance_XP=new_XP)
                session.add(settings)

            await session.commit()

    async def change_speed_XP(self, new_XP: float):
        """Обновляет базовый XP за скорость"""
        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()

            if settings:
                settings.speed_XP = new_XP
            else:
                settings = GlobalSettings(speed_XP=new_XP)
                session.add(settings)

            await session.commit()

    # ---

    async def get_base_order_XP(self) -> float:
        """Возвращает базовый XP за заказ"""
        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()
            return settings.base_order_XP if settings else 0.0

    async def get_distance_XP(self) -> float:
        """Возвращает базовый XP за расстояние"""
        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()
            return settings.distance_XP if settings else 0.0

    async def get_speed_XP(self) -> float:
        """Возвращает базовый XP за скорость"""
        async with self.async_session_factory() as session:
            result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = result.scalar_one_or_none()
            return settings.speed_XP if settings else 0.0

    # ---

    async def get_courier_info_by_max_distance_covered_ever(self) -> tuple | None:
        """Возвращает курьера, который прошел наибольшее расстояние за все время"""
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(Courier).order_by(Courier.covered_distance_km.desc()).limit(1)
            )

            courier = result.scalar_one_or_none()
            if not courier:
                return (None,) * 2

            return courier.courier_id, courier.covered_distance_km

    async def get_courier_info_by_max_orders_count_ever(self) -> tuple | None:
        """Возвращает курьера, который выполнил наибольшее количество заказов за все время"""
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(Courier).order_by(Courier.orders_completed.desc()).limit(1)
            )

            courier = result.scalar_one_or_none()
            if not courier:
                return (None,) * 2

            return courier.courier_id, courier.orders_completed

    async def get_courier_info_by_max_earned_ever(self) -> tuple | None:
        """Возвращает курьера, который заработал больше всех за все время"""
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(Courier).order_by(Courier.total_earned.desc()).limit(1)
            )

            courier = result.scalar_one_or_none()
            if not courier:
                return (None,) * 2

            return courier.courier_id, courier.total_earned

    # ---

    async def get_courier_info_by_max_date_distance_covered(
        self, date: datetime
    ) -> tuple | None:
        """
        Возвращает курьера, который прошел наибольшее расстояние за указанный день,
        на основе всех выполненных заказов.
        """
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(
                    Order.courier_id,
                    func.sum(Order.distance_km).label("total_distance"),
                )
                .where(
                    Order.order_status == OrderStatus.COMPLETED,
                    func.date_trunc("day", Order.completed_at_moscow_time) == date,
                )
                .group_by(Order.courier_id)
                .order_by(func.sum(Order.distance_km).desc())
                .limit(1)
            )

            row = result.first()
            if not row:
                return (None,) * 2

            courier_id, total_distance = row
            return courier_id, total_distance

    async def get_courier_info_by_max_date_orders_count(
        self, date: datetime
    ) -> tuple | None:
        """
        Возвращает курьера, который выполнил наибольшее количество заказов за указанный день.
        """
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(
                    Order.courier_id, func.count(Order.order_id).label("total_orders")
                )
                .where(
                    Order.order_status == OrderStatus.COMPLETED,
                    func.date_trunc("day", Order.completed_at_moscow_time) == date,
                )
                .group_by(Order.courier_id)
                .order_by(func.count(Order.order_id).desc())
                .limit(1)
            )

            row = result.first()
            if not row:
                return (None,) * 2

            courier_id, total_orders = row
            return courier_id, total_orders

    async def get_courier_info_by_max_date_earnings(
        self, date: datetime
    ) -> tuple | None:
        """
        Возвращает курьера, который заработал больше всех за указанный день.
        """
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(
                    Order.courier_id, func.sum(Order.price_rub).label("total_earnings")
                )
                .where(
                    Order.order_status == OrderStatus.COMPLETED,
                    func.date_trunc("day", Order.completed_at_moscow_time) == date,
                )
                .group_by(Order.courier_id)
                .order_by(func.sum(Order.price_rub).desc())
                .limit(1)
            )

            row = result.first()
            if not row:
                return (None,) * 2

            courier_id, total_earnings = row
            return courier_id, total_earnings

    # ---

    async def get_courier_info_by_max_period_distance_covered(
        self, start_date: datetime, end_date: datetime
    ) -> tuple | None:
        """
        Возвращает курьера, который прошел наибольшее расстояние за указанный период,
        на основе всех выполненных заказов.
        """
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(
                    Order.courier_id,
                    func.sum(Order.distance_km).label("total_distance"),
                )
                .where(
                    Order.order_status == OrderStatus.COMPLETED,
                    func.date_trunc("day", Order.completed_at_moscow_time)
                    >= start_date,
                    func.date_trunc("day", Order.completed_at_moscow_time) <= end_date,
                )
                .group_by(Order.courier_id)
                .order_by(func.sum(Order.distance_km).desc())
                .limit(1)
            )

            row = result.first()
            if not row:
                return (None,) * 2

            courier_id, total_distance = row
            return courier_id, total_distance

    async def get_courier_info_by_max_period_orders_count(
        self, start_date: datetime, end_date: datetime
    ) -> tuple | None:
        """
        Возвращает курьера, который выполнил наибольшее количество заказов за указанный период.
        """
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(
                    Order.courier_id, func.count(Order.order_id).label("total_orders")
                )
                .where(
                    Order.order_status == OrderStatus.COMPLETED,
                    func.date_trunc("day", Order.completed_at_moscow_time)
                    >= start_date,
                    func.date_trunc("day", Order.completed_at_moscow_time) <= end_date,
                )
                .group_by(Order.courier_id)
                .order_by(func.count(Order.order_id).desc())
                .limit(1)
            )

            row = result.first()
            if not row:
                return (None,) * 2

            courier_id, total_orders = row
            return courier_id, total_orders

    async def get_courier_info_by_max_period_earnings(
        self, start_date: datetime, end_date: datetime
    ) -> tuple | None:
        """
        Возвращает курьера, который заработал больше всех за указанный период.
        """
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(
                    Order.courier_id,
                    func.sum(Order.price_rub).label("total_earnings"),
                )
                .where(
                    Order.order_status == OrderStatus.COMPLETED,
                    func.date_trunc("day", Order.completed_at_moscow_time)
                    >= start_date,
                    func.date_trunc("day", Order.completed_at_moscow_time) <= end_date,
                )
                .group_by(Order.courier_id)
                .order_by(func.sum(Order.price_rub).desc())
                .limit(1)
            )

            row = result.first()
            if not row:
                return (None,) * 2

            courier_id, total_earnings = row
            return courier_id, total_earnings

    # ---

    async def get_customer_full_info_by_ID(
        self,
        id: int,
    ) -> tuple:
        """Возвращает всю информацию о клиенте по его ID"""
        async with self.async_session_factory() as session:
            customer = await session.scalar(
                select(Customer).where(Customer.customer_id == id)
            )

            if customer:
                return (
                    customer.customer_tg_id or None,
                    customer.customer_name or None,
                    customer.customer_phone or None,
                    customer.customer_city or None,
                    customer.is_blocked or None,
                )
            return (None,) * 5

    async def get_courier_full_info_by_ID(
        self,
        id: int,
    ) -> tuple:
        """Возвращает всю информацию о клиенте по его ID"""
        async with self.async_session_factory() as session:
            courier = await session.scalar(
                select(Courier).where(Courier.courier_id == id)
            )

            if courier:
                return (
                    courier.courier_tg_id or None,
                    courier.courier_name or None,
                    courier.courier_phone or None,
                    courier.courier_city or None,
                    courier.courier_XP or 0,
                    courier.is_blocked or None,
                )
            return (None,) * 6

    async def get_partner_full_info_by_SEED(
        self,
        seed: str,
    ) -> tuple:
        """Возвращает всю информацию о клиенте по его ID"""
        async with self.async_session_factory() as session:
            res = await session.execute(
                select(Partner)
                .join(SeedKey)
                .options(selectinload(Partner.seed_key))
                .where(SeedKey.seed_key == seed)
            )

            partner = res.scalar_one_or_none()

            if partner:
                return (
                    partner.partner_tg_id or None,
                    partner.balance or None,
                    partner.is_blocked or None,
                )
            return (None,) * 3

    # ---

    async def change_customer_block_status(
        self,
        id: int,
        block_status: bool,
    ):
        """Изменяет статус блокировки клиента"""
        async with self.async_session_factory() as session:
            customer = await session.scalar(
                select(Customer).where(Customer.customer_id == id)
            )
            customer.is_blocked = block_status
            await session.commit()

    async def change_courier_block_status(
        self,
        id: int,
        block_status: bool,
    ):
        """Изменяет статус блокировки курьера"""
        async with self.async_session_factory() as session:
            courier = await session.scalar(
                select(Courier).where(Courier.courier_id == id)
            )
            courier.is_blocked = block_status
            await session.commit()

    async def change_partner_block_status(
        self,
        seed: int,
        block_status: bool,
    ):
        """Изменяет статус блокировки курьера"""
        async with self.async_session_factory() as session:
            res = await session.execute(
                select(Partner)
                .join(SeedKey)
                .options(selectinload(Partner.seed_key))
                .where(SeedKey.seed_key == seed)
            )
            partner = res.scalar_one_or_none()
            partner.is_blocked = block_status
            await session.commit()

    # ---

    async def get_customer_block_status(self, tg_id: int) -> bool:
        """Возвращает статус блокировки клиента"""
        async with self.async_session_factory() as session:
            status = await session.scalar(
                select(Customer.is_blocked).where(Customer.customer_tg_id == tg_id)
            )
            return bool(status)

    async def get_courier_block_status(self, tg_id: int) -> bool:
        """Возвращает статус блокировки курьера"""
        async with self.async_session_factory() as session:
            status = await session.scalar(
                select(Courier.is_blocked).where(Courier.courier_tg_id == tg_id)
            )
            return bool(status)

    async def get_partner_block_status(self, tg_id: int) -> bool:
        """Возвращает статус блокировки партнера"""
        async with self.async_session_factory() as session:
            status = await session.scalar(
                select(Partner.is_blocked).where(Partner.partner_tg_id == tg_id)
            )
            return bool(status)

    # ---

    async def change_courier_max_active_orders_count(self, new_count: int) -> int:
        """Возвращает количество активных заказов у курьера"""
        async with self.async_session_factory() as session:
            query = await session.execute(select(GlobalSettings))
            settings = query.scalar_one_or_none()
            if settings:
                settings.max_orders_count = new_count
            else:
                settings = GlobalSettings(max_orders_count=new_count)
                session.add(settings)

            await session.commit()

    async def get_courier_max_active_orders_count(self) -> int:
        """Получает текущее значение максимального количества активных заказов у курьера"""
        async with self.async_session_factory() as session:
            query = await session.execute(select(GlobalSettings))
            settings = query.scalar_one_or_none()
            if settings:
                return settings.max_orders_count
            return 3

    # ---

    async def update_taxi_orders_count(self, value: int):
        """Увеличивает счетчик заказов на такси"""
        async with self.async_session_factory() as session:
            res: Result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = res.scalar_one_or_none()
            if settings:
                settings.taxi_orders_count += value
            else:
                settings = GlobalSettings(taxi_orders_count=value)
                session.add(settings)

            await session.commit()

    async def get_taxi_orders_count(self) -> int:
        """Возвращает текущий счётчик заказов на такси"""
        async with self.async_session_factory() as session:
            res: Result = await session.execute(select(GlobalSettings))
            settings: GlobalSettings = res.scalar_one_or_none()
            return settings.taxi_orders_count if settings else 0

    # ---

    async def change_task_status(self, task_status: bool):
        """Изменяет флаг активности воркера уведомлений"""
        async with self.async_session_factory() as session:
            query = await session.execute(select(GlobalSettings))
            settings = query.scalar_one_or_none()
            if settings:
                settings.task_status = task_status
            else:
                settings = GlobalSettings(task_status=task_status)
                session.add(settings)

            await session.commit()

    async def get_task_status(self) -> bool:
        """Возвращает флаг активности воркера уведомлений"""
        async with self.async_session_factory() as session:
            query = await session.execute(select(GlobalSettings.task_status))
            value = query.scalar_one_or_none()
            return value if value is not None else True


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

    async def get_partner_id_by_tg_id(self, tg_id: int) -> Optional[int]:
        """Возвращает ID партнера по его Telegram ID"""
        async with self.async_session_factory() as session:
            query = await session.execute(
                select(Partner).where(Partner.partner_tg_id == tg_id)
            )

            partner = query.scalar_one_or_none()

            return partner.partner_id if partner else None

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

    # ---

    async def create_new_earn_request(
        self,
        seed_key: str,
        tg_id: int,
        user_link: str,
        amount: int,
    ) -> bool:
        """Создает новый запрос на выплату заработка или перезаписывает старый, если он еще не был обработан"""
        async with self.async_session_factory() as session:
            try:
                partner = await session.scalar(
                    select(Partner).where(Partner.partner_tg_id == tg_id)
                )
                if not partner:
                    return False

                existing_request = await session.scalar(
                    select(EarnRequest).where(
                        EarnRequest.partner_tg_id == tg_id,
                        EarnRequest.refund_status == RefundStatus.WAITING,
                    )
                )

                current_time = await Time.get_moscow_time()

                if existing_request:
                    existing_request.partner_user_link = user_link
                    existing_request.amount = amount
                    existing_request.request_date = current_time
                    existing_request.partner_seed = seed_key
                    await session.flush()
                else:
                    request = EarnRequest(
                        partner_id=partner.partner_id,
                        partner_tg_id=tg_id,
                        partner_user_link=user_link,
                        partner_seed=seed_key,
                        request_date=current_time,
                        amount=amount,
                        refund_status=RefundStatus.WAITING,
                    )
                    session.add(request)
                    await session.flush()

                await session.commit()
                return True
            except Exception as e:
                await session.rollback()
                log.error(f"Ошибка при добавлении запроса на выплату: {e}")
                return False

    async def get_all_waiting_earn_requests(self) -> dict:
        """Возвращает словарь всех ожидающих выплат с данными по каждому запросу"""
        async with self.async_session_factory() as session:
            query = await session.execute(
                select(EarnRequest).where(
                    EarnRequest.refund_status == RefundStatus.WAITING
                )
            )
            requests = query.scalars().all()

            result = {
                request.earn_request_id: (
                    request.partner_seed,
                    request.partner_tg_id,
                    request.partner_user_link,
                    request.amount,
                    request.request_date.strftime("%d.%m.%Y %H:%M"),
                )
                for request in requests
            }

            return result

    async def get_all_earn_requests(self) -> list:
        """Возвращает все запросы на выплату заработка"""
        async with self.async_session_factory() as session:
            query = await session.execute(select(EarnRequest))
            requests = query.scalars().all()

            result = {
                request.earn_request_id: (
                    request.partner_tg_id,
                    request.partner_user_link,
                    request.amount,
                    request.request_date.strftime("%d.%m.%Y %H:%M"),
                    (
                        "Оплачено"
                        if request.refund_status == RefundStatus.PAID
                        else "Ожидает"
                    ),
                )
                for request in requests
            }

            return result

    async def get_waiting_earn_request_by_id(self, request_id: int) -> tuple:
        """Возвращает запрос на выплату заработка по ID"""
        async with self.async_session_factory() as session:
            query = await session.execute(
                select(EarnRequest).where(
                    EarnRequest.earn_request_id == request_id,
                    EarnRequest.refund_status == RefundStatus.WAITING,
                )
            )
            request = query.scalar_one_or_none()

            if not request:
                return (
                    None,
                    None,
                    None,
                    None,
                )

            return (
                request.partner_tg_id,
                request.partner_user_link,
                request.amount,
                request.request_date.strftime("%d.%m.%Y %H:%M"),
            )

    async def update_earn_request_status_and_balance(
        self,
        request_id: int,
        partner_tg_id: int,
    ) -> bool:
        """Обновляет статус запроса на выплату заработка и баланс партнера"""
        async with self.async_session_factory() as session:
            try:

                request = await session.execute(
                    select(EarnRequest).where(
                        EarnRequest.earn_request_id == request_id,
                    )
                )
                request = request.scalar_one_or_none()
                if not request:
                    return False

                partner = await session.execute(
                    select(Partner).where(
                        Partner.partner_tg_id == partner_tg_id,
                    )
                )
                partner = partner.scalar_one_or_none()
                if not partner:
                    return False

                request.refund_status = RefundStatus.PAID

                partner.balance = 0

                session.add(request)
                session.add(partner)
                await session.commit()

                return True
            except Exception as e:
                await session.rollback()
                log.error(f"Ошибка при обновлении запроса или партнера: {e}")
                return False

    # ---

    async def set_min_refund_amount(self, amount: int):
        """Устанавливает минимальную сумму возврата"""
        async with self.async_session_factory() as session:
            settings = await session.scalar(select(GlobalSettings))
            if settings:
                settings.min_refund_amount = amount
            else:
                settings = GlobalSettings(min_refund_amount=amount)
                session.add(settings)
            await session.commit()

    async def set_max_refund_amount(self, amount: int):
        """Устанавливает минимальную сумму возврата"""
        async with self.async_session_factory() as session:
            settings = await session.scalar(select(GlobalSettings))
            if settings:
                settings.max_refund_amount = amount
            else:
                settings = GlobalSettings(max_refund_amount=amount)
                session.add(settings)
            await session.commit()

    async def get_min_refund_amount(self) -> int:
        """Возвращает минимальную сумму выплаты партнеру"""
        async with self.async_session_factory() as session:
            settings = await session.scalar(select(GlobalSettings))
            return settings.min_refund_amount if settings else 0

    async def get_max_refund_amount(self) -> int:
        """Возвращает максимальную сумму выплаты партнеру"""
        async with self.async_session_factory() as session:
            settings = await session.scalar(select(GlobalSettings))
            return settings.max_refund_amount if settings else 0

    # ---

    async def get_all_partners_tg_ids(self) -> list:
        """Возвращает список tg_id всех партнеров"""
        async with self.async_session_factory() as session:
            query = await session.execute(select(Partner.partner_tg_id))
            return query.scalars().all()

    # ---

    async def get_seed_key_by_partner_tg_id(self, tg_id: int) -> str | None:
        """Возвращает seed_key по Telegram ID партнёра"""
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(SeedKey.seed_key)
                .join(Partner)
                .where(Partner.partner_tg_id == tg_id)
            )
            seed_key = result.scalar_one_or_none()
            return seed_key


class OrderData:

    def __init__(self, async_session_factory: Callable[..., AsyncSession]):
        self.async_session_factory = async_session_factory

    # ---

    async def create_order(
        self,
        tg_id: int,
        username: str,
        data: dict,
        order_forma: str,
        hide_phone_forma: str,
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
                    customer_username=username,
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
                    hide_phone_forma=hide_phone_forma,
                    order_status=OrderStatus.PENDING,
                )

                session.add(new_order)
                await session.flush()
                order_id = new_order.order_id

            await session.commit()

        return order_id

    # ---

    async def get_courier_tg_id_by_order_id(self, order_id: int) -> Optional[int]:
        """Возвращает tg_id курьера по номеру заказа"""
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(Order.courier_tg_id).where(Order.order_id == order_id)
            )
            return result.scalar_one_or_none()

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
                # OrderStatus.IN_PROGRESS,
                OrderStatus.COMPLETED,
                OrderStatus.CANCELLED,
            ):
                return False

            if new_status == OrderStatus.CANCELLED:
                order.cancelled_at_moscow_time = await Time.get_moscow_time()

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
        courier_username: str,
        new_status: OrderStatus,
        execution_time_seconds: int,
        speed_kmh: float,
    ) -> bool:
        """Обновляет статус заказа и время завершения его выполнения"""

        async with self.async_session_factory() as session:
            order = await session.get(Order, order_id)
            if not order:
                log.error("Заказ не найден")
                return False

            order.order_status = new_status
            order.courier_username = courier_username
            order.completed_at_moscow_time = await Time.get_moscow_time()
            order.speed_kmh = speed_kmh
            order.execution_time_seconds = execution_time_seconds

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
                .order_by(Order.created_at_moscow_time.desc())
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
                .order_by(Order.created_at_moscow_time.desc())
            )
            return query.scalars().all()

    async def get_active_courier_orders(self, tg_id: int) -> list:
        """Возвращает активные заказы курьера"""

        async with self.async_session_factory() as session:
            query = await session.execute(
                select(Order)
                .join(
                    Courier,
                    Courier.courier_id == Order.courier_id,
                )
                .where(
                    Courier.courier_tg_id == tg_id,
                    Order.order_status == OrderStatus.IN_PROGRESS,
                )
                .order_by(Order.created_at_moscow_time.desc())
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
                .order_by(Order.completed_at_moscow_time.desc())
            )
            return query.scalars().all()

    async def get_completed_courier_orders(self, tg_id: int) -> list:
        """Возвращает завершенные заказы"""

        async with self.async_session_factory() as session:
            query = await session.execute(
                select(Order)
                .join(
                    Courier,
                    Courier.courier_id == Order.courier_id,
                )
                .where(
                    Courier.courier_tg_id == tg_id,
                    Order.order_status == OrderStatus.COMPLETED,
                )
                .order_by(Order.completed_at_moscow_time.desc())
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
                select(Order)
                .where(Order.order_status == OrderStatus.PENDING)
                .order_by(Order.created_at_moscow_time.desc())
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
                        hide_order_forma = (
                            zlib.decompress(order.hide_phone_forma).decode("utf-8")
                            if order.hide_phone_forma
                            else "-"
                        )
                        available_orders[order.order_id] = {
                            "text": order_forma,
                            "hide_phone_text": hide_order_forma,
                            "starting_point": [start_lat, start_lon],
                            "status": order.order_status.value,
                            "distance_km": order.distance_km,
                            "price_rub": order.price_rub,
                        }
                except (ValueError, TypeError) as e:
                    log.warning(
                        f"Ошибка обработки координат заказа {order.order_id}: {e}"
                    )
                except Exception as e:
                    log.error(
                        f"Ошибка декодирования order_forma для заказа {order.order_id}: {e}"
                    )

            await asyncio.gather(*[check_order(order) for order in all_orders])

            return available_orders

    async def get_pending_orders_in_city(self, city: str) -> dict:
        """Возвращает все ожидающие заказы в указанном городе"""
        async with self.async_session_factory() as session:
            query = await session.execute(
                select(Order)
                .where(
                    Order.order_city == city,
                    Order.order_status == OrderStatus.PENDING,
                )
                .order_by(Order.created_at_moscow_time.desc())
            )

            city_orders = query.scalars().all()
            city_orders_dict = {}

            for order in city_orders:
                order_forma = (
                    zlib.decompress(order.order_forma).decode("utf-8")
                    if order.order_forma
                    else "-"
                )
                hide_order_forma = (
                    zlib.decompress(order.hide_phone_forma).decode("utf-8")
                    if order.hide_phone_forma
                    else "-"
                )
                city_orders_dict[order.order_id] = {
                    "text": order_forma,
                    "hide_phone_text": hide_order_forma,
                    "starting_point": order.starting_point,
                    "status": order.order_status.value,
                    "distance_km": order.distance_km,
                    "price_rub": order.price_rub,
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

    async def get_fastest_order_speed_ever(self) -> Optional[float]:
        """Возвращает скорость самого быстрого заказа"""
        async with self.async_session_factory() as session:
            stmt = (
                select(Order)
                .where(Order.order_status == OrderStatus.COMPLETED)
                .order_by((Order.execution_time_seconds).asc())
                .limit(1)
            )

            query = await session.execute(stmt)
            order = query.scalar_one_or_none()

            if order:
                log.info(f"Скорость самого быстрого заказа: {order.speed_kmh}")
                return order.courier_id, order.speed_kmh
            return (None,) * 2

    async def get_fastest_order_by_date(self, date: datetime) -> Optional[Order]:
        """Возвращает самый быстрый заказ за указанную дату"""
        async with self.async_session_factory() as session:
            try:

                result = await session.execute(
                    select(Order)
                    .where(
                        func.date_trunc("day", Order.completed_at_moscow_time) == date,
                        Order.order_status == OrderStatus.COMPLETED,
                    )
                    .order_by((Order.speed_kmh).desc())
                )
                fastest_order = result.scalars().first()
                return (
                    (
                        fastest_order.order_id,
                        fastest_order.courier_tg_id,
                        fastest_order.courier_name,
                        fastest_order.courier_username,
                        fastest_order.courier_phone,
                        fastest_order.order_city,
                        fastest_order.speed_kmh,
                        fastest_order.distance_km,
                        fastest_order.execution_time_seconds,
                    )
                    if fastest_order
                    else (None,) * 9
                )
            except Exception as e:
                log.error(f"Ошибка при получении самого быстрого заказа: {e}")
                return (None,) * 9

    async def get_fastest_order_by_period(
        self, date_1: datetime, date_2: datetime
    ) -> Optional[Order]:
        """Возвращает самый быстрый заказ за указанный период"""
        async with self.async_session_factory() as session:
            try:
                result = await session.execute(
                    select(Order)
                    .where(
                        func.date_trunc("day", Order.completed_at_moscow_time)
                        >= date_1,
                        func.date_trunc("day", Order.completed_at_moscow_time)
                        <= date_2,
                        (Order.order_status) == OrderStatus.COMPLETED,
                    )
                    .order_by((Order.speed_kmh).desc())
                )
                fastest_order = result.scalars().first()
                return (
                    (
                        fastest_order.order_id,
                        fastest_order.courier_tg_id,
                        fastest_order.courier_name,
                        fastest_order.courier_username,
                        fastest_order.courier_phone,
                        fastest_order.order_city,
                        fastest_order.speed_kmh,
                        fastest_order.distance_km,
                        fastest_order.execution_time_seconds,
                    )
                    if fastest_order
                    else (None,) * 9
                )
            except Exception as e:
                log.error(f"Ошибка при получении самого быстрого заказа: {e}")
                return (None,) * 9

    # ---

    async def get_order_dict_by_id(self, order_id: int) -> dict | None:
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(Order).where(Order.order_id == order_id)
            )
            order: Order = result.scalar_one_or_none()

            if not order:
                return None

            return {
                "order_id": order.order_id,
                "order_city": order.order_city,
                "order_status": (
                    order.order_status.value if order.order_status else None
                ),
                "customer_id": order.customer_id,
                "customer_name": order.customer_name,
                "customer_phone": order.customer_phone,
                "courier_id": order.courier_id,
                "courier_name": order.courier_name,
                "courier_phone": order.courier_phone,
                "created_at_moscow_time": (
                    str(order.created_at_moscow_time)
                    if order.created_at_moscow_time
                    else None
                ),
                "started_at_moscow_time": (
                    str(order.started_at_moscow_time)
                    if order.started_at_moscow_time
                    else None
                ),
                "completed_at_moscow_time": (
                    str(order.completed_at_moscow_time)
                    if order.completed_at_moscow_time
                    else None
                ),
                "distance_km": order.distance_km,
                "execution_time_seconds": order.execution_time_seconds,
                "speed_kmh": order.speed_kmh,
                "delivery_object": order.delivery_object,
                "price_rub": order.price_rub,
                "description": order.description,
            }

    # ---

    async def get_count_and_sum_orders_in_city(self, city) -> tuple:
        """Возвращает количество заказов и их общую сумму в каждом городе"""
        async with self.async_session_factory() as session:
            res = await session.execute(
                select(
                    func.count(Order.order_id),
                    func.coalesce(func.sum(Order.price_rub), 0),
                ).where(
                    Order.order_city == city,
                    Order.order_status == OrderStatus.PENDING,
                )
            )
            count_orders, total_price = res.one()
            return count_orders, total_price


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
