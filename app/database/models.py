import os
from datetime import datetime
from typing import Optional, Annotated
from sqlalchemy import ForeignKey, String, BigInteger, Enum, Boolean, DateTime, Text, Float, Date, func, MetaData, text, \
    Table, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship, MappedColumn
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy import Column, Integer
from dotenv import load_dotenv
import enum
import pytz

from app.database.config_db import settings

load_dotenv()

intPK = Annotated[int, mapped_column(Integer, primary_key=True)]
str_256 = Annotated[str, 256]

sqlalchemy_url = os.getenv("SQLALCHEMY_URL")
engine = create_async_engine(url=settings.DB_URL_asyncpg, echo=False)  # pool_size=5, max_overflow=10
async_session_factory = async_sessionmaker(engine)

moscow_time = datetime.now(pytz.timezone("Europe/Moscow")).replace(tzinfo=None, microsecond=0)
utc_time = datetime.now(pytz.timezone("utc")).replace(tzinfo=None, microsecond=0)


# Enums


class Base(AsyncAttrs, DeclarativeBase):
    # type_annotation_map = {
    #     str_256: String(256)
    #
    # }

    repr_cols_num = 3
    repr_cols = tuple()

    def __repr__(self):
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")
        return f"<{self.__class__.__name__}{','.join(cols)}>"


class AssociateTables:
    # Ассоциативная таблица для связывания заказов и курьеров
    order_courier_association = Table(
        'order_courier_association', Base.metadata,
        Column('order_id', Integer, ForeignKey('orders.order_id')),
        Column('courier_id', Integer, ForeignKey('users.user_id'))
    )

    # Ассоциативная таблица для связывания заказов и клиентов
    order_customer_association = Table(
        'order_customer_association', Base.metadata,
        Column('order_id', Integer, ForeignKey('orders.order_id')),
        Column('customer_id', Integer, ForeignKey('users.user_id'))
    )


class Role(enum.Enum):
    undefined = "undefined"
    courier = "Курьер"
    customer = "Клиент"


class OrderStatus(enum.Enum):
    PENDING = "Ожидается курьер"
    IN_PROGRESS = "В пути"
    COMPLETED = "Доставлено"
    CANCELLED = "Отменено"


class SubscriptionType(enum.Enum):
    ONE_DAY = 1
    TEN_DAYS = 10
    ONE_MONTH = 30


# Таблицы

class User(Base):
    __tablename__ = "users"

    # Поля
    user_id: Mapped[intPK]  # Основной ID пользователя
    user_tg_id: Mapped[int] = mapped_column(BigInteger)
    user_name: Mapped[str] = mapped_column(String(100), nullable=True)
    user_email: Mapped[str] = mapped_column(String(255), nullable=True)
    user_phone_number: Mapped[str] = mapped_column(String(20), nullable=True)
    user_registration_date: Mapped[datetime] = mapped_column(DateTime, default=utc_time)

    user_orders: Mapped[int] = mapped_column(Integer, ForeignKey("orders.order_id"), ondelete="CASCADE")


class Courier(Base):
    __tablename__ = "couriers"

    # Поля
    courier_id: Mapped[intPK]  # Основной ID пользователя
    courier_tg_id: Mapped[int] = mapped_column(BigInteger)
    courier_name: Mapped[str] = mapped_column(String(100), nullable=True)
    courier_email: Mapped[str] = mapped_column(String(255), nullable=True)
    courier_phone_number: Mapped[str] = mapped_column(String(20), nullable=True)
    courier_registration_date: Mapped[datetime] = mapped_column(DateTime, default=utc_time)

    courier_orders: Mapped[int] = mapped_column(Integer, ForeignKey("orders.order_id"), ondelete="CASCADE")


class Order(Base):
    __tablename__ = "orders"

    order_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING)

    courier_id: Mapped[int] = mapped_column(Integer, ForeignKey("couriers.courier_id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))

    courier = relationship("Courier", back_populates="courier_orders")
    user = relationship("User", back_populates="user_orders")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_time, nullable=True)

    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    execution_time: Mapped[float] = mapped_column(Float, nullable=True)


class Subscription(Base):
    __tablename__ = "subscriptions"

    subscription_id: Mapped[intPK]

    # Поле для типа подписки
    subscription_type: Mapped[SubscriptionType] = mapped_column(Enum(SubscriptionType), nullable=False)

    start_date: Mapped[datetime] = mapped_column(DateTime, default=moscow_time, nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Стоимость подписки
    subscription_cost: Mapped[float] = mapped_column(Float, nullable=False)

    # Связь с пользователем
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id"), nullable=False)

    user = relationship("User", back_populates="subscriptions")


class DailyEvent(Base):
    __tablename__ = "daily_events"

    # Основные поля
    daily_event_id: Mapped[intPK]
    event_date: Mapped[Date] = mapped_column(Date, primary_key=True, default=func.current_date(), nullable=False)
    total_orders: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed_orders: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    canceled_orders: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    new_users: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    new_subscriptions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_order_revenue: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    fastest_order_time: Mapped[float] = mapped_column(Float, nullable=True)  # В секундах или минутах
    total_reviews: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    support_requests: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Поле для дополнительных комментариев или данных
    notes: Mapped[str] = mapped_column(Text, nullable=True)

    def __repr__(self):
        return (f"DailyEvent(date={self.event_date}, total_orders={self.total_orders}, "
                f"completed_orders={self.completed_orders}, total_revenue={self.total_order_revenue})")


# Функция
async def async_main():
    async with engine.begin() as conn:
        # engine.echo = False
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
